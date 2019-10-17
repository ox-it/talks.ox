import os
from datetime import datetime

from fabric.api import *
from fabric.contrib import *
from fabric.contrib.files import exists
from fabric import utils


_private_pypi = os.getenv('PRIVATE_PYPI')
PIP_OPTIONS = '-i %s' % _private_pypi if _private_pypi else ''

"""
Environments
"""

ENVIRONMENTS = ('dev', 'staging', 'production')

@task
def local():
    env.environment = 'dev'
    env.repo = "https://github.com/ox-it/talks.ox.git"
    env.hosts = ['talks.vm']
    env.user = 'talks'
    env.settings_module = 'talks.settings'
    env.remote_install_dir = '/srv/talks/talks.vm'
    env.remote_git_checkout = '/srv/talks/talks.ox'
    env.requirements = ['requirements.txt']
    env.secrets_dir = '/etc/puppet/secrets/talks-dev.oucs.ox.ac.uk'

@task
def virtual():
    env.environment = 'dev'
    env.repo = "https://github.com/ox-it/talks.ox.git"
    env.hosts = ['192.168.33.178']
    env.user = 'talks'
    env.settings_module = 'talks.settings'
    env.remote_install_dir = '/srv/talks/talks-dev.oucs.ox.ac.uk'
    env.remote_git_checkout = '/srv/talks/talks.ox'
    env.requirements = ['requirements.txt']
    env.secrets_dir = '/srv/%s/secrets' % (env.user)

@task
def staging():
    env.environment = 'staging'
    env.repo = "https://github.com/ox-it/talks.ox.git"
    env.hosts = ['talks-dev.oucs.ox.ac.uk']
    env.user = 'talks'
    env.settings_module = 'talks.settings'
    env.remote_install_dir = '/srv/talks/talks-dev.oucs.ox.ac.uk'
    env.remote_git_checkout = '/srv/talks/talks.ox'
    env.requirements = ['requirements.txt']
    env.secrets_dir = '/srv/%s/secrets' % (env.user)

@task
def production():
    env.environment = 'production'
    env.repo = "https://github.com/ox-it/talks.ox.git"
    env.hosts = ['talks-prod.oucs.ox.ac.uk']
    env.user = 'talks'
    env.settings_module = 'talks.settings'
    env.remote_install_dir = '/srv/talks/talks-prod.oucs.ox.ac.uk'
    env.remote_git_checkout = '/srv/talks/talks.ox'
    env.requirements = ['requirements.txt']
    env.secrets_dir = '/srv/%s/secrets' % (env.user)


"""
Methods
"""


@task
def deploy(version):
    if not version:
        utils.abort('You must specify a version (whether branch or tag).')
    require('user', provided_by=ENVIRONMENTS)
    git_hash = git_branch(version)
    versioned_path = '/srv/%s/talks.ox-%s-%s' % (env.user, datetime.now().strftime('%Y%m%d%H%M'), git_hash)
    createvirtualenv(versioned_path)
    with prefix('source %s' % os.path.join(versioned_path, 'bin', 'activate')):
        install_dir = prepare(versioned_path)
        install(install_dir)
    run('rm %s/secrets.py' % install_dir)
    run('ln -s %s/secrets.py %s/secrets.py' % (env.secrets_dir, install_dir))
    run('rm -f %s' % env.remote_install_dir)
    run('ln -s %s %s' % (versioned_path, env.remote_install_dir))
    run('touch %s' % os.path.join(env.remote_install_dir, 'talks', 'wsgi.py'))


def prepare(venv):
    static_dir = os.path.join(venv, 'static')
    install_dir = os.path.join(venv, 'talks')
    run('cp -r %s %s' % (os.path.join(env.remote_git_checkout, 'static'), static_dir))
    run('cp -r %s %s' % (os.path.join(env.remote_git_checkout, 'talks'), install_dir))
    run('cp -r %s %s' % (os.path.join(env.remote_git_checkout, 'manage.py'), venv))
    for req in env.requirements:
        run('pip install -r %s %s' % (os.path.join(env.remote_git_checkout, req), PIP_OPTIONS))
    return install_dir


def install(install_dir):
    with cd(os.path.dirname(install_dir)):
        run('python manage.py makemigrations --settings=%s' % env.settings_module)
        run('python manage.py migrate --settings=%s' % env.settings_module)
        run('python manage.py collectstatic --noinput --settings=%s' % env.settings_module)

@task
def rebuild_index():
    with cd(env.remote_install_dir):
        run('bin/python manage.py rebuild_index')

"""
Private methods
"""


def createvirtualenv(path):
    run('virtualenv --system-site-packages %s' % path)

def git_check_existing_repo():
    """
    Checks that git repo exists, create it if it doesn't
    """
    if not exists(env.remote_git_checkout):
        run('git clone %s %s' % (env.repo, env.remote_git_checkout))


def git_branch(name):
    """
    Do a checkout on a branch
    """
    git_check_existing_repo()
    with cd(env.remote_git_checkout):
        run('git fetch origin')
        run('git checkout origin/%s' % name)
        return run('git rev-parse --short HEAD')

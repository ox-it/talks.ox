from django.shortcuts import render_to_response
from django.contrib.auth import logout


def webauth_logout(request):
    context = {'was_webauth': True}
    logout(request)
    return render_to_response('auth/logged_out.html', context)

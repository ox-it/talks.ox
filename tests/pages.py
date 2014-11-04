import os

from robot.libraries.BuiltIn import BuiltIn

HOST = "http://localhost:8000"
BROWSER = os.environ.get('BROWSER', 'firefox')

def _get_variable_value(variable):
    return BuiltIn().replace_variables('${%s}' % variable)


class Page(object):
    def __init__(self, path):
        self.path = path

    @property
    def url(self):
        return "%s%s" % (_get_variable_value('HOST'), self.path)

    @classmethod
    def of(klass, model_instance):
        if isinstance(model_instance, basestring):
            model_instance = _get_variable_value(model_instance)
        return klass(model_instance.get_absolute_url())


class Element(object):

    def __init__(self, locator):
        self.locator = locator

    def __getitem__(self, index):
        if self.locator.startswith('css='):
            raise NotImplementedError("indexing not supported for css selectors")
        elif self.locator.startswith('//'):
            suffix = '[%s]' % (index + 1)
        return Element(self.locator + suffix)


# pages

add_talk_page = Page('/events/new')
talk_page = Page('/events/id/\d+')


# elements

abstract_field = Element('css=#id_event-description')
title_field = Element('css=#id_event-title')
group_field = Element('css=#id_group')
venue_field = Element('css=#id_event-location_suggest')
button_done = Element('//button[text()="Done"]')
checkbox_in_group_section = Element('css=#id_event-group-enabled')
error_message = Element('//*[contains(@class, "alert-warning")]')
success_message = Element('//*[contains(@class, "alert-success")]')
create_group_button = Element("//a[text()='New event group']")
suggestion_list = Element('css=.js-suggestion')
suggestion_popup = Element('css=.tt-suggestions')
modal_dialog = Element('//*[@id="form-modal"]')
modal_dialog_title = Element('//*[@id="form-modal-label"]')
modal_dialog_submit_button = Element('//*[@id="form-modal"]//input[@type="submit"]')

# dynamic elements

field = lambda label: Element('//*[@id=//label[text()="%s"]/@for]' % label)
modal_dialog_field = lambda label: Element('//*[@id=//*[@id="form-modal"]//label[text()="%s"]/@for]' % label)
suggested_item = lambda label: Element('//a[contains(text(), "%s")][contains(@class, "js-suggestion")]' % label)
suggestion_popup_item = lambda label: Element('//*[contains(., "%s")][@class="tt-suggestion"]' % label)
list_group_item = lambda label: Element('//*[contains(@class, "list-group-item")][contains(text(), "%s")]' % label)

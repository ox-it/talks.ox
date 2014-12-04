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

    @property
    def is_css(self):
        return self.locator.startswith('css=')

    @property
    def is_xpath(self):
        return self.locator.startswith('//')

    def __getitem__(self, index):
        if self.locator.startswith('css='):
            raise NotImplementedError("indexing not supported for css selectors")
        elif self.locator.startswith('//'):
            suffix = '[%s]' % (index + 1)
        return Element(self.locator + suffix)

    def in_(self, other):
        other = _get_variable_value(other)
        assert self.is_css == other.is_css, "Both locators must be of same type"
        if self.is_css:
            return Element(other.locator + " " + self.locator[len('css='):])
        elif self.is_xpath:
            return Element(other.locator + self.locator)  # FIXME might fail for advanced xpath

# pages

add_talk_page = Page('/events/new')
talk_page = Page('/events/id/\d+')
login_page = Page('/admin/login/')

# dynamic pages

edit_talk_page = lambda slug: Page('/events/id/%s/edit' % slug)


# elements

abstract_field = Element('css=#id_event-description')
title_field = Element('css=#id_event-title')
start_field = Element('css=#id_event-start')
end_field = Element('css=#id_event-end')
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
datetimepicker = Element('//div[contains(@class,"datetimepicker ")]')
datetimepicker_current_day = Element('//*[@class="datetimepicker-days"]//*[contains(@class, "active")]')
datetimepicker_current_hour = Element('//*[@class="datetimepicker-hours"]//*[contains(@class, "active")]')
datetimepicker_current_minute = Element('//*[@class="datetimepicker-minutes"]//*[contains(@class, "active")]')
button_login = Element('//input[@type="submit"]')
username_field = Element('css=#id_username')
password_field = Element('css=#id_password')


# dynamic elements

field = lambda label: Element('//*[@id=//label[text()="%s"]/@for]' % label)
modal_dialog_field = lambda label: Element('//*[@id=//*[@id="form-modal"]//label[text()="%s"]/@for]' % label)
suggested_item = lambda label: Element('//a[contains(text(), "%s")][contains(@class, "js-suggestion")]' % label)
suggestion_popup_item = lambda label: Element('//*[contains(., "%s")][@class="tt-suggestion"]' % label)
list_group_item = lambda label: Element('//*[contains(@class, "list-group-item")][contains(text(), "%s")]' % label)

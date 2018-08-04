from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage
User = get_user_model()


def quit_if_possible(browser):
    try: browser.quit()
    except: pass


class AdminSiteTest(FunctionalTest):

    def test_admin_user_can_assign_a_list_to_a_user(self):
        # Edith goes to the home page and starts a list
        # But she forgets to log-in
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Make a cake')
        list_page.wait_for_row_in_list_table('Make a cake', 1)
        list_url = self.browser.current_url
        
        # Edith logs-in and asks site admin to add this list to her account lists
        self.create_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Mike is a site admin, he logs-in into admin site
        User.objects.create_superuser('mike@example.com', 'testpassword')
        mike_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(mike_browser))

        self.browser = mike_browser
        self.browser.get(self.live_server_url + '/admin/')
        self.browser.find_element_by_id('id_username').send_keys('mike@example.com')
        self.browser.find_element_by_id('id_password').send_keys('testpassword')
        self.browser.find_element_by_id('id_password').send_keys(Keys.ENTER)
        
        # Selects Edith's list to change
        list_model_change = self.wait_for(
            lambda: self.browser.find_element_by_css_selector('.model-list .changelink')
        )
        list_model_change.click()
        list_change = self.wait_for(
            lambda: self.browser.find_element_by_link_text('Make a cake')
        )
        list_change.click()

        # Chooses Edith's email in "owner" field drop-down, and submits changes
        select_owner = self.wait_for(
            lambda: Select(self.browser.find_element_by_id('id_owner'))
        )
        select_owner.select_by_visible_text('edith@example.com')
        self.browser.find_element_by_id('list_form').submit()

        # Edith goes to "My lists" page and her list is now there
        self.browser = edith_browser
        MyListsPage(self).go_to_my_lists_page()
        self.browser.find_element_by_link_text('Make a cake').click()
        self.wait_for(lambda: self.assertEqual(self.browser.current_url, list_url))

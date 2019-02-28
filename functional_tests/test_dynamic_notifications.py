from selenium import webdriver

from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage


def quit_if_possible(browser):
    try: browser.quit()
    except: pass


class DynamicNotificationsTest(FunctionalTest):

    def test_can_immediately_see_changes_when_another_user_adds_item_to_list(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))
        
        # Her friend Martha is also hanging out on the lists site
        martha_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(martha_browser))
        self.browser = martha_browser
        self.create_pre_authenticated_session('martha@example.com')
        
        # Edith goes to the home page, starts a list
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item("Edith's item")
        
        # And shares it with Martha
        list_page.share_list_with('martha@example.com')
        
        # Martha adds her own item to the list
        self.browser = martha_browser
        MyListsPage(self).go_to_my_lists_page()
        self.browser.find_element_by_link_text("Edith's item").click()
        list_page2 = ListPage(self).add_list_item("Martha's item")
        
        # On Edith's screen a message appears telling her
        # that an item has been added to the list by another user
        self.browser = edith_browser
        self.wait_for(lambda: self.assertIn(
            'List has been updated by another user',
            self.browser.find_element_by_tag_name('body').text
        ))
        
        # And that item is now on the list
        list_page2.wait_for_row_in_list_table("Martha's item", 2)

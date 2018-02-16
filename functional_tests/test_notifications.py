from selenium import webdriver
from .base import FunctionalTest
from .list_page import ListPage


def quit_if_possible(browser):
    try: browser.quit()
    except: pass

    
class NotificationsTest(FunctionalTest):

    def test_user_notified_when_someone_shares_list_with_them(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))
        
        # Her friend Mary is also hanging out on the lists site
        mary_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(mary_browser))
        self.browser = mary_browser
        self.create_pre_authenticated_session('mary@example.com')
        
        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Ask Mary')
        
        # She shares her list
        list_page.share_list_with('mary@example.com')
        
        # Mary sees notification.
        # It says Edith shared list with her:
        self.browser = mary_browser
        self.browser.get(self.live_server_url)
        notification = self.browser.find_element_by_css_selector('#id_notify_list li')
        self.assertIn('edith@example.com', notification)
        self.assertIn('Ask Mary', notification)

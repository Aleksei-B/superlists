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
        
        # Edith goes to the home page and starts 3 list and shares them
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Recipe 1')
        list_page.share_list_with('mary@example.com')
        
        self.browser.get(self.live_server_url)
        list_page.add_list_item('Recipe 2')
        list_page.share_list_with('mary@example.com')
        
        self.browser.get(self.live_server_url)
        list_page.add_list_item('Recipe 3')
        list_page.share_list_with('mary@example.com')
        
        # Mary notices 'Notifications' button
        self.browser = mary_browser
        self.browser.get(self.live_server_url)
        notify_button = self.browser.find_element_by_id('id_notify_button')
        
        # With a badge telling her she have 3 new notifications
        notify_badge = self.browser.find_element_by_css_selector('#id_notify_button .badge')
        self.assertEqual(notify_badge.text, '3')
        
        # She clicks on it
        notify_button.click()

        # Modal opens and she sees notifications
        self.browser.find_element_by_class_name('modal-open')
        self.assertEqual(
            len(self.browser.find_elements_by_css_selector('#id_notify_list h4')),
            3
        )
        self.assertEqual(
            self.browser.find_elements_by_css_selector('#id_notify_list h4')[1].text,
            'edith@example.com shared a list with you:\nRecipe 2'
        )
        
        # In the corner of each notification there is 'mark as read' link
        # Mary clicks link of recipe 2
        mark_as_read_links = self.browser.find_elements_by_css_selector('#id_notify_list .pull-right')
        self.assertEqual(
            mark_as_read_links[0].text,
            'mark as read'
        )
        mark_as_read_links[1].click()
        
        # 'Mark as read' changes to already read
        self.assertEqual(
           self.browser.find_elements_by_css_selector('#id_notify_list .pull-right')[1].text,
            'already read'
        )
        
        # Mary refreshes the page, recipe 2 notification dissapears
        self.browser.refresh()
        notify_button = self.browser.find_element_by_id('id_notify_button')
        notify_button.click()
        self.browser.find_element_by_class_name('modal-open')

        self.assertEqual(
            len(self.browser.find_elements_by_css_selector('#id_notify_list h4')),
            2
        )
        notifications = [element.text for element in self.browser.find_elements_by_css_selector('#id_notify_list h4')]
        self.assertNotIn(
            'edith@example.com shared a list with you:\nRecipe 2',
            notifications
        )

        # At the bottom of notifications list Mary sees 'mark all as read' link
        mark_all_as_read = self.browser.find_element_by_css_selector('#id_notify_list li:last-child a')
        
        # She clicks it and all notifications become 'alread read'
        mark_all_as_read.click()
        mark_as_read_links = self.browser.find_elements_by_css_selector('#id_notify_list .pull-right')
        for element in mark_as_read_links:
            self.assertEqual(element.text, 'already read')

        # Mary refreshes the page, all notifications and 'mark all as read' dissapear
        self.browser.refresh()
        notify_button = self.browser.find_element_by_id('id_notify_button')
        notify_button.click()
        self.browser.find_element_by_class_name('modal-open')
        
        self.assertEqual(
            len(self.browser.find_elements_by_css_selector('#id_notify_list h4')),
            0
        )
        self.assertEqual(
            self.browser.find_elements_by_css_selector('#id_notify_list li:last-child a'),
            []
        )

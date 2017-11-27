from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage


class MyListsTest(FunctionalTest):
        
    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@example.com')
        
        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('Reticulate splines')
        list_page.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url
        
        # She notices a "My lists" link, for the first time.
        my_lists_page = MyListsPage(self).go_to_my_lists_page()
        
        # She sees that her list is in there, named according to its
        # first list item
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )
        
        # She decides to start another list, just to see
        self.browser.get(self.live_server_url)
        list_page.add_list_item('Click cows')
        second_list_url = self.browser.current_url
        
        # Under "My lists", her new list appears
        my_lists_page.go_to_my_lists_page()
        self.browser.find_element_by_link_text('Click cows').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )
        
        # She logs out. The "My lists" option dissapears
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_elements_by_link_text('My lists'),
            []
        ))

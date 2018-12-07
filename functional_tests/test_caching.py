import time
from .base import FunctionalTest
from .list_page import ListPage

""" Is functional tests the right place? """

class CachingTest(FunctionalTest):

    def test_caching_enabled(self):
        # Mark goes to superlists site and starts a list
        self.browser.get(self.live_server_url)
        ListPage(self).add_list_item('A list item')
        
        # He redirected to list page
        ## Cached template fragment has a timestamp
        source = self.browser.page_source
        start_index = source.find('<!--')
        self.assertNotEqual(start_index, -1)  # check if comment with timestamp exist
        start_index = start_index + len('<!--')
        end_index = source.find('-->')
        old_timestamp = source[start_index : end_index].strip()
        
        # Mark refreshes the page
        time.sleep(1)
        self.browser.refresh()

        ## Timestamp shouldn't change
        source = self.browser.page_source
        start_index = source.find('<!--') + len('<!--')
        end_index = source.find('-->')
        new_timestamp = source[start_index : end_index].strip()
        self.assertEqual(old_timestamp, new_timestamp)

    def test_cache_invalidation(self):
        # Mark goes to superlists site and starts a list
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item('First item')
        
        source = self.browser.page_source
        start_index = source.find('<!--')
        self.assertNotEqual(start_index, -1)  # check if comment with timestamp exist
        start_index = start_index + len('<!--')
        end_index = source.find('-->')
        old_timestamp = source[start_index : end_index].strip()
        
        # He adds another list item
        list_page.add_list_item('Second item')
        
        # And refreshes the page
        time.sleep(1)
        self.browser.refresh()

        ## Timestamp should change
        source = self.browser.page_source
        start_index = source.find('<!--') + len('<!--')
        end_index = source.find('-->')
        new_timestamp = source[start_index : end_index].strip()
        
        self.assertNotEqual(old_timestamp, new_timestamp)

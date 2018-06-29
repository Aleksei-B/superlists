from .base import FunctionalTest


class CustomErrorPagesTest(FunctionalTest):
    
    def test_404_page(self):
        # Edith inputs wrong url by mistake
        self.browser.get(self.live_server_url + '/404_no_such_url/')
        
        # And sees custom 404 error page
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Sorry, but the requested page could not be found.', page_text)
        self.assertIn('Page not found', page_text)

    def test_500_page(self):
        # Edith goes to the site, but something wrong with the server
        # and she sees custom 500 error page
        self.browser.get(self.live_server_url + '/test_500_error/')
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Page unavailable', page_text)
        self.assertIn('Sorry, but something wrong with the server.', page_text)

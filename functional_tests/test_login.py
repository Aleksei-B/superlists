import os
import poplib
import re
import time
from django.core import mail
from django.contrib.auth import get_user_model
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
from lists.models import List
User = get_user_model()


SUBJECT = 'Your login link for Superlists'


class LoginTest(FunctionalTest):

    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body
            
        email_id = None
        start = time.time()
        while time.time() - start < 60:
            try:
                inbox = poplib.POP3_SSL('TEST_POP3_SERVER')
                inbox.user(test_email)
                inbox.pass_(os.environ['TEST_EMAIL_PASSWORD'])
                # get 10 newest messages
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print('getting msg', i)
                    _, lines, __ = inbox.retr(i)
                    lines = [l.decode('utf8') for l in lines]
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        return body
            finally:
                if email_id:
                    inbox.dele(email_id)
                inbox.quit()
            time.sleep(5)

    def test_can_get_email_link_to_log_in(self):
        # Edith goes to the awesome superlists site
        # and notices a "Log in" section in the navbar for the first time
        # It's telling her to enter her email address, so she does
        if self.staging_server:
            test_email = 'TEST_EMAIL'
        else:
            test_email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)
        
        # a message appears telling her an email has been sent
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))
        
        # She checks her email and finds a message
        body = self.wait_for_email(test_email, SUBJECT)
        
        # It has a url link in it
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)
        
        # she clicks it
        self.browser.get(url)
        
        # she is logged in!
        self.wait_to_be_logged_in(email=test_email)
        
        # Now she logs out
        self.browser.find_element_by_link_text('Log out').click()
        
        # She is logged out
        self.wait_to_be_logged_out(email=test_email)
        
    def test_registered_users_lists_are_private(self):
        # Edith is a site user with a list
        owner = User.objects.create_user('edith@example.com')
        list_ = List.objects.create(owner=owner)
        list_url = self.live_server_url + list_.get_absolute_url()
        
        # George is a site user too, he tries to see his list but makes two mistakes
        # He forgets to log-in and inputs wrong(Edith's) list url
        self.browser.get(list_url)
        
        # He redirected to the main page and message appears telling him
        # that he must log-in to see this list
        self.wait_for(lambda: self.assertEqual(
            self.browser.current_url,
            self.live_server_url
        ))
        self.assertIn(
            'You must log-in to see this list',
            self.browser.find_element_by_tag_name('body').text
        )
        
        # George logs-in and tries again
        self.create_pre_authenticated_session('george@example.com')
        self.browser.get(list_url)
        
        # He redirected again with another message:
        # only list owner and users owner shared this list with can see it
        self.wait_for(lambda: self.assertEqual(
            self.browser.current_url,
            sekf.live_server_url
        ))
        self.assertIn(
            'Only list owner and users owner shared this list with can see this list',
            self.browser.find_element_by_tag_name('body').text
        )

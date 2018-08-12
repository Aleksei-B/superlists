import unittest
from unittest.mock import patch, Mock
from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape
from django.contrib.auth import get_user_model
User = get_user_model()
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm,
)
from lists.models import Item, List
from lists.views import new_list, NOT_LOGGED_ERROR, NOT_OWNER_OR_SHAREE_ERROR


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
        
    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)
    

class ListViewTest(TestCase):
    
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')
        
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)
        
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)
        
    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        
        self.assertRedirects(response, f'/lists/{correct_list.id}/')
        
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )
        
    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)
        
    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        
    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        
    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))
        
    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')
    
    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )
        
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)
        
    def test_not_owner_or_not_sharee_cant_access_list_anonymous_redirects_to_home_page(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertRedirects(response, '/')
        
    def test_not_owner_or_not_sharee_cant_access_list_registered_redirects_to_home_page(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        user = User.objects.create_user('user@example.com')
        self.client.force_login(user)
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertRedirects(response, '/')
        
    def test_list_sharee_CAN_access_list(self):
        owner = User.objects.create_user('owner@example.com')
        sharee = User.objects.create_user('sharee@example.com')
        list_ = List.objects.create(owner=owner)
        Item.objects.create(text='text', list=list_)
        list_.shared_with.add(sharee)
        
        self.client.force_login(sharee)
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        
    def test_not_owner_or_not_sharee_cant_access_list_anonymous_nothing_saved_to_db(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        self.client.post(f'/lists/{list_.id}/', data={'text': 'A new item'})
        self.assertEqual(Item.objects.count(), 0)
        
    def test_not_owner_or_not_sharee_cant_access_list_registered_nothing_saved_to_db(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        user = User.objects.create_user('user@example.com')
        self.client.force_login(user)
        self.client.post(f'/lists/{list_.id}/', data={'text': 'A new item'})
        self.assertEqual(Item.objects.count(), 0)
        
    def test_not_owner_or_not_sharee_cant_access_list_anonymous_get_error_message(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        response = self.client.get(f'/lists/{list_.id}/', follow=True)
        
        self.assertEqual(len(response.context['messages']), 1)
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            NOT_LOGGED_ERROR
        )
        self.assertEqual(message.tags, "error")
        
    def test_not_owner_or_not_sharee_cant_access_list_registered_get_error_message(self):
        owner = User.objects.create_user('owner@example.com')
        list_ = List.objects.create(owner=owner)
        
        user = User.objects.create_user('user@example.com')
        self.client.force_login(user)
        response = self.client.get(f'/lists/{list_.id}/', follow=True)
        
        self.assertEqual(len(response.context['messages']), 1)
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            NOT_OWNER_OR_SHAREE_ERROR
        )
        self.assertEqual(message.tags, "error")
    
  
@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()
        
    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)
        
    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)
        
    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
        self, mock_redirect, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        
        response = new_list(self.request)
        
        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)
        
    @patch('lists.views.render')
    def test_render_home_template_with_form_if_form_invalid(
        self, mock_render, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        
        response = new_list(self.request)
        
        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    @patch('lists.views.render')
    def test_does_not_save_if_form_invalid(
        self, mock_render,  mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)
  

class NewListViewIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')
        
    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))
    
    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)
        
        
class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')
        
    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)
        

class ShareListTest(TestCase):

    def test_post_redirects_to_lists_page(self):
        owner = User.objects.create(email='owner@example.com')
        user = User.objects.create(email='fred@example.com')
        list_ = List.objects.create(owner=owner)
        self.client.force_login(owner)
        response = self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee': 'fred@example.com'}
        )
        self.assertRedirects(response, f'/lists/{list_.id}/')
        
    def test_email_user_added_to_shared_with(self):
        owner = User.objects.create(email='john@example.com')
        user = User.objects.create(email='fred@example.com')
        list_ = List.objects.create(owner=owner)
        self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee': 'fred@example.com'}
        )
        self.assertIn(user, list_.shared_with.all())

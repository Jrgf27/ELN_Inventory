# pylint: disable=relative-beyond-top-level
"""Module used for testing of item category urls"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import ItemCategory

class ItemCategoryUrlsTest(TestCase):
    """Class for testing of item category urls"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user1',
            email='user@account.com',
            password='pwd'
        )

    def test_category_list_not_authenticated(self):
        """Testing category list url paths without authentication"""
        path = reverse('CategoryList')
        login_redirection = '/login/?next=' + path
        request1 = self.client.get(path)
        self.assertRedirects(
            request1,
            login_redirection,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

    def test_category_list_authenticated(self):
        """Test category list URL for authenticated user"""
        path = reverse('CategoryList')
        login_result = self.client.login(username='user1', password='pwd')
        self.assertTrue(login_result)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'itemcategory/categoryList.html')

    def test_category_detail_not_authenticated(self):
        """Testing detail category url paths without authentication"""
        path = reverse('specificCategory', kwargs= {'category_id': 1})
        login_redirection = '/login/?next=' + path

        request = self.client.get(path)
        self.assertRedirects(
            request,
            login_redirection,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

        request = self.client.post(path)
        self.assertRedirects(
            request,
            login_redirection,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

    def test_category_detail_authenticated_get(self):
        """Test detail category URL for authenticated user for GET"""
        path = reverse('specificCategory', kwargs= {'category_id': 1})
        path_to_list = reverse('CategoryList')
        login_result = self.client.login(username='user1', password='pwd')
        self.assertTrue(login_result)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

        category = ItemCategory(
            name = 'cat1',
            description = 'description1'
        )
        category.save()
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'itemcategory/specificCategory.html')
        self.assertEqual(response.context['categoryInfo'].name, category.name)
        self.assertEqual(response.context['categoryInfo'].description, category.description)

        category.isEnabled=False
        category.save()
        response = self.client.get(path)
        self.assertRedirects(
            response,
            path_to_list,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

    def test_category_detail_authenticated_post(self):
        """Test detail category URL for authenticated user for GET"""
        path = reverse('specificCategory', kwargs= {'category_id': 1})
        path_to_list = reverse('CategoryList')
        path_to_edit = reverse('editCategory', kwargs= {'category_id': 1})

        login_result = self.client.login(username='user1', password='pwd')
        self.assertTrue(login_result)

        response = self.client.post(path)
        self.assertEqual(response.status_code, 404)

        category = ItemCategory(
            name = 'cat1',
            description = 'description1'
        )
        category.save()
        self.assertTrue(category.isEnabled)

        response = self.client.post(path)
        self.assertRedirects(
            response,
            path_to_list,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

        response = self.client.post(path, data={'edit_category':'True'})
        self.assertRedirects(
            response,
            path_to_edit,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

        response = self.client.post(path, data={'delete_category':'True'})
        self.assertRedirects(
            response,
            path_to_list,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

        category=ItemCategory.objects.get(pk=1)
        self.assertFalse(category.isEnabled)

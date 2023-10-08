# pylint: disable=relative-beyond-top-level
"""Module used for testing of item category urls"""

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse

class ItemCategoryUrlsTest(TestCase):
    """Class for testing of item category urls"""

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username='user1',
            email='user@account.com',
            password='pwd'
        )
        self.path = reverse('CategoryList')

    def test_category_list_not_authenticated(self):
        """Testing category list url paths"""

        login_redirection = '/login/?next=' + self.path
        request1 = self.client.get( self.path)
        self.assertRedirects(
            request1,
            login_redirection,
            status_code=302,
            target_status_code=200,
            msg_prefix='',
            fetch_redirect_response=True)

    def test_category_list_authenticated(self):
        """Test category list URL for authenticated user"""

        login_result = self.client.login(username='user1', password='pwd')
        self.assertTrue(login_result)

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'itemcategory/categoryList.html')

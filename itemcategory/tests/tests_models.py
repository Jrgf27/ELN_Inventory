# pylint: disable=relative-beyond-top-level
"""Module used for testing of item category models"""

from django.test import TestCase
from django.shortcuts import get_list_or_404
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner
from django.contrib.auth.models import User
from ..models import ItemCategory, ItemCategoryVersions
from ..utils import item_category_versioning


class ItemCategoryTests(TestCase):
    """Class for testing of item category model"""

    def test_itemcategory_creation_good(self):
        """Testing for creation of item categories with correct inputs"""

        category1 = ItemCategory(
            name='testName',
            description = 'testDescription',
        )
        category1.save()
        self.assertTrue(isinstance(category1, ItemCategory))
        self.assertEqual(str(category1), str(category1.name))
        self.assertTrue(category1.isEnabled)

        category2 = ItemCategory(
            name='testName2',
            description = 'testDescription2',
        )
        category2.save()
        category_list=get_list_or_404(ItemCategory, isEnabled=True)
        self.assertEqual(len(category_list),2)

        category2.isEnabled=False
        category2.save()
        category_list2=get_list_or_404(ItemCategory, isEnabled=True)
        self.assertEqual(len(category_list2),1)

    def test_itemcategory_creation_bad_name(self):
        """Testing for creation of item categories with improper name inputs"""
        category1=ItemCategory(name=21321, description = 'testDescription')
        self.assertRaises(TypeError, category1.save())
        category3=ItemCategory(name=True, description = 'testDescription')
        self.assertRaises(TypeError, category3.save())
        category5=ItemCategory(name=['2322',3232], description = 'testDescription')
        self.assertRaises(TypeError, category5.save())

    def test_itemcategory_creation_bad_description(self):
        """Testing for creation of item categories with improper description inputs"""
        category6=ItemCategory(name='testName', description = ['2322',3232])
        self.assertRaises(TypeError, category6.save())
        category4=ItemCategory(name='testName', description = False)
        self.assertRaises(TypeError, category4.save())
        category2=ItemCategory(name='testName', description = 123123123)
        self.assertRaises(TypeError, category2.save())

    def test_itemcategory_creation_bad_isenabled(self):
        """Testing for creation of item categories with improper isEnabled field inputs"""
        with self.assertRaises(ValidationError):
            category=ItemCategory(
                name='testName',
                description = 'testDescription',
                isEnabled=1232131)
            category.save()

        with self.assertRaises(ValidationError):
            category=ItemCategory(
                name='testName',
                description = 'testDescription',
                isEnabled='1232131')
            category.save()

        with self.assertRaises(ValidationError):
            category=ItemCategory(
                name='testName',
                description = 'testDescription',
                isEnabled=[1232131])
            category.save()

    def test_itemcategory_versioning(self):
        """Testing for versioning functions following creations, deletion or edit of category"""
        timestamper = TimestampSigner()
        category1 = ItemCategory(
            name='testName',
            description = 'testDescription',
        )
        category1.save()
        user = User.objects.create_user(username='testuser',password='testpwd')
        item_category_versioning(
            action="CREATED",
            item_category_model= category1,
            user = user
        )
        version_model = get_list_or_404(ItemCategoryVersions)[0]
        unsigned_version_sig = timestamper.unsign_object(version_model.lastEditedUserSignature)

        self.assertTrue(isinstance(version_model, ItemCategoryVersions))
        self.assertEqual(str(version_model), str(version_model))
        self.assertEqual(version_model.lastAction, "CREATED")
        self.assertEqual(unsigned_version_sig['ID'], 1)
        self.assertEqual(unsigned_version_sig['Username'], user.username)

        item_category_versioning(
            action="EDITED",
            item_category_model= category1,
            user = user
        )
        versions = get_list_or_404(ItemCategoryVersions)
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[1].lastAction, "EDITED")

        item_category_versioning(
            action="DELETED",
            item_category_model= category1,
            user = user
        )
        versions = get_list_or_404(ItemCategoryVersions)
        self.assertEqual(len(versions), 3)
        self.assertEqual(versions[2].lastAction, "DELETED")
        self.assertEqual(versions[1].lastAction, "EDITED")
        self.assertEqual(versions[0].lastAction, "CREATED")

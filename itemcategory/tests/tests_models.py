# pylint: disable=relative-beyond-top-level
"""Module used for testing of item category models"""

from django.test import TestCase
from django.shortcuts import get_list_or_404
from django.core.exceptions import ValidationError
from ..models import ItemCategory


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

    def test_itemcategory_creation_bad(self):
        """Testing for creation of item categories with improper inputs"""

        category1=ItemCategory(name=21321, description = 'testDescription')
        self.assertRaises(TypeError, category1.save())
        category2=ItemCategory(name='testName', description = 123123123)
        self.assertRaises(TypeError, category2.save())

        category3=ItemCategory(name=True, description = 'testDescription')
        self.assertRaises(TypeError, category3.save())
        category4=ItemCategory(name='testName', description = False)
        self.assertRaises(TypeError, category4.save())

        category5=ItemCategory(name=['2322',3232], description = 'testDescription')
        self.assertRaises(TypeError, category5.save())
        category6=ItemCategory(name='testName', description = ['2322',3232])
        self.assertRaises(TypeError, category6.save())

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

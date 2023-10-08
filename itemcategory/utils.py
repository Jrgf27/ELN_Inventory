# pylint: disable=relative-beyond-top-level
"""Several utility methods used in the item category application"""
from django.utils import timezone
from django.core.signing import TimestampSigner
from .models import ItemCategoryVersions

def item_category_versioning(action = None, item_category_model = None, user=None):
    """Method to be called after any action is performed regarding
    Item categories creation, editing or deletion/disabling;
    Action field can be CREATED, EDITED or DELETED"""
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    item_category_version_model = ItemCategoryVersions(
        itemCategory = item_category_model,
        name = item_category_model.name,
        description= item_category_model.description,
        lastAction = action,
        lastEditedUserSignature = esignature)
    item_category_version_model.save()

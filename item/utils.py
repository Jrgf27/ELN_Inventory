from django.utils import timezone
from django.core.signing import TimestampSigner
from .models import  Items_Versions

def item_versioning(action=None, itemModel=None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID": user.id,
        "Username": user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    itemVersionModel = Items_Versions(item=itemModel,
                                      name=itemModel.name,
                                      description=itemModel.description,
                                      minimumStock=itemModel.minimumStock,
                                      itemCategoryId=itemModel.itemCategoryId,
                                      lastAction=action,
                                      lastEditedUserSignature=esignature)
    itemVersionModel.save()
    
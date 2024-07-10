from django.utils import timezone
from django.core.signing import TimestampSigner
from .models import Equipment_Versions

def equipment_versioning(action = None, equipmentModel = None, user=None):
    timestamper = TimestampSigner()
    esignature = timestamper.sign_object({
        "ID":user.id, 
        "Username":user.username,
        "Email": user.email,
        "FirstName": user.first_name,
        "LastName": user.last_name,
        "TimeOfSignature": str(timezone.now())})
    newversion = Equipment_Versions(
        equipment = equipmentModel,
        name = equipmentModel.name,
        description= equipmentModel.description,
        origin = equipmentModel.origin,
        supportContact = equipmentModel.supportContact,
        responsibleUser= equipmentModel.responsibleUser,
        lastAction = action,
        relatedSOP = equipmentModel.relatedSOP,
        relatedRiskAssessment = equipmentModel.relatedRiskAssessment,
        lastEditedUserSignature = esignature)
    newversion.save()
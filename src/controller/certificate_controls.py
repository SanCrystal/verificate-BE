# for the certificates controller
from src.utils.functions import Model
from src.service.certificate_generator import generate_certificate
from src.service.ipfs import get_certificate_from_ipfs,upload_certificate_to_ipfs
from src.service.template import template
from src.utils.constants import CERTIFICATE_FOLDER_PATH

# create certificates
async def create_certificate(user_id,skill,level):
    """
        Create a certificate
        :param certificate: 
            user_id: user_id of certificate
            skill: skill of certificate
            level: level of certificate
            
        :return: 
            {
            "success":True,
            "message":"certificate created successfully",
            "status":201,
            "certificate":create_certificate object,
            "certificate_url": https://gateway.pinata.cloud/ipfs/Qm......
            } if successful

            {
            "error": f'{error}',
            "success":False,
            "status":500,
            "message":"An error occurred while creating the certificate"
            } if unsuccessful

            {
                "success":False,
                "message":"Certificate already exists",
                "status":409
            } if certificate already exists

            {
                "success":False,
                "message":"User does not exist",
                "status":404
            } if user does not exist
    """
    try:
        # validate that caller is authorized to create a certificate
        # ---- TODO ---- auth user check
        # create certificate

        # check if user exist / registered
        # user = await Model.findone({"_id": user_id}, "users_collection")
        user = {
           "first_name":"John",
            "last_name":"Doe",
            "email":"johndoe@gmail.com",
            "password":"123456789",
            "linked_in":"https://www.linkedin.com/in/johndoe",
            "results":{
                "java":[
                    {
                        "level":"BEGINNER",
                        "test_result":"FAILED",
                        "score":10
                    },
                    {
                        "level":"INTERMEDIATE",
                        "test_result":"PASSED",
                        "score":70
                    },
                    {
                        "level":"ADVANCED",
                        "test_result":"FAILED",
                        "score":40
                    }

                ]
            }
            
        }
        if user is None:
            return {
                "success":False,
                "message":"User does not exist",
                "status":404
                }
        # generate certificate
        full_name = user["last_name"] + " " + user["first_name"]
        # create certifcate name
        certificate_name = f"{full_name}_{level.lower()}_{skill.lower()}_certificate"
        # check if certifcate for that level and skill exist
        certificate_exist = await Model.findone({"certificate_name": certificate_name}, "certificates_collection")
        if certificate_exist is not None:
            return {
                "success":False,
                "message":"Certificate already exists",
                "status":409
            }
        # user model structure should be a hash table with the following keys: category of the test, level,test_result
        if user["results"][skill.lower()]["test_result"] == "PASSED":
            
            certificate =await generate_certificate(full_name,skill,level,template)
            
            # upload certificate to ipfs
            upload_to_ipfs = await upload_certificate_to_ipfs(CERTIFICATE_FOLDER_PATH,certificate[1])
            
            if upload_to_ipfs["success"]:
            # create certificate object

                certificate_object = {
                    "user_id":user_id,
                    "category":skill.upper(),
                    "level":level.upper(),
                    "certificate_name":certificate_name,
                    "certificate_hash":upload_to_ipfs["ipfs_hash"],
                    "certificate_view_url":get_certificate_from_ipfs(upload_to_ipfs["ipfs_hash"]),
                    "issued_by":"Verificate",
                    "date_issued":upload_to_ipfs["time_stamp"]

                }
                # create certificate in database
                create_certificate = await Model.create(certificate_object, "certificates_collection")
           
            # return certificate created
            return {
                "success":True,
                "message":"certificate created successfully",
                "status":201,
                "certificate":create_certificate,
                "certificate_url": create_certificate["certificate_view_url"]
            }
        else:
            return {
                "success":False,
                "message":"User does not have passed the test",
                "status":409
                }
    except Exception as error:
        return {
            "error": f'{error}',
            "success":False,
            "status":500,
            "message":"An error occurred while creating the Certificate"
            }

# get Certificates of a user
async def get_certificates(user_id):
    """
        Get certificates by user_id
        :param user_id: user_id of certificates
        :return: list of certificates
    """
    try:
        # validate that caller is authorized /user
        # ---- TODO ---- auth user check
        # get certificates
        certificates = await Model.findall({"user_id": user_id}, "certificates_collection")
        
        return {
            "certificates":certificates,
            "success":True,
            "message":"certificates retrieved successfully",
            "status":200
            }
    except Exception as error:
        return {
            "error": f'{error}',
            "success":False,
            "status":500,
            "message":"An error occurred while retrieving the certificates"
            }

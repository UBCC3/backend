import json
import logging
import os
import subprocess
import jwt
import boto3

from uuid import UUID


from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import Depends, status, HTTPException, File
from fastapi.security import HTTPBearer

from openbabel import openbabel


dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

def set_up():
    """Sets up configuration for the app"""
    load_dotenv()

    config = {
        "DOMAIN": os.environ.get("AUTH0_DOMAIN"),
        "API_AUDIENCE": os.environ.get("AUTH0_AUDIENCE"),
        "ALGORITHMS": os.environ.get("AUTH0_ALGO"),
    }
    return config


token_auth_schema = HTTPBearer()


def token_auth(token: str = Depends(token_auth_schema)):
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token, permissions=None, scopes=None):
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = set_up()
        # This gets the JWKS from a given URL and does processing so you can use any of
        # the keys available
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": f"PyJWKClientError: {str(error)}"}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": f"DecodeError: {str(error)}"}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer="https://"+self.config["DOMAIN"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if self.scopes:
            result = self._check_claims(payload, "scope", str, self.scopes.split(" "))
            if result.get("error"):
                return result

        if self.permissions:
            result = self._check_claims(payload, "permissions", list, self.permissions)
            if result.get("error"):
                return result

        return payload

    def _check_claims(self, payload, claim_name, claim_type, expected_value):
        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == "scope":
            payload_claim = payload[claim_name].split(" ")

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (
                    f"Insufficient {claim_name} ({value}). You don't have "
                    "access to this resource"
                )
                return result
        return result

def convert_file_to_xyz(input_file_string) -> str:
    obc = openbabel.OBConversion()
    obc.SetInAndOutFormats("pdb","xyz")
    structure = openbabel.OBMol()
    try:
#         obc.ReadString(structure, """HEADER    SMALL MOLECULE
# ATOM      1  C1  ETN     1       0.000   0.000   0.000  1.00  0.00           C
# ATOM      2  C2  ETN     1       1.540   0.000   0.000  1.00  0.00           C
# ATOM      3  O   ETN     1       2.040   1.260   0.000  1.00  0.00           O
# ATOM      4  H1  ETN     1      -0.540   0.900   0.000  1.00  0.00           H
# ATOM      5  H2  ETN     1      -0.540  -0.900   0.000  1.00  0.00           H
# ATOM      6  H3  ETN     1       2.540  -0.900   0.000  1.00  0.00           H
# ATOM      7  H4  ETN     1       1.540   0.540   0.900  1.00  0.00           H
# ATOM      8  H5  ETN     1       1.540   0.540  -0.900  1.00  0.00           H
# ATOM      9  H6  ETN     1       2.040   1.800  -0.900  1.00  0.00           H
# TER
# END
# """)
        # TODO: Fix issue with newlines
        obc.ReadString(structure, input_file_string)
    except Exception as e:
        print(e)
    try:
        output_string = obc.WriteString(structure)
        return output_string
    except Exception as e:
        print(e)

# TODO: use openbabel to convert file type for consistency *.xyz
def upload_to_s3(file: File, structure_id: UUID):
    my_config = Config(
        region_name = os.environ.get("AWS_REGION_NAME"),
    )
    
    s3 = boto3.client("s3")
    
    try:
        response = s3.upload_fileobj(
            # TODO: decide the value of the third parameter (directly upload the file or use a folder)
            file.file, os.environ.get("S3_BUCKET"), str(structure_id) + "/" + file.filename
        )
    except ClientError as e:
        logging.error(e)
        return False
    
def create_presigned_post(object_name, fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file
    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(os.environ.get("S3_BUCKET"),
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response       

# NOTE: route for downloading disabled for now
#       files in s3 should all be in .xyz from the upload fn
def download_from_s3(file_name: str, structure_id: UUID):
    s3 = boto3.client("s3")
    file_key = str(structure_id) + "/" + file_name
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": os.environ.get("S3_BUCKET"), "Key": file_key},
            ExpiresIn=60,  # One minute, should be enough time to download file?
        )
        return response
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=403, detail="Credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NOTE: route for reading file disabled for now
def read_from_s3(file_name: str, structure_id: UUID):
    s3 = boto3.client("s3")
    file_key = structure_id + "/" + file_name
    try:
        response = s3.get_object(Bucket=os.environ.get("S3_BUCKET"), Key=file_key)
        # bytes = response["Body"].read()
        result = json.loads(obj['Body'].read().decode('utf-8'))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def item_to_dict(item):
    return {c.name: getattr(item, c.name) for c in item.__table__.columns}

def cluster_call(action: str, parameters: dict):
    """communicate with the scripts on the compute cluster"""
    command_data = {
        "action": action,
        "parameters": parameters
    }
    json_data = json.dumps(command_data)
    main_exec_path = os.environ.get("CLUSTER_LOC")
    ssh_command = ["ssh", "cluster", "python3", main_exec_path]
    # ssh_command = ["python3", main_exec_path]
    try:
        process = subprocess.Popen(
            ssh_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json_data)
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=stderr)
        return json.loads(stdout)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
import os
import jwt
from dotenv import load_dotenv
from fastapi import Depends, status, HTTPException, File
from fastapi.security import HTTPBearer
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import logging
from uuid import UUID

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

def set_up():
    """Sets up configuration for the app"""
    load_dotenv()

    config = {
        "DOMAIN": os.environ.get("AUTH0_DOMAIN"),
        "API_AUDIENCE": os.environ.get("AUTH0_AUDIENCE"),
        "ISSUER": os.environ.get("AUTH0_ISSUER"),
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
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
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

# NOTE: route for downloading disabled for now
#       files in s3 should all be in .xyz from the upload fn
def download_from_s3(file_name: str, structure_id: UUID):
    s3 = boto3.client("s3")
    file = file_name + '.xyz'
    file_key = str(structure_id) + "/" + file
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": os.environ.get("S3_BUCKET"), "Key": file_key},
            ExpiresIn=60,  # One minute, should be enough time to download file?
        )
        print('respnse', response)
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# NOTE: route for reading file disabled for now
def read_from_s3(file_name: str, structure_id: UUID):
    s3 = boto3.client("s3")
    file_key = structure_id + "/" + file_name
    try:
        response = s3.get_object(Bucket=os.environ.get("S3_BUCKET"), Key=file_key)
        bytes = response["Body"].read()
        # pythonObject = json.loads(obj['Body'].read().decode('utf-8'))
        return bytes
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


def item_to_dict(item):
    return {c.name: getattr(item, c.name) for c in item.__table__.columns}

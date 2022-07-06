from fastapi import HTTPException
import firebase_admin
import firebase_admin.auth
from firebase_admin._auth_utils import UserNotFoundError

app = firebase_admin.initialize_app()

def decode_jwt(jwt):
    try:
        user_data = firebase_admin.auth.verify_id_token(jwt)
    except (
        firebase_admin.auth.InvalidIdTokenError,
        firebase_admin.auth.ExpiredIdTokenError,
        firebase_admin.auth.RevokedIdTokenError,
        firebase_admin.auth.CertificateFetchError
    ) as error:
        raise HTTPException(400, detail='Authorization Error: ' + str(error.cause))
    return user_data

def create_or_get_user_by_email_and_return_firebase_uid(email):
    # returns firebase user id
    try:
        user_record = firebase_admin.auth.get_user_by_email(email)
        return user_record.uid
    except UserNotFoundError:
        user_record = firebase_admin.auth.create_user(email=email)
        return user_record.uid

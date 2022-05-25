from fastapi import HTTPException
import firebase_admin
import firebase_admin.auth

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

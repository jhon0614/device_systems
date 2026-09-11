from fastapi import HTTPException, status

from device_systems.services.user_service import email_exists, get_user_by_id


def get_user_or_404(user_id: int):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


def get_email_validator():
    def validate_email(email: str, ignored_user_id: int = None):
        if email_exists(email, ignored_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya esta registrado",
            )
    return validate_email

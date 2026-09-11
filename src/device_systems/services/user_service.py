from device_systems.data.users_db import users_db


def get_all_users():
    return users_db


def get_user_by_id(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


def email_exists(email: str, ignored_user_id: int = None):
    for user in users_db:
        same_email = user["email"].lower() == email.lower()
        different_user = user["id"] != ignored_user_id
        if same_email and different_user:
            return True
    return False


def create_user(user_data):
    new_id = max([user["id"] for user in users_db], default=0) + 1
    new_user = {"id": new_id, **user_data.model_dump()}
    users_db.append(new_user)
    return new_user


def update_user(user, new_data):
    user.update(new_data)
    return user


def delete_user(user):
    users_db.remove(user)

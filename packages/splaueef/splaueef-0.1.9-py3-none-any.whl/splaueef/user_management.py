# user_management.py
banned_users = set()

def ban_user(user_id: int):
    banned_users.add(user_id)

def unban_user(user_id: int):
    banned_users.discard(user_id)

def is_user_banned(user_id: int):
    return user_id in banned_users

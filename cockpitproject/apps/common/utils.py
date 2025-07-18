import bcrypt


def hash_password(plain_text_password):
    hashed = bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())
    return hashed


def check_password(plain_text_password, hashed_password):
    if bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password):
        return True
    return False

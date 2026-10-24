import hashlib

def generateHashPassword(password: str, salt: bytes):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000).hex()
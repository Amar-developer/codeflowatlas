from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


# Used when an email does not exist, so login still performs password
# verification work before returning the same generic error.
DUMMY_HASH = password_hash.hash("not-a-real-user-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)
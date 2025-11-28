import bcrypt

def hash_password(password: str):
    # Batasi password maksimal 72 bytes (batas bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt dan hash password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        # Batasi password maksimal 72 bytes
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False
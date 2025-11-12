import hashlib
# ---- Password hashing ----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
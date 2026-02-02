from backend.app.core.security import get_password_hash 

password_hash = "test123"
password_hashed = get_password_hash(password_hash)
print ("Hashed password:", password_hashed)

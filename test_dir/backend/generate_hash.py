import sys
import os

# Add current dir to path
# sys.path.append(os.getcwd())

from app.core.security import hash_password

password = "Admin@123"
hashed = hash_password(password)
print(f"PASSWORD: {password}")
print(f"HASH: {hashed}")

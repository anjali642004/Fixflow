import bcrypt

# Generate hash for superadmin password
password = "superadmin123"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f"Password: {password}")
print(f"Hash: {hashed}")

# Test verification
test_password = "superadmin123"
is_valid = bcrypt.checkpw(test_password.encode(), hashed.encode())
print(f"Verification test: {is_valid}") 
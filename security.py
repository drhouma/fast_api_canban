from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


#move to env
SECRET_KEY = "SECRET_KEY"+ "1"*22
algo = "HS256"

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

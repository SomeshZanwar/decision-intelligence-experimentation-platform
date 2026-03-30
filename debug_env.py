from dotenv import load_dotenv
import os

load_dotenv()

print("USER:", os.getenv("DB_USER"))
print("PASS:", os.getenv("DB_PASSWORD"))
print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
print("NAME:", os.getenv("DB_NAME"))
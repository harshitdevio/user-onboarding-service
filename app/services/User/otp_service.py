from app.core.redis import redis_client
import random

OTP_EXPIRY = 300 
OTP_MAX_REQUESTS = 3

# generate OTP
def generate_otp() -> str:
    return str(random.randint(100000, 999999))





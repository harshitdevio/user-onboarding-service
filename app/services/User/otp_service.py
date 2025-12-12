from app.core.redis import redis_client
import random

OTP_EXPIRY = 300 
OTP_MAX_REQUESTS = 3

async def send_otp(phone: str):
    #Check rate limit
    count_key = f"otp_count:{phone}"
    count = await redis_client.incr(count_key)

    if count == 1:
        await redis_client.expire(count_key, OTP_EXPIRY)

    if count > OTP_MAX_REQUESTS:
        raise Exception("Too many OTP requests")

    # Generate and store OTP
    otp = generate_otp()
    otp_key = f"otp:{phone}"
    await redis_client.set(otp_key, otp, ex=OTP_EXPIRY)

    # Send via provider (dummy)
    print(f"SMS to {phone}: {otp}")  # replace with real SMS API

    return True


async def verify_otp(phone: str, user_otp: str):
    otp_key = f"otp:{phone}"
    saved = await redis_client.get(otp_key)

    if not saved:
        return False

    if saved != user_otp:
        return False

    # OTP correct → delete it
    await redis_client.delete(otp_key)

    return True

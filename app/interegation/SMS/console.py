from app.interegation.SMS.base import SMSProvider

#dummy provider
class ConsoleSMSProvider(SMSProvider):
    """Development SMS provider that logs messages to the console."""

    async def send(self, phone: str, message: str) -> None:
        print(f"[SMS] {phone}: {message}")

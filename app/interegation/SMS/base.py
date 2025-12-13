
class SMSProvider:
    """
    Base interface for SMS providers.

    Implementations of this class handle the actual delivery
    of SMS messages via external services.
    """

    async def send(self, phone: str, message: str) -> None:
        """
        Send an SMS message.

        Args:
            phone (str): Destination phone number in E.164 format.
            message (str): Message content.

        Raises:
            SMSDeliveryError: If the message fails to send.
        """
        raise NotImplementedError

from enum import Enum

class OTPPurpose(str, Enum):
    LOGIN = "login"
    SIGNUP = "signup"
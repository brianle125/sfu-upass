import pyotp

def get_mfa(key):
    totp = pyotp.TOTP(key)
    return totp.now()
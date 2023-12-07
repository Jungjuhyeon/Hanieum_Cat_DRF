import hashlib
import hmac
import base64

def make_signature(timestamp):
    access_key = 'NA7oRhD7Qhb7zO7Hes7l'
    secret_key = 'oO34AWPT3rPjyaho8xPvRiugAZpdQo1puErTfgIU'
    
    secret_key = bytes(secret_key, 'UTF-8')

    uri= '/sms/v2/services/ncp:sms:kr:313328416753:han_cat_sms/messages'

    message = "POST" + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey


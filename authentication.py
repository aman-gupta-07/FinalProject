
from twilio.rest import Client
import random
account_sid = 'AC3207c908a23b982eaf9d1cec872e3270'
auth_token = '621d95e11c525fb44f1c74edc7132dd3'
client = Client(account_sid, auth_token)
otp = random.randrange(100000,999999)

message = client.messages.create(
    body='Your OTP for login into result server is '+str(otp),
    from_='+19842039780',
    to='+917080253038'
)

print(message.sid)
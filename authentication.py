
from twilio.rest import Client
import os
import random
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
client = Client(account_sid, auth_token)
otp = random.randrange(100000,999999)

message = client.messages.create(
    body='Your OTP for login into result server is '+str(otp),
    from_='*****',
    to=''****'
)

print(message.sid)

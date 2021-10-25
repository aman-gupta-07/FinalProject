# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from twilio.rest import Client
import random

app = Flask(__name__)


app.secret_key = 'otp'
#
#
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '13020621#Aman'
# app.config['MYSQL_DB'] = 'result'
#

mysql = MySQL(app)


@app.route('/')
def home():
	return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
	number = request.form['number']
	val = getOTPApi(number)
	if val:
		return render_template('OTPAuthentication.html')


@app.route('/validateOTP', methods=['POST'])
def validateOTP():
	otp = request.form['otp']
	if 'response' in session:
		s = session['response']
		session.pop('response',None)
		if s == otp:
			return "You are Authorized, Thank You"
		else:
			return "You are not Authorized, Sorry!!"


def getOTPApi(number):
	account_sid = 'AC3207c908a23b982eaf9d1cec872e3270'
	auth_token = '621d95e11c525fb44f1c74edc7132dd3'
	client = Client(account_sid, auth_token)
	otp = random.randrange(100000, 999999)
	session['response'] = str(otp)

	message = client.messages.create(
		body='Your OTP for login into result server is ' + str(otp),
		from_='+19842039780',
		to='+91'+str(number)

	)
	if message.sid:
		return True
	else:
		return False


if __name__ == "__main__":
	app.run(host ="localhost", debug=True)
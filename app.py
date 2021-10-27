
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail
import MySQLdb.cursors
from twilio.rest import Client
import random
import os
from dotenv import load_dotenv
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')


# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'yourId@gmail.com'
# app.config['MAIL_PASSWORD'] = '*****'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)



# @app.route("/sendEmail", methods=['POST'])
# def sendEmail():
#     msg = Message(
#         'Hello',
#         sender='yourId@gmail.com',
#         recipients=['receiver’sid@gmail.com']
#     )
#     msg.body = 'Hello Flask message sent from Flask-Mail'
#     mail.send(msg)
#     return 'Sent'


app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('checkNumber.html')



@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        msg = None
        number = request.form['number']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT number FROM details WHERE number = %s;" % number)
        data = cursor.fetchall()
        if len(data) > 0:
            msg = "You have successfully verified your registered mobile number."
            session['number'] = number
            return render_template('otpGeneration.html', msg=msg)
        else:
            msg = "This number is not registered here"
            return render_template('checkNumber.html', msg=msg)
    return render_template('checkNumber.html')


@app.route('/getOTP', methods=['POST'])
def getOTP():
    number = request.form['number']
    if 'number' in session:
        msg = None
        s = session['number']
        if s == number:
            session['number']=number

            val = getOTPApi(s)
            if val:
                msg = 'OTP Sent to your registered mobile number'
                return render_template('OTPAuthentication.html', msg=msg)
            else:

                return render_template('otpGeneration.html')
        else:
            msg = 'Enter the registered mobile number only.'
            return render_template('otpGeneration.html', msg=msg)



@app.route('/validateOTP', methods=['POST'])
def login():
    otp = request.form['otp']
    if 'response' in session:
        msg = None
        s = session['response']
        session.pop('response',None)
        if s == otp:
            cursor = mysql.connection.cursor()
            number = session['number']
            cursor.execute("SELECT username FROM details WHERE number = %s;" % number)
            data = cursor.fetchall()
            # type(data)

            msg = "Hello" + " " + str(list(list(data)[0])[0])

            return render_template('user.html', msg=msg)
        else:
            msg = "You are not Authorized, Sorry!!"
            return render_template('otpGeneration.html', msg=msg)




def getOTPApi(number):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
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


@app.route('/studentPage')
def studentPage():
    return render_template('user.html')


@app.route('/result', methods=['GET'])
def result():
    number = session['number']
    session.pop('number', None)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM details WHERE number = %s;" % number)
    data = cursor.fetchall()
    id = list(list(data[0]))[0]
    session['id'] = id
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT stream,score FROM outcome WHERE id = %i;" % id)
    data = cursor.fetchall()
    return str(data)



if __name__ == "__main__":
    app.run(host="localhost", debug=True)

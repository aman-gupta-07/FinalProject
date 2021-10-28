
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import MySQLdb.cursors
from twilio.rest import Client
import random
import os
from dotenv import load_dotenv
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
    # In this method we verify the number entered in Verification page.
    if request.method == 'POST':
        msg = None
        number = request.form['number']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT number FROM details WHERE number = %s;" % number)
        data = cursor.fetchall()
        if len(data) > 0:
            msg = "You entered your registered mobile number,please enter the same mobile number for OTP authentication."
            session['number'] = number
            return render_template('otpGeneration.html', msg=msg)
        else:
            msg = "This number is not registered here"
            return render_template('checkNumber.html', msg=msg)
    return render_template('checkNumber.html')


@app.route('/getOTP', methods=['POST'])
def getOTP():
    # In this method we send the otp to the registered user if entered registered contact number.
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
    # In this method we validate the otp entered by user and direct the user to user's page
    # if the entered otp is correct otherwise direct user back to otpAuthentication.

    otp = request.form['otp']
    if 'response' in session:

        msg = None
        s = session['response']
        session.pop('response', None)
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
    msg = "Your score in the stream you appeared for qualifying in Fynd Academy is : " + str(list(list(data)[0])[:])
    session['msg'] = msg
    return render_template('final.html', msg=msg)


@app.route('/sendEmail', methods=['GET'])
def sendEmail():
    id = session['id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM details WHERE id = %i;" % id)
    data = cursor.fetchall()
    email = list(list(data[0]))[0]
    session.pop('id', None)
    msg1 = Message(
        'Hello',
        sender=os.getenv('MAIL_USERNAME'),
        recipients=[email]
    )
    msg1.body = session['msg']
    session.pop('msg', None)

    mail.send(msg1)
    return 'Email has been sent to your registered email id.'


if __name__ == "__main__":
    app.run(host="localhost", debug=True)

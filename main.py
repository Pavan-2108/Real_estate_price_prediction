import base64
import os
import random
import datetime
import re

import numpy as np
import pandas as pd
from multiprocessing import shared_memory
from flask import Flask, render_template, url_for, redirect, jsonify, Response, abort, session, request, send_file
from werkzeug.utils import secure_filename
import sqlite3
import shutil



from sendmail import sendmail
from predict_price import predict_price

import systemcheck

# pip3 install numpy pandas flask werkzeug


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


conn = sqlite3.connect('data.db')
print ("Opened database successfully")


otp_dict = dict()
cities = ['hyderabad', 'banglore']

apt_types = ["Apartment", "Villa"]

conn.execute('''CREATE TABLE IF NOT EXISTS USERS
         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
         USERNAME           TEXT UNIQUE,
         PASSWORD           TEXT,
         NAME               TEXT,
         EMAIL              TEXT,
         PHONE              TEXT);''')



conn.close()

shape = (480, 640, 3)
app = Flask(__name__)


outputFrame = None
number = random.randint(1000000, 9999999)


def html_return(msg, redirect_to = "/", delay = 5):
    return f"""
                <html>
                    <head>
                        <title>Real Estate Price Prediction </title>
                        <meta http-equiv="refresh" content="{delay};URL='{redirect_to}'" />
                    </head>
                    <body>
                        <h2> {msg}</h2>
                        <p>This page will refresh automatically.</p>
                    </body>
                </html>

                """



@app.route('/signup/' , methods=['get', 'post'])
def signup():
    session.clear()
    if request.method == 'POST':

        username, password, name, contact = request.form['username'], request.form['password'], request.form['name'], request.form['contact']
        print("Got Details", username, password, name, contact)

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(regex,username)):
            print("Valid Email")
            otp_dict[username] = str(random.randint(1000,9999))
            sendmail(f"Your OTP for Signup is {otp_dict[username]} .", username)
            return render_template('signup_otp.html', msg= f"Enter OTP sent to {username}", username=username, password=password, name=name, contact=contact)

        else:
            print("Invalid Email")
            return render_template('signup.html', msg="Enter Correct Mail ID")

    return render_template('signup.html', msg="")



@app.route('/signup_otp/' , methods=['get', 'post'])
def signup_otp():
    print("SIGNUP OTP Function Called")

    if request.method == 'POST':

        otp = request.form['otp']
        username = request.form['username']
        name = request.form['name']
        contact = request.form['contact']
        password = request.form['password']

        print("GOT OTP", otp, username)

        if otp == otp_dict[username]:
            print("OTP Verified Successfully")

            conn = sqlite3.connect('data.db')
            conn.execute(f"DELETE FROM USERS WHERE USERNAME = '{username}'")
            conn.execute(f"INSERT INTO USERS (USERNAME, PASSWORD, NAME, EMAIL, PHONE) VALUES ('{username}', '{password}', '{name}', '{username}', '{contact}' )")
            conn.commit()
            conn.close()

            return html_return("Account Created Successfully.")
        else:
            return render_template('signup_otp.html', msg= f"Wrong OTP. Enter OTP sent to {username}", username=username, password=password, name=name)

    return render_template('signup_otp.html', msg="")


@app.route('/update_password/' , methods=['get', 'post'])
def update_password():
    if 'username' in session.keys():
        print("Update Password Function Called")

        if request.method == 'POST':

            old_password = request.form['old_password']
            new_password = request.form['new_password']

            conn = sqlite3.connect('data.db')
            print ("Opened database successfully 1")
            cursor = conn.execute(f"SELECT USERNAME, PASSWORD, NAME from USERS")
            for row in cursor:
                print(row[0] ,session['username'], row[1] , old_password)
                if  row[0] == session['username']  and row[1] == old_password:
                    print("Updating Passowrd")
                    conn.close()

                    conn = sqlite3.connect('data.db')
                    conn.execute(f"UPDATE USERS SET PASSWORD = '{new_password}' WHERE USERNAME = '{session['username']}' ")
                    conn.commit()
                    conn.close()

                    return html_return("Password Updated Successfully.. Login Using New Password.", redirect_to="/logout")

            return html_return("Enter Old Password Correctly.. ", redirect_to="/update_password")
        else:
            return render_template('update_password.html', user=(session['username'], session['name']))
    else:
            return render_template('login-page.html')



@app.route('/update_mail/' , methods=['get', 'post'])
def update_mail():
    if 'username' in session.keys():
        print("Update Mail Function Called")

        if request.method == 'POST':

            new_mail = request.form['new_mail']

            conn = sqlite3.connect('data.db')
            print ("Opened database successfully 1")
            cursor = conn.execute(f"SELECT USERNAME, PASSWORD, NAME, EMAIL, PHONE from USERS")
            for row in cursor:
                if  row[0] == session['username']:
                    print("Updating Mail")

                    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
                    if(re.search(regex,session['username'])):
                        print("Valid Email")
                        otp_dict[new_mail] = str(random.randint(1000,9999))
                        sendmail(f"Your OTP for Signup is {otp_dict[new_mail]} .", new_mail)
                        conn.close()
                        return render_template('signup_otp.html', msg= f"Enter OTP sent to {new_mail}", username=new_mail, password=row[1], name=row[2], contact=row[4])


                    return html_return("Password Updated Successfully.. Login Using New Password.", redirect_to="/logout")

            return html_return("Enter Old Password Correctly.. ", redirect_to="/update_password")
        else:
            return render_template('update_mail.html', user=(session['username'], session['name']))
    else:
            return render_template('login-page.html')


@app.route('/', methods=['get', 'post'])
def login_page():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if username == "niltech" and password == "Niltech@12345":
            session['username'] = username
            session['city'] = None
            session['locality'] = None
            session['area'] = None
            session['type'] = None
            return render_template('select_location.html', user=(session['username']))
        else:
            try:
                conn = sqlite3.connect('data.db')
                print ("Opened database successfully 1")
                cursor = conn.execute(f"SELECT USERNAME, PASSWORD, NAME from USERS")
                for row in cursor:
                    if  row[0] == username  and row[1] == password:
                        session['name'] = row[2]
                        session['username'] = row[0]
                        session['city'] = None
                        session['locality'] = None
                        session['area'] = None
                        session['type'] = None
                        print("Login Successful")
                        conn.close()
                        return render_template('select_city.html', user=(session['username'] , session['name']))
                else:
                    return render_template('login-page.html')
            except Exception as e:
                print("DB Error 1: ", e)
    elif 'username' in session.keys():
        return render_template('select_city.html', user=(session['username'], session['name']))
    else:
        return render_template('login-page.html')



@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login_page'))



@app.route('/select_city/', methods=['get', 'post'])
def select_city():
    if 'username' in session.keys():
        if request.method == 'POST':

            return redirect(request.url)
        return render_template('select_city.html', user=(session['username'], session['name']))
    else:
        return redirect(url_for('login_page'))



@app.route('/select_locality/', methods=['get', 'post'])
def select_locality():
    if 'username' in session.keys():
        if request.method == 'GET':
            args = request.args
            city = args.get("city")
            session['city'] = city
            session['locality'] = None
            session['area'] = None
            session['type'] = None

            if city.lower() == "banglore":
                localities = ['indra nagar', 'jayanagar']
            elif city.lower() == "hyderabad":
                localities = [ 'dilsukhnagar', 'kukatpally']
            else:
                return redirect(url_for('select_city'))

            return render_template('select_locality.html', user=(session['username'], session['name']), localities = localities)
        return redirect(url_for('select_city'))
    else:
        return redirect(url_for('login_page'))



@app.route('/select_area/', methods=['get', 'post'])
def select_area():
    if 'username' in session.keys():
        if request.method == 'POST':
            locality = request.form['locality']
            session['locality'] = locality
            session['area'] = None
            session['type'] = None

            print("Locality Selected:", locality)

            return render_template('select_area.html', user=(session['username'], session['name']))
    else:
        return redirect(url_for('login_page'))



@app.route('/select_parameters/', methods=['get', 'post'])
def select_parameters():
    if 'username' in session.keys():
        if request.method == 'POST':
            area = request.form['area']
            session['area'] = area
            session['type'] = None

            print("Area Required:", area)


            return render_template('select_parameters.html', user=(session['username'], session['name']), apt_types = apt_types)

        return render_template('select_parameters.html', user=(session['username'], session['name']))
    else:
        return redirect(url_for('login_page'))



@app.route('/result/', methods=['get', 'post'])
def result():
    if 'username' in session.keys():
        if request.method == 'POST':
            apt_type = request.form['apt_type']
            bhk = request.form['bhk']
            distance = request.form['distance']

            session['type'] = apt_type
            session['bhk'] = bhk
            session['distance'] = distance


            print(session['username'])
            print(session['city'])
            print(session['locality'])
            print(session['area'])
            print(session['type'])

            if session['locality'] == "dilsukhnagar":
                locality = 0
            elif session['locality'] == "kukatpally":
                locality = 1
            elif session['locality'] == "indira nagar":
                locality = 2
            elif session['locality'] == "jayanagar":
                locality = 3

            predicted_price = int(predict_price([cities.index(session['city']),locality,int(session['area']),int(session['area']), apt_types.index(session['type']), int(session['bhk']), int(session['distance'])]))

            sendmail(f"Thanks for Using Real Estate Price Prediction.\n\nCity: {session['city']} \nLocality: {session['locality']} \n Type: {session['type']}  \nArea: {session['area']} \nPredicted Price: {predicted_price/1.1} to {predicted_price} Lakhs.", session['username'])


            return render_template('result.html', user=(session['username']), result = f"Thanks for Using Real Estate Price Prediction.\n\nCity: {session['city']} \nLocality: {session['locality']} \n Type: {session['type']}  \nArea: {session['area']} \nPredicted Price: {int(predicted_price/1.1)} to {predicted_price} Lakhs.")
        return render_template('result.html', user=(session['username'], session['name']), result = "Some Random Text")
    else:
        return redirect(url_for('login_page'))



@app.errorhandler(404)
def nice(_):
    return render_template('error_404.html')



app.secret_key = 'q12q3q4e5g5htrh@werwer15454'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 5000, debug = True)#80)
# global outputFrame ## Warning: Unused global

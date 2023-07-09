from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import requests
import os
from openai_files import FitnessGenie
from ml_model import model

import smtplib
from email.mime.text import MIMEText
from mail_config import mail_pass
from bs4 import BeautifulSoup

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


from cam import readb64, get_details, predict

app = Flask(__name__)

results = ""


app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
        msg = "Invalid username or password"
        return render_template('login.html', form=form, msg=msg)
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    try:
        return render_template('login.html', form=form, msg = request.args['msg'])
    except:
        return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login', msg = "New user has been created!"))

        # return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html', name=current_user.username)
    except:
        return redirect(url_for('login'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.before_first_request
def create_tables():
    try:
        db.create_all()
    except:
        print("Database already exists")

@app.route('/res')
@login_required
def res():    
    data = request.args.to_dict()
    # print(data)
    w = float(data['Weight'])
    h = float(data['Height'])
    data['BMI'] = str(w / (h * h / 10000))
    data['Calorie_Deficient_or_Over'] = str(float(data['calories']) - float(data['calories_burnt']) - 2000)
    pred = model.predict(data)
    fitness_plan = FitnessGenie.ai_response(json.dumps(data), str(pred))
    return render_template('res.html', results=pred, plan=fitness_plan, data=data, name=current_user.username
                        #    , billing_info=FitnessGenie.billing_resp()
                           )

from_email = "cloud1project01@gmail.com"
from_password = mail_pass
subject = "Fitness Report from Fitness Genie"


def html_to_plain_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text('\n')


def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Connect to Gmail's SMTP server and send email
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}") 

                 
@app.route('/send_fitness_email', methods=['POST'])
@login_required
def send_fitness_email():
    fitness_plan_html = request.form.get('fitness_plan')
    fitness_plan = html_to_plain_text(fitness_plan_html)
    form_data = request.form.get('form_data')
    
    if fitness_plan and form_data:
        to_email = current_user.email
        email_subject = "Fitness Report from Fitness Genie"
        
        # Include form details in the email body
        email_body = f"Hello {current_user.username},\n\nHere are the details you submitted:\n\n{form_data}\n\nHere is your personalized fitness plan:\n\n{fitness_plan}"
        
        send_email(to_email, email_subject, email_body)
        return jsonify({"success": True, "message": "Email sent successfully!"})
    else:
        return jsonify({"success": False, "message": "Error sending email"})
    
@app.route('/camera')
@login_required
def camera():
    return render_template('camera.html', name=current_user.username)

@login_required
@app.route('/preview', methods=['POST'])
def preview():
    img_data = request.form.get('img-data')
    img = readb64(img_data)
    foodname = predict(img)
    fname = foodname[foodname.rfind("_") + 1:]
    print("Food name:",fname)
    details = get_details(fname)
    print(details)
    try:
        det = details['dishes'][0]
    except:
        det = {
            'caloric' : 'No data available',
            'fat' : 'No data available',
            'carbon' : 'No data available', 
            'protein' : 'No data available'
        }
    return render_template('preview.html', img_data=img, foodname=fname, details=det, name=current_user.username)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=True)
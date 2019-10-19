# Python standard libraries
import json
import os, datetime
import sqlite3
import requests

# Third party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User
from backend import backend, get_preferences

# Configuration
GOOGLE_CLIENT_ID = '208590313636-v7vdem6a4f4ttf4kmeq3vaihvajq4sgh.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'PNgh_8aUQnUQkYe49W-mldd8'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
DB_NAME = 'sqlite_db'
# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

#registering blueprints
app.register_blueprint(backend)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    # return "You must be logged in to access this content.", 403
    # return render_template('login.html')
    return redirect(url_for('index'))

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        logout_user()
        return render_template('login.html')
        # return redirect(url_for('logout'))
    else:
        return render_template('login.html')
        # return "<a href='/login'>login</a>"

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        # redirect_uri="/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in our db with the information provided
    # by Google
    try:
        # Verifying user is from nith or not
        if not (users_email.endswith('@nith.ac.in')):
            return render_template('invalid_email.html')

        else:
            # Finding students Rollno. and branch
            current_year = str(datetime.datetime.now().year)[2:]
            current_month = datetime.datetime.now().month
            student_sem  = 0
            student_year = int(current_year) - int(users_email[:2]) + 1
            if(current_month > 5):
                student_sem = str(2 * student_year - 1)
            else:
                student_sem = str(2 * student_year)
            roll_number = users_email[:users_email.index('@')]
            branch_name = ''
            users_email = str(users_email)
            if('mi5' in users_email):
                branch_name = 'CSE-Dual'
            elif('mi4' in  users_email):
                branch_name = 'ECE-Dual'
            elif(users_email[2] == '3'):
                branch_name = 'Mechanical'
            elif(users_email[2] == '5'):
                branch_name = 'CSE'          
            elif(users_email[2] == '6'):
                branch_name = 'Architecture'
            elif(users_email[2] == '7'):
                branch_name = 'Chemical'
            elif(users_email[2] == '1'):
                branch_name = 'Civil'
            elif(users_email[2] == '4'):
                branch_name = 'ECE'
            elif(users_email[2] == '2'):
                branch_name = 'Electrical'
            elif(users_email[2] == '8'):
                branch_name = 'Material'

            student_cgpi = '9.6'
            user = User(
                id_=unique_id, name=users_name, email=users_email, roll_number=roll_number, branch=branch_name, semester=student_sem, cgpi=student_cgpi
            )
            login_user(user)

            # Doesn't exist? Add to database
            if not User.get(unique_id):
                User.create(unique_id, users_name, users_email, roll_number, branch_name, student_sem, student_cgpi)
            # Begin user session by logging the user in
            return redirect(url_for('home'))
    except:
        render_template('invalid_email.html')

@app.route("/home")
@login_required
def home():
    subject_5th_sem = ['CEO-316: Finite element method', 'EEO-316: Neural Networks and Fuzzy Logic', 'MEO-316: Robotics', 'MEO-316: Modelling and Simulation', 'ECO-316: MEMS and Sensor Design', 'ECO-316: Telecommunication Systems', 'CSO-316: Data Structure', 'CHO-316: Computational Fluid Dynamics', 'MSO-317: Fuel Cells and Hydrogen Energy', 'ARO-317: Auto CAD', 'HUO-316: Indian Buisness Environment', 'HUO-316: Dynamics of Behavioural Science in Industries', 'CMO-316: Catalysis(Principles and Applications)']
    name = current_user.name
    roll_number = current_user.roll_number
    branch = current_user.branch
    semester = current_user.semester
    cgpi = current_user.cgpi
    if(branch.lower() == 'cse-dual'):
        subject_5th_sem.remove('CSO-316: Data Structure')
    elif(branch.lower() == 'cse'):
        subject_5th_sem.remove('CSO-316: Data Structure')
    elif(branch.lower() == 'civil'):
        subject_5th_sem.remove('CEO-316: Finite element method')
    elif(branch.lower() == 'electrical'):
        subject_5th_sem.remove('EEO-316: Neural Networks and Fuzzy Logic')
    elif(branch.lower() == 'mechanical'):
        subject_5th_sem.remove('MEO-316: Robotics')
        subject_5th_sem.remove('MEO-316: Modelling and Simulation')
    elif(branch.lower() == 'ece'):
        subject_5th_sem.remove('ECO-316: MEMS and Sensor Design')
        subject_5th_sem.remove('ECO-316: Telecommunication Systems')
    elif(branch.lower() == 'ece-dual'):
        subject_5th_sem.remove('ECO-316: MEMS and Sensor Design')
        subject_5th_sem.remove('ECO-316: Telecommunication Systems')
    elif(branch.lower() == 'chemical'):
        subject_5th_sem.remove('CHO-316: Computational Fluid Dynamics')
    elif(branch.lower() == 'material'):
        subject_5th_sem.remove('MSO-317: Fuel Cells and Hydrogen Energys')
    elif(branch.lower() == 'architecture'):
        subject_5th_sem.remove('ARO-317: Auto CAD')
    
    # this is the way to get the list of preferences
    # currently showing all subjects
    subject_5th_sem = get_preferences(current_user.roll_number)

    return render_template('student_details.html', roll_number = roll_number, branch = branch, semester = semester, name = name, student_cgpi = '9.6', subjects = subject_5th_sem)

@app.route("/save_details", methods=['POST', 'GET'])
@login_required
def save_details():
    final_list = request.form.getlist('subjects[]')
    print(final_list)
    return redirect(url_for('home'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

if __name__ == "__main__":
    print(app.url_map)
    app.run(ssl_context="adhoc")    

 


    # ni24yc462

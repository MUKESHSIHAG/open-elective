# import google

# Python standard libraries
import json
import os, datetime
import sqlite3
import requests


# Third party libraries
from flask import Flask, redirect, request, url_for, render_template, g
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import psycopg2

def get_db():
    if "db" not in g:
        DATABASE_URL = os.environ['DATABASE_URL']
        g.db = psycopg2.connect(DATABASE_URL,sslmode='prefer')
    return g.db
# Internal imports
# from db import init_db_command
from user import User
from backend import backend, get_preferences, get_cgpi

# Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID',None) 
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET',None)
# from google import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "local-secret"
#  or os.urandom(24)

#registering blueprints
app.register_blueprint(backend)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    print("Unauthorized access, Redirecting to index")
    # return "You must be logged in to access this content.", 403
    # return render_template('login.html')
    return redirect(url_for('index'))

# Naive database setup
# try:
#     init_db_command()
# except Exception as e:
#     print(e)
#     # Assume it's already been created
#     pass
# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.before_request
def enforceHttpsInHeroku():
  if request.headers.get('X-Forwarded-Proto') == 'http':
    url = request.url.replace('http://', 'https://', 1)
    code = 301
    return redirect(url, code=code)

@app.route("/")
def index():
    if current_user.is_authenticated:
        logout_user()
        return render_template('login.html')
        # return redirect(url_for('logout'))
    else:
        return render_template('login.html')
        # return "<a href='/login'>login</a>"

@app.route("/login") #(also checking unicode support)
def login():
    # Find out what URL to hit for Google login
    try:
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
    except (requests.exceptions.ConnectionError):
        return '<html><body><center><h1 style="margin-top:10%">Check Your Network Connection</h1></center</body></html>'

@app.route("/login/callback")
def callback():
    print("Reached at login/callback")
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
            return redirect(url_for('invalid_email'))
        
        elif (users_email.startswith('iiitu')):
            return "Sorry, It's  only for NITians"

        elif not (users_email[:2].isnumeric()):
            return "Don't Try! it's only for Students"

        else:
            print(f"{users_email} is valid.")
            # Finding students Rollno. and branch
            current_year = str(datetime.datetime.now().year)[2:]
            current_month = datetime.datetime.now().month
            student_sem  = None
            student_year = int(current_year) - int(users_email[:2])
            
            if(current_month > 5):
                student_year += 1
                student_sem = str(2 * student_year - 1)
            else:
                student_sem = str(2 * student_year)
            roll_number = users_email[:users_email.index('@')]
            branch_name = ''
            branch_code = ''
            users_email = str(users_email)
            if('mi5' in users_email):
                branch_name = 'CSE-Dual'
                branch_code = 'CS'
            elif('mi4' in  users_email):
                branch_name = 'ECE-Dual'
                branch_code = 'EC'
            elif(users_email[2] == '3'):
                branch_name = 'Mechanical'
                branch_code = 'MC'
            elif(users_email[2] == '5'):
                branch_name = 'CSE'        
                branch_code = 'CS'  
            elif(users_email[2] == '6'):
                branch_name = 'Architecture'
                branch_code = 'AR'
            elif(users_email[2] == '7'):
                branch_name = 'Chemical'
                branch_code = 'CH'
            elif(users_email[2] == '1'):
                branch_name = 'Civil'
                branch_code = 'CE'
            elif(users_email[2] == '4'):
                branch_name = 'ECE'
                branch_code = 'EC'
            elif(users_email[2] == '2'):
                branch_name = 'Electrical'
                branch_code = 'EE'
            elif(users_email[2] == '8'):
                branch_name = 'Material'
                branch_code = 'MS'
            student_cgpi = get_cgpi(roll_number)
            if student_cgpi is None:
                return "CGPI not found"
            user = User(
                id_=unique_id, name=users_name, email=users_email, roll_number=roll_number, branch=branch_name, branch_code=branch_code, semester=student_sem, cgpi=student_cgpi
            )
            login_user(user)

            # Doesn't exist? Add to database
            try:
                if not User.get(unique_id):
                    User.create(unique_id, users_name, users_email, roll_number, branch_name, branch_code, student_sem, student_cgpi)
            except Exception as e:
                print(e)
                return "FFFF"
            print("User login success")
            # Begin user session by logging the user in
            
            if student_year == '1':
                return "You have enough time for open elective choice! Now just focus on your study only :)"
            elif (student_sem == '7' or student_sem == '6'):
                return redirect(url_for('home'))
            # elif(str(roll_number).startswith("17")):
            #     return redirect(url_for('home'))
            else:
                return "Open elective is not for you"
    except:
        redirect(url_for('invalid_email'))

@app.route("/invalid_email")
def invalid_email():
    return render_template('invalid_email.html')

@app.route("/home")
@login_required
def home():
    subjects = get_preferences(current_user.roll_number)
    return render_template('student_details.html', subjects = subjects)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/syllabus")
def syllabus():
    return render_template('syllabus.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.errorhandler(500)
def internal_error(error):
    return "500 error"

if __name__ == "__main__":
    # from db import get_db
    # from backend import do_allotment
    # with app.app_context():
    #     get_db()
    #     do_allotment()
    
    # app.run(ssl_context=('cert.pem','key.pem'))
    app.run(ssl_context='adhoc', debug=0)
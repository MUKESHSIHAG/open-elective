from flask import Blueprint, request, render_template, jsonify, g, redirect, url_for, flash
from flask_login import login_required, current_user

from urllib import request as urlrequest
import json

backend = Blueprint('backend',__name__)

@backend.route("/save_details", methods=['POST'])
@login_required
def save_details():
    roll_number = current_user.roll_number
    final_list = request.form.getlist('subjects[]')
    update_preferences(roll_number,final_list)
    flash('Preferences updated successfully!')
    return redirect(url_for('home'))

def get_preferences(roll_number):
    with g.db as conn:
        cur = conn.execute('''SELECT scode,sname FROM preferences NATURAL JOIN course WHERE roll_number=(?) ORDER BY preference ASC''',(roll_number,))

        result = cur.fetchall()
        return result or get_default_preferences(roll_number)

def get_default_preferences(rollno):
    with g.db as conn:
        cur = conn.execute('''SELECT scode FROM course''')
        result = cur.fetchall()
        result = [i[0] for i in result]
        print(result,'get_default_preferences')
        update_preferences(rollno,result)
    return get_preferences(rollno)

def update_preferences(roll_number,prefs):
    with g.db as conn:
        conn.execute('DELETE FROM preferences WHERE roll_number = (?)',(roll_number,))
        for i,sub_code in enumerate(prefs,start=1):
            try:
                conn.execute('''INSERT INTO preferences VALUES (?,?,?)''',(roll_number,sub_code,i))
            except Exception as e:
                print("Error: ",i,sub_code,e)

def get_cgpi(roll_number):
    api_url = f'https://nithp.herokuapp.com/api/cgpi/{roll_number}'
    req = urlrequest.Request(api_url)
    response = ''
    with urlrequest.urlopen(req) as resp:
        response = resp.read().decode()
    return json.loads(response)
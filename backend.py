from flask import Blueprint, request, render_template, jsonify, g
from flask_login import login_required, current_user

import sqlite3

backend = Blueprint('backend',__name__)

@backend.route("/save_details", methods=['POST'])
@login_required
def save_details():
    roll_number = current_user.roll_number
    
    final_list = request.form.getlist('subjects[]')
    final_list = [sub.split(':')[0] for sub in final_list]

    update_preferences(roll_number,final_list)
    return "Redirect to Home page"

def get_preferences(roll_number):
    with g.db as conn:
        cur = conn.execute('''SELECT scode FROM preferences WHERE roll_number=(?) ORDER BY preference ASC''',(roll_number,))

        result = cur.fetchall()
        result = [i[0] for i in result]
        print(result)
        return result or get_default_preferences(roll_number)

def get_default_preferences(rollno):
    with g.db as conn:
        cur = conn.execute('''SELECT code FROM course''')
        result = cur.fetchall()
        result = [i[0] for i in result]
        print(result,'get_defualt_preferences')
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
        cur = conn.execute('SELECT * FROM preferences')
        result = cur.fetchall()
        return result
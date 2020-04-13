from flask import (
    Blueprint, request, render_template, jsonify, g, redirect, url_for, flash
    )
from flask_login import login_required, current_user

from urllib import request as urlrequest
import json
import os

# local imports
from app import get_db

backend = Blueprint('backend',__name__)

@backend.route("/save_details", methods=['POST'])
@login_required
def save_details():
    roll_number = current_user.roll_number
    final_list = request.form.getlist('subjects[]')
    
    try:
        update_preferences(roll_number,final_list)
        flash('Preferences updated successfully!')
    except Exception as e:
        print(e)
        flash('There was some error')
    
    return redirect(url_for('home'))

def get_preferences(roll_number):
    with g.db as conn:
        cur = conn.cursor()
        cur.execute('''SELECT scode,sname FROM \
            preferences NATURAL JOIN course \
            WHERE roll_number=(%s) ORDER BY preference ASC''',
            (roll_number,))

        result = cur.fetchall()
        # print('here',result)
        return result or create_default_preferences(roll_number)

def create_default_preferences(rollno):
    with g.db as conn:
        cur = conn.cursor()
        cur.execute('''SELECT scode FROM course''')
        prefs = cur.fetchall()
        branch = lambda x: x.startswith(current_user.branch_code)
        prefs = [i[0] for i in prefs if not branch(i[0])]

        for i,sub_code in enumerate(prefs,start=1):
            cur.execute('''INSERT INTO preferences VALUES (%s,%s,%s)''',
            (rollno,sub_code,i))
        # update_preferences(rollno,result)
    return get_preferences(rollno)

def update_preferences(roll_number,prefs):
    with g.db as conn:
        cur = conn.cursor()
        cur.execute('''SELECT scode FROM preferences 
                        WHERE roll_number = (%s)''',
                        (roll_number,))
        subs = cur.fetchall()

        subs = [i[0] for i in subs]

        assert sorted(subs) == sorted(prefs) # To prevent custom POST request
        
        cur.execute('DELETE FROM preferences WHERE roll_number = (%s)',
        (roll_number,))

        for i,sub_code in enumerate(prefs,start=1):
            cur.execute('''INSERT INTO preferences VALUES (%s,%s,%s)''',
            (roll_number,sub_code,i))

            # try:
                # Ideally table should be updated
                # But on update, uniqueness is broken temporarily
                # No way to defer a UNIQUE constraint in sqlite3 is knwown
                # conn.execute('''UPDATE preferences SET scode=(?) \
                # WHERE roll_number=(?) AND preference=(?)''',
                # (sub_code,roll_number,i))

            # except Exception as e:
            #     print("Error: ",i,sub_code,e)
        conn.commit()
def get_cgpi(roll_number):
    import sys
    api_url = f'https://nithp.herokuapp.com/api/result/student/{roll_number}'
    req = urlrequest.Request(api_url)
    response = ''
    try:
        with urlrequest.urlopen(req) as resp:
            response = resp.read().decode()
        
        response = json.loads(response)
        # print(response)
        cgpi = response['cgpi']
    except:
        print("Error in fetching cgpi from nithp.herokuapp.com",file=sys.stderr)
        cgpi = 0
    return json.dumps(cgpi)

@backend.route('/do_allotment')
# @login_required
def do_allotment():
    # Start with highest cgpi
    # allot the lowest preference possible
    get_db() # Why g.db is not available? Due to flask_login?
    MAX_CLASS_SIZE = int(os.getenv('MAX_CLASS_SIZE',1))  # Maximum no. of students in a class
    print("MAX_CLASS_SIZE=",MAX_CLASS_SIZE)
    with g.db as conn:
        cur = conn.cursor()
        cur.execute('''DELETE FROM alloted''')

        cur.execute('''SELECT roll_number,scode,preference,cgpi 
        FROM preferences NATURAL JOIN users ORDER BY cgpi DESC, preference ASC''')
        result = cur.fetchall()

        for roll_number,scode,_,_ in result:
            cur.execute('''SELECT roll_number FROM alloted WHERE roll_number=(%s)''',(roll_number,))
            done = cur.fetchone()

            if not done:
                cur.execute('''SELECT count(*) from alloted where scode=(%s)''',(scode,))
                class_size = cur.fetchone()

                class_size = class_size[0]

                if class_size < MAX_CLASS_SIZE:
                    cur.execute('''INSERT INTO alloted VALUES (%s,%s)''',(roll_number,scode))
        
        cur.execute('''SELECT roll_number,scode,sname FROM alloted NATURAL JOIN course''')
        table = cur.fetchall()
        # table = ((''))
#         table = [
# ('17mi510','PHO-325','NUCLEAR SCIENCE AND ITS APPLICATIONS'),
# ('17mi526','PHO-316','QUANTUM MECHANICS & ITS APPLICATIONS'),
# ('17mi528','MSO-326(b)','FUEL CELL AND HYDROGEN ENERGY'),
# ('17mi527','MSO-326(a)','NANO-MATERIALS & TECHNOLOGY'),
# ('17701','MSO-317','FUEL CELL & HYDROGEN ENERGY'),
# ('17566','MEO-325','MODELLING AND SIMULATION'),
# ('17mi432','MEO-316','QUALITY ENGINEERING'),
# ('17mi532','PHO-325','NUCLEAR SCIENCE AND ITS APPLICATIONS'),
# ('17432','PHO-316','QUANTUM MECHANICS & ITS APPLICATIONS'),
# ('17123','MSO-326(b)','FUEL CELL AND HYDROGEN ENERGY'),
# ('17423','MSO-326(a)','NANO-MATERIALS & TECHNOLOGY'),
# ('17323','MSO-317','FUEL CELL & HYDROGEN ENERGY'),
# ('17683','MEO-325','MODELLING AND SIMULATION'),
# ('17221','MEO-316','QUALITY ENGINEERING')]
        # table = [('17mi432','CEO-312','asdf'),('17MI528','EEO-312(a)','Neural Network')]*30 # for testing purposes only
        return render_template('allotment.html',table=table)

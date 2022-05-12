import logging
import os
import pathlib
from flask import Flask, render_template, redirect, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'industrialtraiingkeydbasmdbjas'
# code for connection
app.config['MYSQL_HOST'] = 'localhost'  # hostname
app.config['MYSQL_USER'] = 'root'  # username
app.config['MYSQL_PASSWORD'] = ''  # password
# in my case password is null so i am keeping empty
app.config['MYSQL_DB'] = 'training'  # database name
# sqlalchemy track modifications in sqlalchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# enable debugging mode
app.config["DEBUG"] = True

mysql = MySQL(app)


@app.route('/')
@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')


@app.route('/studenthome')
@app.route('/studenthome', methods=['POST', 'GET'])
def studenthome():
    result = ''
    # Fetch Data from advisor database using stored procedure
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM advisor')
    # fetching data from MySQL
    resultadvisor = cursor.fetchall()
    mysql.connection.commit()

    name = session['user']
    # Fetch Data from application database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM application WHERE name = %s', (name,))
    # fetching data from MySQL
    result = cursor.fetchone()
    mysql.connection.commit()

    if result:
        return render_template('studenthome.html', status=result['appstatus'], advisor=resultadvisor, result=result)

    return render_template('studenthome.html', status='Not Available', advisor=resultadvisor, result=result)


@app.route('/editapplication', methods=['POST', 'GET'])
def editapplication():
    studentid = request.form.get('editstudentid')
    yourname = request.form.get('edityourname')
    credithours = request.form.get('editcredithours')
    department = request.form.get('editdepartment')
    advisor = request.form.get('editadvisor')
    comments = request.form.get('editcomments')

    name = session['user']
    # Fetch Data from application database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM application WHERE name = %s', (name,))
    mysql.connection.commit()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO application VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (studentid, yourname, credithours, department, advisor, None, comments))
    # fetching data from MySQL
    mysql.connection.commit()
    return redirect('/studenthome')


@app.route('/advisorhome')
@app.route('/', methods=['POST', 'GET'])
def advisorhome():
    advisor = session['user']
    print(advisor)
    # Fetch Data from application database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM application WHERE advisor = %s', (advisor,))
    # fetching data from MySQL
    result = cursor.fetchall()
    mysql.connection.commit()
    return render_template('advisorhome.html', result=result)


@app.route('/approve/<string:student>')
def approve(student):
    # Fetch Data from Airline staff database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE application SET appstatus = %s WHERE studentid = %s', ('Approve', student))
    # fetching data from MySQL
    result = cursor.fetchone()
    mysql.connection.commit()

    return redirect('/advisorhome')


@app.route('/reject/<string:student>')
def reject(student):
    # Fetch Data from Airline staff database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE application SET appstatus = %s WHERE studentid = %s', ('Reject', student))
    # fetching data from MySQL
    result = cursor.fetchone()
    mysql.connection.commit()
    return redirect('/advisorhome')


@app.route('/studentsignin', methods=['POST', 'GET'])
def studentsignin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # stored proc

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE name = %s AND password = %s', (username, password))
        # fetching data from MySQL
        result = cursor.fetchone()
        mysql.connection.commit()

        if result:
            session['user'] = result['name']
            return redirect('/studenthome')

    return render_template('studentsignin.html')


@app.route('/studentsignup', methods=['POST', 'GET'])
def studentsignup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # prepared statment
        cursor.execute('INSERT INTO student VALUES (%s, %s, %s, %s)',
                       (name, email, password, re_password))
        # fetching data from MySQL
        mysql.connection.commit()
        return redirect('/studentsignin')

    return render_template('studentsignup.html')


@app.route('/advisorsignin')
@app.route('/advisorsignin', methods=['POST', 'GET'])
def advisorsignin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch Data from Airline staff database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM advisor WHERE name = %s AND password = %s', (username, password))
        # fetching data from MySQL
        result = cursor.fetchone()
        mysql.connection.commit()

        if result:
            session['user'] = result['name']
            return redirect('/advisorhome')
    return render_template('advisorsignin.html')


@app.route('/advisorsignup')
@app.route('/advisorsignup', methods=['POST', 'GET'])
def advisorsignup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO advisor VALUES (%s, %s, %s, %s)',
                       (name, email, password, re_password))
        # fetching data from MySQL
        mysql.connection.commit()
        return redirect('/advisorsignin')
    return render_template('advisorsignup.html')


@app.route('/submitapplication', methods=['POST', 'GET'])
def submitapplication():
    studentid = request.form.get('studentid')
    yourname = request.form.get('yourname')
    credithours = request.form.get('credithours')
    department = request.form.get('department')
    advisor = request.form.get('advisor')
    comments = request.form.get('comments')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO application VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (studentid, yourname, credithours, department, advisor, None, comments))
    # fetching data from MySQL
    mysql.connection.commit()
    return redirect('/studenthome')


@app.route('/logout')
def logout():
    if 'user' in session:
        app.logger.info('Logged out')
        session.pop('user')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

# create table application (
#     studentid varchar(32),
#     name varchar(32),
#     studentlevel varchar(32),
#     department varchar(32),
#     advisor varchar(32),
#     appstatus varchar(32),
#     comments varchar(32),
#     primary key (name) );

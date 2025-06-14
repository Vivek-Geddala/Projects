from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'Vivek#MyPass' 


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_users_table()  

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            return redirect('/dashboard')
        else:
            flash('Invalid email or password.')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Email already registered. Try logging in.')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return render_template('dashboard.html', email=session['email'])
    else:
        flash('Please log in first.')
        return redirect('/login')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('email', None)  # Logs the user out
    flash('Logged out successfully.')
    return redirect('/login')   # Redirects to login page

# ...existing code...

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' in session:
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE email = ?', (session['email'],))
        conn.commit()
        conn.close()
        session.pop('email', None)
        flash('Your account has been deleted.')
        return redirect('/register')
    else:
        flash('You must be logged in to delete your account.')
        return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

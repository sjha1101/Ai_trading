from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash
import mysql.connector
import re
import datetime
import pandas as pd
import glob
import json
import os
app = Flask(__name__)
app.secret_key = 'dev-please-change-this'  # TODO: change before production

# --- DB CONFIG ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'aitrading'
}

# def get_db_connection():
#     return mysql.connector.connect(**db_config)

#         df['SMA10'] = df['Close'].rolling(window=10).mean()
#         df['SMA30'] = df['Close'].rolling(window=30).mean()
#         df['Signal'] = df.apply(lambda row: 1 if row['SMA10'] > row['SMA30'] else (-1 if row['SMA10'] < row['SMA30'] else 0), axis=1)
#         df['Crossover'] = df['Signal'].diff()
#         df['Action'] = df['Crossover'].apply(lambda x: 'BUY' if x == 2 else ('SELL' if x == -2 else ''))

#         df = df.tail(120)
#         df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

#         chart_data = df[['Date', 'Close', 'SMA10', 'SMA30', 'Action']].dropna().to_dict(orient='records')

#         all_data.append({
#             'symbol': file.replace('.csv', ''),
#             'data': chart_data
#         })

#     return jsonify(all_data)


@app.route('/report')
def report():
# Absolute path to data folder
    data_path = os.path.join(os.getcwd(), 'data')

    # Check if data folder exists and list CSVs
    if os.path.exists(data_path):
        files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
    else:
        files = []

    print("CSV files found:", files)  # Debug log
    return render_template('homepage.html', files=files)

# --- AGE CHECK ---
def is_18_plus(dob_str: str) -> bool:
    if not dob_str:
        return False
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age >= 18

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip()
        phone_number     = request.form.get('phone_number', '').strip()
        date_of_birth    = request.form.get('date_of_birth', '').strip()
        pan_tax_id       = request.form.get('pan_tax_id', '').strip().upper()
        country          = request.form.get('country', '').strip()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('cpassword', '')

        # --- Required ---
        if not username or not email or not password:
            flash("Username, Email, and Password are required!", "danger")
            return redirect(url_for('register'))

        # --- Email ---
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash("Invalid email format!", "danger")
            return redirect(url_for('register'))

        # --- Phone ---
        if not re.match(r'^[6-9]\d{9}$', phone_number):
            flash("Phone number must be 10 digits and start with 6, 7, 8, or 9.", "danger")
            return redirect(url_for('register'))

        # --- Age ---
        if not is_18_plus(date_of_birth):
            flash("You must be at least 18 years old to register.", "danger")
            return redirect(url_for('register'))

        # --- PAN ---
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_tax_id):
            flash("Invalid PAN format (expected: ABCDE1234F).", "danger")
            return redirect(url_for('register'))

        # --- Password match & length ---
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for('register'))

        # --- Hash password ---
        hashed_password = generate_password_hash(password)

        # --- Parse DOB (safe because we validated above) ---
        try:
            dob_sql = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date of birth format.", "danger")
            return redirect(url_for('register'))

        # --- Insert ---
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO users (username, email, phone_number, date_of_birth, pan_tax_id, country, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            vals = (username, email, phone_number, dob_sql, pan_tax_id, country, hashed_password)
            cursor.execute(sql, vals)
            conn.commit()

            print("Insert successful! ID:", cursor.lastrowid)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        except mysql.connector.IntegrityError as e:
            conn.rollback()
            print("IntegrityError:", e)
            flash("Username, Email, or PAN already exists.", "danger")
            return redirect(url_for('register'))

        except Exception as e:
            conn.rollback()
            print("DB ERROR:", e)
            flash(f"Database error: {e}", "danger")
            return redirect(url_for('register'))

        finally:
            cursor.close()
            conn.close()

    # GET request
    return render_template('registration.html')

# --- LOGIN ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/homepage')
        else:
            return "Invalid login. <a href='/'>Try again</a>"

    return render_template('login.html')  

# --- DASHBOARD ---
@app.route('/homepage')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('homepage.html', username=session['username'])

@app.route('/password_reset', methods=['GET', 'POST'])
def reset():
    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('reset'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (generate_password_hash(new_password), session['username']))
        conn.commit()
        cursor.close()
        conn.close()

        session.pop('username', None)
        flash("Password reset successful. Please log in again.", "success")
        return redirect(url_for('login'))

    return render_template('Reset_paasword.html')

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)
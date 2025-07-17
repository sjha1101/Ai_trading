from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash
import mysql.connector
import re
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'aitrading'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        date_of_birth = request.form.get('date_of_birth')
        pan_tax_id = request.form.get('pan_tax_id')
        country = request.form.get('country')
        password = request.form.get('password')
        confirm_password = request.form.get('cpassword')

        # ✅ Required fields check
        if not username or not email or not password:
            flash("Username, Email, and Password are required!", "danger")
            return redirect(url_for('register'))

        # ✅ Password match check
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        # ✅ Email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "danger")
            return redirect(url_for('register'))

        # ✅ Phone number validation (10 digits)
        if not phone_number.isdigit() or len(phone_number) != 10:
            flash("Phone number must be 10 digits!", "danger")
            return redirect(url_for('register'))

        # ✅ Password hashing
        hashed_password = generate_password_hash(password)

        # ✅ Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, phone_number, date_of_birth, pan_tax_id, country, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, email, phone_number, date_of_birth, pan_tax_id, country, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('show_stocks'))
        except mysql.connector.IntegrityError:
            flash("Username or Email already exists.", "danger")
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('registration.html')

@app.route('/homepage')
def show_stocks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stocks ORDER BY price DESC")
    stocks = cursor.fetchall()
    conn.close()
    return render_template('homepage.html', stocks=stocks)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)

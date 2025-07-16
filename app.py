print("Starting Flask app...")

from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for sessions! Use a strong secret key in production.

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',     
    'password': '', 
    'database': 'aitrading'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
@app.route('/stocks')
def show_stocks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stocks ORDER BY price DESC")
    stocks = cursor.fetchall()
    conn.close()
    return render_template('stock.html', stocks=stocks)

if __name__ == '__main__':
    print("Running Flask now...")
    app.run(debug=True)

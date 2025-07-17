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

# @app.route('/')
# def home():
#     if 'username' in session:
#         return redirect('/dashboard')
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM reg WHERE username = %s AND password = %s", (username, password))
#     user = cursor.fetchone()
#     conn.close()

#     if user:
#         session['username'] = username
#         return redirect('/dashboard')
#     else:
#         return "Invalid login. <a href='/'>Try again</a>"

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute("INSERT INTO reg (username, password) VALUES (%s, %s)", (username, password))
#             conn.commit()
#             return redirect('/')
#         except mysql.connector.IntegrityError:
#             return "Username already exists. <a href='/register'>Try again</a>"
#         finally:
#             conn.close()

#     return render_template('register.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'username' not in session:
#         return redirect('/')
#     return render_template('success.html', username=session['username'])

@app.route('/homepage')
def show_stocks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary=True gives column names
    cursor.execute("SELECT * FROM stocks ORDER BY price DESC")
    stocks = cursor.fetchall()
    conn.close()
    # return render_template('stocks.html', stocks=stocks)
    return render_template('homepage.html', stocks=stocks)

@app.route('/logout')
def logout():
    
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

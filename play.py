from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import stripe
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['STRIPE_PUBLIC_KEY'] = 'YOUR_STRIPE_PUBLIC_KEY'
app.config['STRIPE_SECRET_KEY'] = 'YOUR_STRIPE_SECRET_KEY'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

def init_db():
    conn = sqlite3.connect('user.db')
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()
    cursor3 = conn.cursor()
    cursor4 = conn.cursor()

    cursor1.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor2.execute('''
        CREATE TABLE IF NOT EXISTS monthly_subscriptions (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            product_quality TEXT,
            product_rag TEXT,
            product_device TEXT,
            price_id TEXT,
            price_amount INTEGER,
            subscription_type TEXT
        )
    ''')
    cursor3.execute('''
        CREATE TABLE IF NOT EXISTS yearly_subscriptions (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            product_name TEXT,
            product_quality TEXT,
            product_rag TEXT,
            product_device TEXT,
            price_id TEXT,
            price_amount INTEGER,
            subscription_type TEXT
        )
    ''')
    cursor4.execute('''
        CREATE TABLE IF NOT EXISTS users_subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            product_name TEXT,
            price_id TEXT,
            subscription_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_authenticated():
    return 'email' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

# url domain
@app.route('/', methods=['GET', 'POST'])
def index():
    if is_authenticated():
        return render_template('index_login.html')
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == password:
            session['name'] = user[0]
            session['email'] = user[1]
            # print("Fetched Name:", user[0])
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    name = session.get('name', 'Default Value')
    email = session.get('email', 'Default Value')
    subs = True

    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_subscription WHERE email = ? AND name = ?', (email, name,))
    user = cursor.fetchone()
    if user is None:
        subs = False
        monthly_database = []
        cursor1 = conn.cursor()
        cursor1.execute('SELECT * FROM monthly_subscriptions')
        monthly_rows = cursor1.fetchall()
        for row in monthly_rows:
            plan = {
                'product_id': row[1],
                'product_name': row[2],
                'product_quality': row[3],
                'product_rag': row[4],
                'product_device': row[5],
                'price_id': row[6],
                'price_amount': row[7],
                'subscription_type': row[8]
            }
            monthly_database.append(plan)
        
        yearly_database = []
        cursor2 = conn.cursor()
        cursor2.execute('SELECT * FROM yearly_subscriptions')
        yearly_rows = cursor2.fetchall()
        for row in yearly_rows:
            plan = {
                'product_id': row[1],
                'product_name': row[2],
                'product_quality': row[3],
                'product_rag': row[4],
                'product_device': row[5],
                'price_id': row[6],
                'price_amount': row[7],
                'subscription_type': row[8]
            }
            yearly_database.append(plan)
        cursor.close()

        return render_template('checkout.html', email=email, name=name, subs=subs, monthly_database=monthly_database, yearly_database=yearly_database)
    if user:
        product_name = user[3]
        subscription_type = user[5]
    return render_template('checkout.html', name=name, email=email, subs=subs, product_name=product_name, subscription_type=subscription_type, app=app.config['STRIPE_SECRET_KEY'])

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()

        session['name'] = name
        session['email'] = email
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    plan_id = request.form.get('plan_id')  # Get plan_id from form
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': plan_id,
            'quantity': 1,
        }],
        mode='subscription',  # Use 'subscription' for recurring payments
        success_url=url_for('success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('cancel', _external=True),
    )
    # return jsonify({'id': session.id})
    return render_template('confirmation.html', session_id=session.id)

@app.route('/success')
@login_required
def success():
    return render_template('success.html')

@app.route('/cancel')
@login_required
def cancel():
    return render_template('cancel.html')

# Your Flask app code
@app.route('/checkout/<session_id>', methods=['GET'])
@login_required
def checkout(session_id):
    return render_template('confirmation.html', session_id=session_id)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
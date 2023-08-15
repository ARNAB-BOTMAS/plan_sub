from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import stripe
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Replace with your Stripe secret key
stripe.api_key = 'sk_test_51Nf1FtSE3pf7X1MUw59X8fewN1ZPnydPybisfVVzbkhZx5tPJKGlGDn7zcnOWROjTTSn4qxcEdsa6pEDfHSSnMFt002nAMKENf'

# Product prices based on product IDs and intervals (monthly/yearly)
product_prices = {
    'product_basic_id': {'monthly': 10000, 'yearly': 100000},
    'product_standard_id': {'monthly': 20000, 'yearly': 200000},
    'product_premium_id': {'monthly': 50000, 'yearly': 500000},
    'product_regular_id': {'monthly': 70000, 'yearly': 700000},
}

# SQLite Database Initialization
def init_db():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def is_authenticated():
    return 'email' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/payment', methods=['POST'])
def payment():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'confirm':
            session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'YOUR_PRODUCT_PRICE_ID',
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('index', _external=True),
            )
            return {
                'checkout_session_id': session['id'], 
                'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
            }
        elif action == 'cancel':
            return redirect('/dashboard')
    
    return redirect('/')

@app.route('/complete-payment', methods=['POST'])
def complete_payment():
    data = request.json
    payment_method_id = data['paymentMethodId']
    product_id = data['product_id']
    interval = data['interval']
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=product_prices[product_id][interval],
            currency='inr',
            payment_method=payment_method_id,
            confirmation_method='manual',
            confirm=True,
        )
        if payment_intent.status == 'succeeded':
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and user[1] == password:
            session['email'] = user[0]
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('checkout.html', email=session['email'])

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

        session['email'] = email
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/comfirm', methods=['GET', 'POST'])
def comfirm():
    if request.method == 'POST':
        selected_product = request.form['product']
        selected_interval = request.form['interval']
        selected_price = product_prices[selected_product][selected_interval] / 100
        return render_template('confirmation.html', product=selected_product, price=selected_price, interval=selected_interval)
    
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)

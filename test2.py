from flask import Flask, request, redirect, url_for

app = Flask(__name__)

@app.route('/route1')
def route1():
    name = 'John'  # Replace with actual value
    email = 'john@example.com'  # Replace with actual value
    return redirect(url_for('dashboard', name=name, email=email))

@app.route('/dashboard')
def dashboard():
    name = request.args.get('name', 'Default Value')
    email = request.args.get('email', 'Default Value')
    return f"Name: {name}, Email: {email}"

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, session, render_template, request, redirect, current_app, jsonify,json
from flask_pymongo import PyMongo
import bcrypt
from src.controllers.admin import admincontrol
from src.controllers.user import usercontrol

app = Flask(__name__)
app.config["SECRET_KEY"] = "5ecd0a5e51f898b687b5a7db92d3b192" 
app.config["MONGO_URI"] = "mongodb+srv://nihal:nihal320@nihal.q2vawjx.mongodb.net/velocity_ventures"
mongo = PyMongo(app)

app.register_blueprint(admincontrol,url_prefix="/admin")
app.register_blueprint(usercontrol, url_prefix="/user")

@app.route('/')
def index():
    login_message = session.get('login_message')
    registration_message = session.get('registration_message')
    return render_template("index.html", login_message=login_message, registration_message=registration_message)


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    nid = request.form['nid']
    mobile_number = request.form['mobile_number']
    address = request.form['address']
    gender = request.form['gender']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the user already exists in the database
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        session['registration_message'] = "User with this email already exists"
        return redirect('/')

    # Check if the passwords match
    if password != confirm_password:
        session['registration_message'] = "Passwords do not match"
        return redirect('/')

    # Hash the password before storing in the database
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert the user data into the database
    user_data = {
        "name": name,
        "email": email,
        "nid": nid,
        "mobile_number": mobile_number,
        "address": address,
        "gender": gender,
        "password": hashed_password
    }
    mongo.db.users.insert_one(user_data)

    session['registration_message'] = "Registration successful"
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Check if the user exists in the database
    user = mongo.db.users.find_one({"email": email})
    if not user:
        session['login_message'] = "User not found"
        return redirect('/')
    if email == "admin@gmail.com" and password == "admin":
        return redirect('/admin/admin_dashboard')
    # Verify the password
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['email'] = user['email']
        return redirect('/user/')
    else:
        session['login_message'] = "Incorrect password"
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=50001)
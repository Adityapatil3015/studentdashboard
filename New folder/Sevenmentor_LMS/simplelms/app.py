from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'


# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/aditya')
db = client["login"]
users_collection = db["users"]

# Course
courses_collection = db["courses"]


# Sample user data
user_data_list = [
    {
        "username": "rushikesh123",
        "password": bcrypt.hashpw("kavya".encode('utf-8'), bcrypt.gensalt()),
        "email":"rushikesh123@gmail.com",
        "enrolled_courses":["course-id-1","course-id-2"],
        "subscription_start_date": datetime(2023, 10, 22),  # Manual start date
    
    },
    
    {
        "username": "nisheshgogia",
        "password": bcrypt.hashpw("NG123".encode('utf-8'), bcrypt.gensalt()),
        "email":"nisheshgogia@gmail.com",
        "enrolled_courses":["course-id-1","course-id-2","course-id-3","course-id-4"]
    },
    {
        "username": "parth",
        "password": bcrypt.hashpw("PV123".encode('utf-8'), bcrypt.gensalt()),
        "email":"parthvitekar@gmail.com",
        "enrolled_courses":["course-id-1","course-id-4","course-id-5"]
    },
     {
        "username": "aditya",
        "password": bcrypt.hashpw("AP123".encode('utf-8'), bcrypt.gensalt()),
        "email":"adityapatil9173@gmail.com",
        "enrolled_courses":["course-id-1","course-id-2"]
    },
    {
        "username": "saloni",
        "password": bcrypt.hashpw("ST123".encode('utf-8'), bcrypt.gensalt()),
        "email":"salonithete@gmail.com",
        "enrolled_courses":["course-id-1","course-id-5"]
    },
     {
        "username": "neha",
        "password": bcrypt.hashpw("NT123".encode('utf-8'), bcrypt.gensalt()),
        "email":"nehathorat@gmail.com",
        "enrolled_courses":["course-id-1","course-id-2","course-id-5"]
    },
     {
        "username": "arti",
        "password": bcrypt.hashpw("AR123".encode('utf-8'), bcrypt.gensalt()),
        "email":"artirahulkar@gmail.com",
        "enrolled_courses":["course-id-1","course-id-5","course-id-2"]
    },
     {
        "username": "nisha",
        "password": bcrypt.hashpw("NI123".encode('utf-8'), bcrypt.gensalt()),
        "email":"nisha123@gmail.com",
        "enrolled_courses":["course-id-5","course-id-4"]
    }
]

#course data


#Sample course data with course IDs and names
sample_course_data = [
    {
        "_id": "course-id-1",
        "name": "Python",
        "drive_link": "https://drive.google.com/drive/folders/10pr-ZPXNkTNuNctgd5v1GfODB3QlOG6h?usp=drive_link",
        "image": " {{url_for('static', filename='images/pythonLogo.jpeg')}} "
    },
    {
        "_id": "course-id-2",
        "name": "SQL",
        "drive_link": "https://drive.google.com/drive/folders/20pr-ZPXNkTNuNctgd5v1GfODB3QlOG6h?usp=drive_link",
        "image": "{{ url_for('static', filename='images/sql.png') }}"
    },
    {
        "_id": "course-id-3",
        "name": "Probability and Statistics",
        "drive_link": "https://drive.google.com/drive/folders/30pr-ZPXNkTNuNctgd5v1GfODB3QlOG6h?usp=drive_link",
        "image": "{{ url_for('static', filename='images/probStat.png') }}"
    },
    {
        "_id": "course-id-4",
        "name": "Machine Learning",
        "drive_link": "https://drive.google.com/drive/folders/40pr-ZPXNkTNuNctgd5v1GfODB3QlOG6h?usp=drive_link",
        "image": "{{ url_for('static', filename='images/ds.png') }}"
    },
    {
        "_id": "course-id-5",
        "name": "Artificial Intelligence",
        "drive_link": "https://drive.google.com/drive/folders/50pr-ZPXNkTNuNctgd5v1GfODB3QlOG6h?usp=drive_link",
        "image": "{{ url_for('static', filename='images/pro1.jpg') }}"
    }
]



# Insert user data into the "users" collection

for user_data in user_data_list:
    if users_collection.count_documents({"username" : user_data["username"]}) == 0:
        user_data["subscription_valid_until"] = user_data["subscription_start_date"] + timedelta(days=365)
        users_collection.insert_one(user_data)

print(f"{len(user_data_list)} user records inserted into the MongoDB database.")

# Insert user data into the "course" collection

for course_data in sample_course_data:
    if courses_collection.count_documents({"_id": course_data["_id"]}) == 0:
        courses_collection.insert_one(course_data)

print(f"{len(sample_course_data)} user records inserted into the courses database.")

@app.route('/')
def index():
    return render_template('login.html', sample_course_data=sample_course_data)

@app.route('/login', methods=['POST'])
def login():
    raw_username = request.form['username']
    password = request.form['password']
    
    username = raw_username.lower()

    user = users_collection.find_one({'username': username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        # Check if subscription is still valid
        if 'subscription_valid_until' in user and datetime.now() < user['subscription_valid_until']:
            session['username'] = username
            return redirect(url_for('lms'))
        else:
            error_message = "Subscription has expired. Please renew your subscription."
            return render_template('login.html', error_message=error_message)
    else:
        error_message = "Invalid login credentials. Please try again."
        return render_template('login.html', error_message=error_message)


@app.route('/lms')
def lms():
    if 'username' in session:
        username = session['username']
        
        # Fetch the user's enrolled courses from the database
        user = users_collection.find_one({'username': username})
        enrolled_courses = user.get('enrolled_courses', [])
        
        # Fetch course details based on course IDs
        user_courses = courses_collection.find({"_id": {"$in": enrolled_courses}})
        
        return render_template('lms.html', username=username, user_courses=user_courses)
    else:
        return redirect(url_for('index'))


    
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the 'username' from the session
    return redirect(url_for('index'))  # Redirect to the login page


if __name__ == '__main__':
    app.run(debug=True)

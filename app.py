from flask import Flask, render_template,request,session,redirect,flash,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import  datetime
import json
from chat import get_response
local_server = True
with open("templates/config.json","r") as c:
    params = json.load(c)['params']
app = Flask(__name__)
app.secret_key = 'ghaurabin'
if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db = SQLAlchemy(app)

#
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=False, nullable=False)
    msz = db.Column(db.String(50), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    email = db.Column(db.String(20), unique=False, nullable=False)

#creating newsfeed class for db table named newsfeed

class Newsfeed(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=False, nullable=False)
    slug = db.Column(db.String(30), unique=False, nullable=False)
    content = db.Column(db.String(120), unique=False, nullable=True)
    date = db.Column(db.String(20), unique=False, nullable=False)
    img_file = db.Column(db.String(30), unique=False, nullable=False)
    href = db.Column(db.String(30), unique=False, nullable=False)

# creating registered user class

class Registered(db.Model):
    username = db.Column(db.String(40), unique=True, nullable=False,primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=True)
    date = db.Column(db.String(20), unique=False, nullable=False)


#  chatbot conversation
class ChatbotConversation(db.Model):
    id = db.Column(db.String(40), unique=True, nullable=False,primary_key=True)
    userinput = db.Column(db.String(255), nullable=False)
    botresponse = db.Column(db.String(255), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(20), unique=False, nullable=False)

#
@app.route("/")
def firstpage():

    return render_template('home.html',params=params)
@app.route("/home")
def index_get():
    return render_template("base.html",params=params)

@app.route("/predict", methods=["GET","POST"])
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}

    if "user" in session:
        user_email = session["user"]
        conversation_entry = ChatbotConversation.query.filter_by(id=user_email).first()

        if conversation_entry:
            conversation_entry.userinput += "\n" + text  # Append the new user input
            conversation_entry.botresponse += "\n" + response  # Append the new bot response
            conversation_entry.timestamp = datetime.now()
        else:
            conversation_entry = ChatbotConversation(
                id=user_email,
                userinput=text,
                botresponse=response,
                tag="",  # Set the appropriate tag if applicable
                timestamp=datetime.now(),
            )

        db.session.add(conversation_entry)
        db.session.commit()

    return jsonify(message)


@app.route("/signup",methods = ['GET','POST'])
def signup():
    if(request.method == 'POST'):
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')
        if(password != confirm_password):
            flash("Your password don't match.Try Again!",category='error')
            return render_template('signup.html')
        elif(password==confirm_password and username!=''):
            user = Registered.query.filter_by(username=username).first()
            if not user:
                # the email doesnt exist
                flash("Congrats! You are in ! Your account has been created. ", category='success')
                entry = Registered(username=username, name=name, password=password, date=datetime.now())
                db.session.add(entry)
                db.session.commit()
                return render_template('signin.html', params=params)
            else:
                # the email exists
                flash("The email/username is already exist ! Try with another username/email", category='error')
                return render_template('signup.html')


        else:
            flash("Congrats! You are in ! Your account has been created. ", category='success')
            return render_template('signin.html', params=params)
    return render_template('signup.html',params=params)


@app.route('/signin', methods=['GET','POST'])
def get_password():
    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("pass")

        user = Registered.query.filter_by(username=username).first()
        if user:
            if(user.password == password):
                session['user'] = username
                return render_template('base.html')
            else:
                flash("Sorry! Your password is not correct !Try Again", category='error')
                return render_template('signin.html')
        else:
            flash("Sorry! Your username/password not exist.Try again",category='error')
            return render_template('signin.html')
    return render_template('signin.html')


@app.route("/logout")
def logout():
    session.pop('user')
    # return render_template('home.html')
    return redirect('/')

@app.route("/main")
def main():
    # posts = Newsfeed.query.filter_by().all()[0:params['no_of_blogs']]
    return render_template('main.html',params=params)


@app.route('/newsfeed',methods=['GET'])
def newsfeed():
    posts = Newsfeed.query.filter_by().all()[0:params['no_of_blogs']]
    return render_template('newsfeed.html',params=params,newsfeed=newsfeed,posts=posts)
@app.route('/profile')
def profile():
    return render_template('profile.html',params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if ( request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name,email=email,phone_num=phone,date= datetime.now(), msz = message)
        db.session.add(entry)
        db.session.commit()
        '''Fetch data and add it to the database'''
    return render_template('contact.html',params=params)


if __name__ == '__main__':
    app.run(debug=True)

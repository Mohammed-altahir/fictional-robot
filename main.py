from flask import Flask, request, render_template, redirect ,url_for, flash
from flask_cors import CORS
from model import db, User
from core import telegram as ts
import core.wordpress as wp
import random


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config['SECRET_KEY'] = 'secret-key-goes'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
    return app

app = create_app()
@app.before_request
def create_tables():
    db.create_all()

async def send(client,phone):
    phone_hash = await client.send_code_request(phone)
    user = User.query.filter().first()
    user.wp_app_password = phone_hash.phone_code_hash
    db.session.commit()
    return client

async def signIn(client,phone,code):
     user = User.query.filter().first()
     await client.sign_in(phone=phone, code=code,phone_code_hash=user.wp_app_password)
     return client

def __handle_no_users():
    flash("There is no any user registerd on this app.\nTherefore the app generated a dummy user data goto settings to fill in your credentials")
    user = User(username=str(random.randint(0,99999)),api_id=123456,api_hash='hash',phone=str(random.randint(1000000000,9999999999)),wp_user='root',wp_app_password='password',wp_website='mywordpress.org')
    db.session.add(user)
    db.session.commit()
    return redirect('/')

async def connect_telegram(user):
    authenticated, client = await ts.init(user.api_id,user.api_hash,user.phone)
    return authenticated, client


async def get_messages(authenticated,client,user):
    if not authenticated:
        flash('you are not logged into your telegram account')
        await send(client,user.phone)
        client.disconnect()
        client.close()
        return redirect(url_for('login'))
    messages = await ts.main(client)
    return messages


@app.route('/',methods=["GET","POST"])
async def home():
    try:
        user = User.query.filter().first()
        if request.method == "GET":
            return render_template('index.html')
        elif request.method == "POST":
            auth, client = await connect_telegram(user)
            messages = await get_messages(auth,client,user)
            flash('messages were extracted successfully')
            user.t_client = messages
            db.session.commit()
        return redirect('/wp')
    # except AttributeError:
    #     __handle_no_users()
    #     return redirect("/")
    except ConnectionRefusedError:
        flash("Connection failed to telegram server")
        return redirect('/')

@app.route('/wp', methods=['GET','POST'])
async def wordp():
    user = User.query.filter().first()
    if request.method == "GET":
        return render_template('wp.html')
    elif request.method == "POST":
        messages = user.t_client
        wp.createPost(messages)
        flash('your post was created successfully')
        return redirect('/')

@app.route('/login' ,methods=["GET","POST"])
async def login():
    user = User.query.filter().first()
    authenticated, client = await ts.init(user.api_id,user.api_hash,user.phone)
    if request.method == "GET":
        return render_template('signIn.html')
    elif request.method == "POST":
        code = request.form.get('code')
        await signIn(client,user.phone,code)
        client.disconnect()
        client.close()
        flash('signed in successfuly')
        return redirect('/')

@app.route('/test')
def test():
    return '<script>alert("this is a test")</script>'
@app.route('/settings',methods=["GET","POST"])
def settings():
    user = User.query.filter().first()
    try:
        context = {
            "username": user.username,
            "api_id": user.api_id,
            "api_hash": user.api_hash,
            "phone": user.phone,
            "wp_user": user.wp_user,
            "wp_app_password": user.wp_app_password,
            "wp_website": user.wp_website
        }
        if request.method == "GET":
            return render_template('form.html',context=context)
        elif request.method == "POST":
            print('this is post')
            print([v for v in request.form.values()])
            form = request.form
            user.username = form.get("username")
            user.api_id = form.get("api_id")
            user.api_hash = form.get("api_hash")
            user.phone = form.get("phone")
            user.wp_user = form.get("wp_user")
            user.wp_app_password = form.get("wp_app_password")
            user.wp_website = form.get("wp_website")
            db.session.commit()
            flash("Saved Successfully")
            return redirect(url_for("settings"))

    except AttributeError:
        __handle_no_users()




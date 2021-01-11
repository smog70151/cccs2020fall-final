from flask import Flask, session, redirect, render_template, request, flash, url_for, json
from flask_socketio import SocketIO, emit, join_room
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user
from dbModel import UserAccounts, Message, Room, db
from functools import wraps
from PIL import Image
from datetime import datetime
import base64
import os
import uuid
import io
import random

MugShot_PATH = 'static/mugshot'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
MugShot_FOLDER = os.path.join(APP_ROOT, MugShot_PATH)

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = "Please LOG IN"
login_manager.login_message_category = "info"

socketio = SocketIO(app)
async_mode = "eventlet"

class User(UserMixin):
    pass

def to_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        get_fun = func(*args, **kwargs)
        return json.dumps(get_fun)

    return wrapper


def query_user(username):
    user = UserAccounts.query.filter_by(UserName=username).first()
    if user:
        return True
    return False

@login_manager.user_loader
def user_loader(username):
    if query_user(username):
        user = User()
        user.id = username
        return user
    return None


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    isLogin = False
    rooms = Room.query.all()
    room_dict = {}
    room_list = []
    for room in rooms:
        room_dict['user_id'] = str(room.UserID)
        room_dict['title'] = str(room.Title)
        room_dict['room_id'] = Room.md5(room.Title + room.URL + room.UserID)
        room_list.append(room_dict)

    if current_user.is_authenticated:
        isLogin = True
        user = {}
        user['name'] = session.get('user_id')
        user['role'] = UserAccounts.query.filter_by(UserName=user['name']).first().Role

    return render_template("home.html", **locals())

@app.route('/channels', methods=['GET'])
def channels():
    isLogin = False
    rooms = Room.query.all()
    room_list = []
    for room in rooms:
        room_dict = {}
        room_dict['user_id'] = str(room.UserID)
        room_dict['title'] = str(room.Title)
        room_dict['url'] = str(room.URL)
        room_dict['room_id'] = Room.md5(room.Title + room.URL + room.UserID)
        room_list.append(room_dict)

    if current_user.is_authenticated:
        isLogin = True
        user = {}
        user['name'] = session.get('user_id')
        user['role'] = UserAccounts.query.filter_by(UserName=user['name']).first().Role

    return render_template("channels.html", **locals())


@app.route('/index/<room_id>', methods=['GET'])
#@app.route('/index', methods=['GET','POST'])
@login_required
def index(room_id):
    print("room_id: ", room_id)
    user_id = session.get('user_id')
    message_data = db.session.query(
        Message,
        UserAccounts.MugShot
    ).join(
        UserAccounts,
        UserAccounts.UserName == Message.UserName,
    ).filter(Message.RoomId == room_id).all()
    mug_shot_title = UserAccounts.query.filter_by(UserName=user_id).first().MugShot
    role = UserAccounts.query.filter_by(UserName=user_id).first().Role
    messages_dic = {}
    messages_list = []
    for message in message_data:
        messages_dic['data'] = []
        messages_dic['UserName'] = message.Message.UserName
        messages_dic['Messages'] = message.Message.Messages
        messages_dic['MugShot'] = message.MugShot
        messages_dic['CreateDate'] = message.Message.CreateDate.strftime('%H:%M')
        messages_dic['RoomId'] = message.Message.RoomId
        messages_list.append(messages_dic)
        messages_dic = {}

    room = Room.query.filter_by(RoomID=room_id).first()#request.args.get('url')
    youtube_url = "https://www.youtube.com/embed/" + room.URL
    Title = room.Title#request.args.get('Title')
    RoomId = room_id
    user = {}
    user['name'] = user_id
    user['role'] = role
    isLogin = True

    return render_template("index.html", **locals())

@app.route('/login', methods=['GET', 'POST'])
def login():
    isLogin = False
    user_id = session.get('user_id')

    if request.method == 'GET':
        return render_template("login.html")

    if current_user.is_authenticated and query_user(user_id):
        return redirect(url_for('home'))

    username = request.form['username']
    user = UserAccounts.query.filter_by(UserName=username).first()
    if not user:
        return render_template("login.html", error="username or password error")
    pw_form = UserAccounts.psw_to_md5(request.form['password'])
    pw_db = user.Password
    if pw_form == pw_db:
        user = User()
        user.id = username
        login_user(user, remember=True)
        flash('Logged in successfully')
        return redirect(url_for('home'))
    return render_template("login.html", error="username or password error")


@app.route('/register', methods=['GET', 'POST'])
def register():
    isLogin = False
    if request.method == 'GET':
        return render_template("register.html")
    username = request.form['username']
    password = request.form['password']
    role = True if request.form['role'] == "host" else False
    mugshot = "default_{}.png".format(str(random.randint(1,9)))
    new_account = UserAccounts(user_name=username, password=password, mugshot=mugshot, role=role)
    db.session.add(new_account)
    db.session.commit()
    return redirect(url_for("home"))
'''
@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method =='POST':
        if request.values['send']=="Submit":
            url = "https://www.youtube.com/embed/" + str(request.values['url'])
            Title = request.values['title']
            return redirect(url_for('index', url=url, Title=Title))
    return render_template("info.html")
'''
@app.route('/create_room',methods=['POST'])
@login_required
def create_room():
    if request.method == 'POST':
        '''
        db table create room
        '''
        user_id = session.get('user_id')
        url_id = str(request.form['url'])
        url = "https://www.youtube.com/embed/" + url_id
        Title = request.form['title']
        room_id = Room.md5(Title + url_id + user_id)
        new_room = Room(title=Title,url=url_id,user_id=user_id,room_id=room_id)
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('index',room_id=room_id, youtube_url=url, Title=Title))
        #return redirect(url_for('index',room_id=room_id), youtube_url=url, Title=Title)

@app.route('/del_room', methods=['POST'])
@login_required
def del_room():
    if request.method == 'POST':
        '''
        db delete room
        '''
        user_id = session.get('user_id')

        url = str(request.form['url']).split('/')[-1]
        title = str(request.form['title'])
        Room.query.filter_by(Title=title, URL=url, UserID=user_id).delete()
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/API_check_UserNameExist', methods=['POST'])
@to_json
def api_check_user_name_exist():
    username = request.json['username']
    user = UserAccounts.query.filter_by(UserName=username).first()
    if not user:
        return "not_exist"
    return "exist"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@socketio.on('join')
def join(message):
    join_room(message['room'])
    print('join: ', message['room'])


@socketio.on('connect')
def test_connect():
    # Userid = session.get('UserId')
    # print(Userid, 'connectd')
    print('connect')


@socketio.on('sendInquiry')
def send_inquiry(msg):
    user_id = session.get('user_id')
    create_date = datetime.now()

    data_message = Message(
        user_name=user_id,
        messages=msg['msg'],
        create_date=create_date,
        room_id = str(msg['room'])
    )
    db.session.add(data_message)
    db.session.commit()
    mug_shot = UserAccounts.query.filter_by(UserName=user_id).first().MugShot
    data = {
        'time': create_date.strftime('%H:%M'),
        'Name': user_id,
        'PictureUrl': mug_shot,
        'msg': msg['msg'],
        'Ad':msg['Ad']
    }
    emit('getInquiry', data, room=msg['room'])


@app.route('/croppic', methods=['GET', 'POST'])
def croppic():
    user_id = session.get('user_id')
    try:
        # imgUrl 		// your image path (the one we recieved after successfull upload)
        img_url = request.form['imgUrl']
        # imgInitW  	// your image original width (the one we recieved after upload)
        # img_init_w = request.form['imgInitW']
        # imgInitH 	    // your image original height (the one we recieved after upload)
        # img_init_h = request.form['imgInitH']
        # imgW 		    // your new scaled image width
        img_w = request.form['imgW']
        # imgH 		    // your new scaled image height
        img_h = request.form['imgH']
        # imgX1 		// top left corner of the cropped image in relation to scaled image
        img_x1 = request.form['imgX1']
        # imgY1 		// top left corner of the cropped image in relation to scaled image
        img_y1 = request.form['imgY1']
        # cropW 		// cropped image width
        crop_w = request.form['cropW']
        # cropH 		// cropped image height
        crop_h = request.form['cropH']
        angle = request.form['rotation']

        # original size
        # imgInitW, imgInitH = int(img_init_w), int(img_init_h)

        # Adjusted size
        img_w, img_h = int(float(img_w)), int(float(img_h))
        img_y1, img_x1 = int(float(img_y1)), int(float(img_x1))
        crop_w, crop_h = int(float(crop_w)), int(float(crop_h))
        angle = int(angle)

        # image_format = imgUrl.split(';base64,')[0].split('/')[1]
        # title_head = img_url.split(',')[0]
        img_data = img_url.split('base64,')[1]
        img_data = base64.b64decode(img_data)

        source_image = Image.open(io.BytesIO(img_data))
        image_format = source_image.format.lower()
        # create new crop image
        source_image = source_image.resize((img_w, img_h), Image.ANTIALIAS)

        rotated_image = source_image.rotate(-float(angle), Image.BICUBIC)
        rotated_width, rotated_height = rotated_image.size
        dx = rotated_width - img_w
        dy = rotated_height - img_h
        cropped_rotated_image = Image.new('RGBA', (img_w, img_h))
        cropped_rotated_image.paste(rotated_image.crop((dx / 2, dy / 2, dx / 2 + img_w, dy / 2 + img_h)),
                                    (0, 0, img_w, img_h))

        final_image = Image.new('RGBA', (crop_w, crop_h), 0)
        final_image.paste(cropped_rotated_image.crop((img_x1, img_y1, img_x1 + crop_w, img_y1 + crop_h)),
                          (0, 0, crop_w, crop_h))

        uuid_name = str(uuid.uuid1())
        mugshot = '{}.{}'.format(uuid_name, image_format)
        user_mugshot = UserAccounts.query.filter_by(UserName=user_id).first()
        if user_mugshot.MugShot != "default.jpg":
            delete_filename = '{}/{}'.format(MugShot_FOLDER, user_mugshot.MugShot)
            os.remove(delete_filename)

        user_mugshot.MugShot = mugshot
        db.session.commit()
        save_path = '{}/{}'.format(MugShot_FOLDER, mugshot)
        final_image.save(save_path)

        data = {
            'status': 'success',
            'url': '/{}/{}'.format(MugShot_PATH, mugshot),
            'filename': mugshot
        }
        return json.dumps(data)
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
        }


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

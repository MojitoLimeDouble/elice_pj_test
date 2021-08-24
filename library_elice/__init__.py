from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO, send
import json

app = Flask(__name__)
# secret_key 설정하지 않으면 플라스크 로그인 기능 구현시 form 사용 불가
app.config['SECRET_KEY'] = 'c567a1920541422652e44a44'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elice_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 웹 소켓 동작시 기존 utf-8 인코딩이 아닌 ascii값으로 인코딩 되어 출력하기 때문에 넣어주는 코드
app.config['JSON_AS_ASCII'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# routes.py에 있는 login_page함수 redirect, 따라서 로그인이 필요한 페이지에 접근할 때 회원이 아니라면 먼저 로그인 페이지로 이동함.
login_manager.login_view = "login_page"
login_manager.login_message = "로그인 후 접근이 가능합니다."
login_manager.login_message_category = "info"

socketio = SocketIO(app, cors_allowed_origins='*')


from library_elice import routes # 이 코드의 위치가 중요함. 맨위에 놓으면 오류! routes.py파일에서 먼저 init.py파일을 불러오기 때문! 둘이 겹침!
from flask import Flask
from library_elice import app # __init__에 있는 app 불러오기
from library_elice import socketio # __init__에 있는 socketio 불러오기
from flask_socketio import SocketIO, send


if __name__ == '__main__': # flask server 실행은 여기서
    app.run(debug=True)
    # 웹소켓을 킬 때는 아래로
    # socketio.run(app)

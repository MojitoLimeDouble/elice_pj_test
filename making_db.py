from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from library_elice.models import db
from library_elice.models import User, Book

# 데이터베이스 삭제
# db.drop_all()
# db.session.commit()

# 데이터베이스 생성
db.create_all()
db.session.commit()


# 데이터 만들기 예시
# u1 = User(username = 'jsc', password_hash='123456', email_address='jsc@jsc.com')
# db.session.add(u1)
# db.session.commit()
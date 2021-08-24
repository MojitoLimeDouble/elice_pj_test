from library_elice import db, login_manager
from library_elice import bcrypt
from flask_login import UserMixin
import datetime
# UserMixin에서 is_active, is_authenticated, is_anonymous, get_id다 포함함 개꿀~

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 유저정보
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email_address = db.Column(db.String(length=30), nullable=False, unique=True)
    username = db.Column(db.String(length=30), nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    borrow_cnt = db.Column(db.Integer(), nullable=False, default=2)
    borrow_book = db.relationship('Book', backref='borrowed_user', lazy=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)


    @property
    def password(self):
        return self.password

    # 비밀번호를 해시값으로 변환시킴
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    # 만약 해시값으로 비밀번호가 처리되었으면 로그인 시도할 때는 그것을 다시 평문으로 읽어 옴(단, 비밀번호가 일치한다면)
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    # 빌릴 수 있는 횟수가 아직 있는 경우
    def can_borrow(self, book_obj):
        return self.borrow_cnt >= 1
    
    # 책을 반납하는 경우
    def can_return(self, book_obj):
        return book_obj in self.borrow_book



# 도서 리스트 정보
class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    book_name = db.Column(db.String(length=30), nullable=False)
    publisher = db.Column(db.String(length=30), nullable=False)
    author = db.Column(db.String(length=30), nullable=False)
    publication_date = db.Column(db.DateTime)
    pages = db.Column(db.Integer)
    isbn = db.Column(db.Integer, nullable=False, unique=True)
    description = db.Column(db.String)
    link = db.Column(db.String)
    borrower = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=True)
    quantity = db.Column(db.Integer(), nullable=False, default=1)
    likes = db.relationship('Like', backref='book', passive_deletes=True)


    def __repr__(self):
        return f'Book {self.book_name}'

    def borrow(self, user):
        self.borrower = user.id
        user.borrow_cnt -= 1
        self.quantity -= 1
        db.session.commit()
    
    def returned(self, user):
        self.borrower = None
        user.borrow_cnt += 1
        self.quantity += 1
        db.session.commit()

# 좋아유 정보
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete="CASCADE"), nullable=False)

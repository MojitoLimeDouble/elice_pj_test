# route들을 보기쉽게 모아 놓은 파일
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from library_elice import app, db, socketio
from library_elice.forms import RegisterForm, LoginForm, BorrowForm, ReturnForm
from flask_login import login_user, logout_user, login_required, current_user
from library_elice.models import User, Book, Like
from flask_socketio import SocketIO, send

# 홈페이지
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # 이메일과 비밀번호가 데이터베이스와 일치하면 로그인 성공
        attempted_email = User.query.filter_by(email_address=form.email_address.data).first()
        if attempted_email and attempted_email.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_email)
            flash(f'{attempted_email.username}님 어서오고~', category='success')
            return redirect(url_for('home_page'))
        # 이메일이랑 비번이 틀리면
        else:
            flash('로그인을 다시 시도해주세요!', category='danger')


    # form을 메소드의 일부로 전달해야함. 안그러면 html에서 읽지 못함 form이뭔지
    return render_template('login.html', form=form)

# 회원가입 페이지
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(email_address=form.email_address.data,username=form.username.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        
        login_user(user_to_create)
        flash(f'회원가입이 완료되었습니다. {user_to_create.username}님 환영합니다.', category='success')

        # 회원가입 성공시 홈페이지로
        return redirect(url_for('home_page'))
    
    # 회원가입 양식에 안맞으면 메시지 출력
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'회원가입을 하기 위해 다음의 지시를 따라주세요.: {err_msg}', category='danger')

    return render_template('register.html', form=form)

# 책 목록 페이지
@app.route('/book_list', methods=['GET', 'POST'])
# 로그인이 필요한 페이지에 사용하는 코드
@login_required
def book_list_page():
    borrow_form = BorrowForm()
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 대여 알고리즘
        borrow_book = request.form.get('borrow_book')
        b_book_object = Book.query.filter_by(book_name=borrow_book).first()
        # 책 빌릴 때 최대 횟수는 2회, 한번 빌릴 때 1 차감하기
        if b_book_object:
            if current_user.can_borrow(b_book_object):
                b_book_object.borrow(current_user)
                flash(f"{b_book_object.book_name}을 성공적으로 대출하였습니다.", category='success')
            else:
                flash("도서 대출 가능 횟수를 초과하셨습니다.", category='danger')
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        users = User.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('book_list.html', books=books, borrow_form=borrow_form, borrowed_books=borrowed_books, return_book_form=return_book_form, users=users)

# 오디오 북 페이지
@app.route('/audio_book', methods=['GET', 'POST'])
@login_required
def audio_book_page():
    return render_template('audiobook.html')

# 오고 가시는 길 페이지
@app.route('/comeon', methods=['GET', 'POST'])
def comeon_page():
    return render_template('comeon.html')

# FAQ 페이지
@app.route('/FAQ', methods=['GET', 'POST'])
def faq_page():
    return render_template('question.html')

# 로그아웃
@app.route('/logout')
def logout_page():
    logout_user()
    flash("성공적으로 로그아웃 하셨습니다.", category='info')
    return redirect(url_for('home_page'))

# 내정보
@app.route('/mypage', methods=['GET', 'POST'])
def my_page():
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('my_page.html', books=books, borrowed_books=borrowed_books, return_book_form=return_book_form)

# 테스트
@app.route('/test', methods=['GET', 'POST'])
def test_page():
    return render_template('test.html')

# 책 리스트 페이지2 
@app.route('/book_list2', methods=['GET', 'POST'])
def book_list_page2():
    borrow_form = BorrowForm()
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 대여 알고리즘
        borrow_book = request.form.get('borrow_book')
        b_book_object = Book.query.filter_by(book_name=borrow_book).first()
        # 책 빌릴 때 최대 횟수는 2회, 한번 빌릴 때 1 차감하기
        if b_book_object:
            if current_user.can_borrow(b_book_object):
                b_book_object.borrow(current_user)
                flash(f"{b_book_object.book_name}을 성공적으로 대출하였습니다.", category='success')
            else:
                flash("도서 대출 가능 횟수를 초과하셨습니다.", category='danger')
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page2'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        users = User.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('book_list2.html', books=books, borrow_form=borrow_form, borrowed_books=borrowed_books, return_book_form=return_book_form, users=users)

# 책 리스트 페이지3 
@app.route('/book_list3', methods=['GET', 'POST'])
def book_list_page3():
    borrow_form = BorrowForm()
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 대여 알고리즘
        borrow_book = request.form.get('borrow_book')
        b_book_object = Book.query.filter_by(book_name=borrow_book).first()
        # 책 빌릴 때 최대 횟수는 2회, 한번 빌릴 때 1 차감하기
        if b_book_object:
            if current_user.can_borrow(b_book_object):
                b_book_object.borrow(current_user)
                flash(f"{b_book_object.book_name}을 성공적으로 대출하였습니다.", category='success')
            else:
                flash("도서 대출 가능 횟수를 초과하셨습니다.", category='danger')
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page3'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        users = User.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('book_list3.html', books=books, borrow_form=borrow_form, borrowed_books=borrowed_books, return_book_form=return_book_form, users=users)

# 책 리스트 페이지4 
@app.route('/book_list4', methods=['GET', 'POST'])
def book_list_page4():
    borrow_form = BorrowForm()
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 대여 알고리즘
        borrow_book = request.form.get('borrow_book')
        b_book_object = Book.query.filter_by(book_name=borrow_book).first()
        # 책 빌릴 때 최대 횟수는 2회, 한번 빌릴 때 1 차감하기
        if b_book_object:
            if current_user.can_borrow(b_book_object):
                b_book_object.borrow(current_user)
                flash(f"{b_book_object.book_name}을 성공적으로 대출하였습니다.", category='success')
            else:
                flash("도서 대출 가능 횟수를 초과하셨습니다.", category='danger')
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page4'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        users = User.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('book_list4.html', books=books, borrow_form=borrow_form, borrowed_books=borrowed_books, return_book_form=return_book_form, users=users)

# 책 리스트 페이지5 
@app.route('/book_list5', methods=['GET', 'POST'])
def book_list_page5():
    borrow_form = BorrowForm()
    return_book_form = ReturnForm()
    if request.method == "POST":
        # 대여 알고리즘
        borrow_book = request.form.get('borrow_book')
        b_book_object = Book.query.filter_by(book_name=borrow_book).first()
        # 책 빌릴 때 최대 횟수는 2회, 한번 빌릴 때 1 차감하기
        if b_book_object:
            if current_user.can_borrow(b_book_object):
                b_book_object.borrow(current_user)
                flash(f"{b_book_object.book_name}을 성공적으로 대출하였습니다.", category='success')
            else:
                flash("도서 대출 가능 횟수를 초과하셨습니다.", category='danger')
        # 반납 알고리즘
        returning_book = request.form.get('returning_book')
        r_book_object = Book.query.filter_by(book_name=returning_book).first()
        if r_book_object:
            if current_user.can_return(r_book_object):
                r_book_object.returned(current_user)
                flash(f"{r_book_object.book_name}을 성공적으로 반납하였습니다.", category='success')
            else:
                flash("도서를 반납하는데 오류가 발생하였습니다. 엘리스에 문의해주시길 바랍니다.", category='danger')
        
        return redirect(url_for('book_list_page5'))

    if request.method == "GET":
        # 대출이 가능하든 불가능 하든 책의 정보를 불러옴, 만약 대출 불가한 책들을 제외하고 싶다면 books = Book.query.filter_by(borrower=None)
        books = Book.query.all()
        users = User.query.all()
        borrowed_books = Book.query.filter_by(borrower=current_user.id)
        return render_template('book_list5.html', books=books, borrow_form=borrow_form, borrowed_books=borrowed_books, return_book_form=return_book_form, users=users)

# 휴게실
@app.route('/game', methods=['GET', 'POST'])
@login_required
def game_page():
    return render_template('game.html')

# 크레딧
@app.route('/credit', methods=['GET', 'POST'])
def credit_page():
    return render_template('credit.html')

# 실시간 채팅방 (웹 소켓으로 구현)
@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_page():
    if request.method == "GET":
        users = User.query.filter_by(username=current_user.username)
    return render_template('chat.html', users=users)

# 책추천(여름)
@app.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend_page():
    return render_template('horror_home.html')

# 좋아유~
@app.route("/like-book/<book_id>", methods=['GET', 'POST'])
@login_required
def like(book_id):
    book = Book.query.filter_by(id=book_id).first()
    like = Like.query.filter_by(author=current_user.id, book_id=book_id).first()

    if not book:
        flash('책 정보가 존재하지 않습니다.', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, book_id=book_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('book_list_page'))

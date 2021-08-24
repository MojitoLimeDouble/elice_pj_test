from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, InputRequired
from library_elice.models import User

# 회원가입 폼
class RegisterForm(FlaskForm):
    # 이메일이 중복이면 경고창 뜨게하기
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('이미 존재하는 이메일입니다. 다른 이메일을 작성해주세요.')

    email_address = StringField(label=' ', validators=[Email(), DataRequired()])
    username = StringField(label=' ', validators=[Length(min=2, max=30), DataRequired()])
    #비밀번호 최소 10자리
    password1 = PasswordField(label=' ', validators=[Length(min=10), DataRequired()])
    password2 = PasswordField(label=' ', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='회원가입')

# 로그인 폼
class LoginForm(FlaskForm):
    email_address = StringField(label=' ', validators=[DataRequired()])
    password = PasswordField(label=' ', validators=[DataRequired()])
    submit = SubmitField(label='로그인')

# 도서 대여 폼
class BorrowForm(FlaskForm):
    submit = SubmitField(label='대출하기')

# 책 반납 폼
class ReturnForm(FlaskForm):
    submit = SubmitField(label='반납하기')


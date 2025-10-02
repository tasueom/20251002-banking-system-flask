from flask import Flask, render_template as ren, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash as gen_pw, check_password_hash as chk_pw
import db
import datetime

app = Flask(__name__)
app.secret_key = "secret_key_b"

#아이디, 이름, 역할을 전역 컨텍스트로 사용
@app.context_processor
def inject_user():
    return dict(uid=session.get("uid"), name=session.get("name"), role=session.get("role"))

@app.route("/")
def index():
    return ren("index.html")

#회원가입
@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == "POST":
        uid = request.form["uid"]
        password = request.form["password"]
        hashed_pw = gen_pw(password)
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        
        try:
            db.signup(uid,hashed_pw,name,phone,email)
        except:
            flash("이미 존재하는 아이디입니다")
            return redirect(url_for("signup"))
        flash("회원가입을 성공하였습니다.")
        return redirect(url_for("signin"))
    return ren("signup.html")

#로그인
@app.route("/signin", methods=['GET','POST'])
def signin():
    if request.method == "POST":
        uid = request.form["uid"]
        password = request.form["password"]
        
        correct_pw, name, role = db.get_user(uid)
        #로그인 성공
        if correct_pw and chk_pw(correct_pw, password):
            # 세션에 정보 등록
            session["uid"] = uid
            session["name"] = name
            session["role"] = role
            return redirect(url_for("index"))
        else:
            return redirect(url_for("signin"))
    return ren("signin.html")

# 로그아웃
@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for("index"))

# 내 계좌 목록 확인
@app.route("/my_acc")
def my_acc():
    uid = session.get("uid")
    accs = db.get_my_acc(uid)
    
    return ren("my_acc.html",accs=accs)

# 계좌 개설
@app.route("/create_acc", methods=['GET','POST'])
def create_acc():
    uid = session.get("uid")
    if request.method == "POST":
        acc_no = request.form["acc_no"]
        balance = request.form["balance"]
        try:
            db.create_acc(acc_no, uid, balance)
            flash("계좌가 정상적으로 개설되었습니다.")
            page = "my_acc"
        except:
            flash("계좌 개설 중 오류가 발생하였습니다.")
            page = "create_acc"
        return redirect(url_for(page))
    acc_no = "100-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return ren("create_acc.html", acc_no=acc_no)

#입금, 출금
@app.route("/transaction", methods=['GET','POST'])
def deposit():
    uid = session.get("uid")
    if request.method == "POST":
        acc_no = request.form["acc_no"]
        trans_type = request.form["trans_type"]
        amount = request.form["amount"]
        existing_balance = db.get_balance(acc_no)
        if trans_type=="입금":
            balance = existing_balance+amount
        else:
            balance = existing_balance-amount
    # 내 계좌 목록 선택하여 넘김
    accs = db.get_my_acc(uid)
    return ren("deposit.html", accs=accs)

#Flask 서버 실행
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
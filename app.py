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
        
        row = db.get_user(uid)
        if row:
            correct_pw = row[1]
            name = row[2]
            role = row[5]
            #로그인 성공
            if chk_pw(correct_pw, password):
                # 세션에 정보 등록
                session["uid"] = uid
                session["name"] = name
                session["role"] = role
                return redirect(url_for("index"))
        flash("아이디 혹은 비밀번호를 확인해주세요.")
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
def transaction():
    uid = session.get("uid")
    if request.method == "POST":
        acc_no = request.form["acc_no"]
        trans_type = request.form["trans_type"]
        amount = int(request.form["amount"])
        existing_balance = db.get_acc(acc_no)[2]
        if trans_type=="입금":
            balance = existing_balance+amount
        else:
            if existing_balance < amount:
                flash("출금 한도를 초과하였습니다.")
                return redirect(url_for("transaction"))
            balance = existing_balance-amount
        db.transaction(acc_no, trans_type, amount, balance)
        flash("정상적으로 완료되었습니다.")
        
        return redirect(url_for("my_acc"))
    # 내 계좌 목록 선택하여 넘김
    accs = db.get_my_acc(uid)
    return ren("transaction.html", accs=accs)

# 계좌이체
@app.route("/transfer", methods=['GET','POST'])
def transfer():
    uid = session.get("uid")
    if request.method == "POST":
        to_acc_no = request.form["to_acc_no"]
        acc_no = request.form["acc_no"]
        amount = int(request.form["amount"])
        existing_balance = db.get_acc(acc_no)[2]
        
        # 받는사람 계좌가 존재하는지 판단
        to_acc = db.get_acc(to_acc_no)
        if not to_acc:
            flash("받는 분 계좌가 존재하지 않습니다")
            return redirect(url_for("transfer"))
        # 출금 한도 초과여부 판단
        if existing_balance < amount:
            flash("출금 한도를 초과하였습니다.")
            return redirect(url_for("transaction"))
        to_balance = db.get_acc(to_acc_no)[2]+amount
        balance = existing_balance-amount
        
        db.transfer(to_acc_no, acc_no, amount, to_balance, balance)
        flash("이체에 성공하였습니다.")
        return redirect(url_for("my_acc"))
    # 내 계좌 목록 선택하여 넘김
    accs = db.get_my_acc(uid)
    return ren("transfer.html", accs=accs)

# 계좌별 거래내역 조회
@app.route("/get_trans_log")
def get_trans_log():
    acc_no = request.args["acc_no"]
    trans_log = db.get_trans_log(acc_no)
    return ren("trans_log.html", trans_log=trans_log)

# (관리자) 전체 회원 조회
@app.route("/user_list")
def user_list():
    if session.get("role") != "admin":
        flash("관리자 전용 페이지입니다.")
        return redirect(url_for("index"))
    user_list = db.get_all_users()
    
    return ren("user_list.html", user_list=user_list)

# (관리자) 전체 계좌 조회
@app.route("/acc_list")
def acc_list():
    if session.get("role") != "admin":
        flash("관리자 전용 페이지입니다.")
        return redirect(url_for("index"))
    acc_list = db.get_all_accs()
    
    return ren("acc_list.html", acc_list=acc_list)

# (관리자) 전체 거래 내역 조회
@app.route("/transaction_list")
def transaction_list():
    if session.get("role") != "admin":
        flash("관리자 전용 페이지입니다.")
        return redirect(url_for("index"))
    acc_search = request.args.get("acc_search", "0")
    if acc_search == "0":
        trans_list = db.list_transactions()
    else:
        trans_list = db.get_trans_log(acc_search)
    acc_list = db.get_all_accs()
    
    return ren("transaction_list.html", trans_list=trans_list, acc_list=acc_list, acc_search=acc_search)

#Flask 서버 실행
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
from flask import Flask, render_template as ren, request, redirect, url_for, session
from werkzeug.security import generate_password_hash as gen_pw, check_password_hash as chk_pw
import db

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
            return redirect(url_for("signup"))
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

#Flask 서버 실행
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
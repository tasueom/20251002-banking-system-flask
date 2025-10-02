from flask import Flask, render_template as ren, request, redirect, url_for, session
from werkzeug.security import generate_password_hash as gen_pw, check_password_hash as chk_pw
import db

app = Flask(__name__)
app.secret_key = "secret_key_b"

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

#Flask 서버 실행
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
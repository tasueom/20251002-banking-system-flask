from flask import Flask, render_template as ren, request, redirect, url_for, session
from werkzeug.security import generate_password_hash as gen_pw, check_password_hash as chk_pw

app = Flask(__name__)
app.secret_key = "secret_key_b"

#Flask 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
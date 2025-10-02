from flask import Flask, render_template as ren, request, redirect, url_for, session

app = Flask(__name__)

#Flask 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
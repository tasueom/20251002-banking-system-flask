import mysql.connector
from werkzeug.security import generate_password_hash as gen_pw

# MySQL 기본 연결 설정 (데이터베이스를 지정하지 않고 접속)
base_config = {
    "host": "localhost",   # MySQL 서버 주소 (로컬)
    "user": "root",        # MySQL 계정
    "password": "1234"     # MySQL 비밀번호
}

# 사용할 데이터베이스 이름
DB_NAME = "bankdb"

# 커넥션과 커서 반환하는 함수
def get_conn():
    return mysql.connector.connect(database=DB_NAME, **base_config)

#테이블 생성
def init_db():
    # DB 생성 (없으면 자동 생성)
    conn = mysql.connector.connect(**base_config)
    cur = conn.cursor()
    cur.execute(f"create database if not exists {DB_NAME} default character set utf8mb4")
    conn.commit()
    conn.close()
    
    conn = get_conn()
    cur = conn.cursor()
    #회원 테이블
    cur.execute("""
                CREATE TABLE if not exists users (
                uid VARCHAR(50) PRIMARY KEY,
                password VARCHAR(200) NOT NULL,
                name VARCHAR(50) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                role VARCHAR(10) DEFAULT 'user'
                )
                """)
    
    #계좌 테이블
    cur.execute("""
                CREATE TABLE if not exists accounts (
                acc_no VARCHAR(20) PRIMARY KEY,
                uid VARCHAR(50),
                balance INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
    
    #거래 내역 테이블
    cur.execute("""
                CREATE TABLE if not exists transactions (
                trans_id INT AUTO_INCREMENT PRIMARY KEY,
                acc_no VARCHAR(20),
                trans_type VARCHAR(10),
                amount INT,
                balance INT,
                trans_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
    
    # 관리자 계정 미리 삽입
    password = gen_pw("1234")
    try:
        cur.execute("""
            insert into users(uid, name, password, role)
            values('admin', '관리자', %s, 'admin')
        """,(password,))
        conn.commit()
    except:
        pass
    
    conn.commit()
    conn.close()

#회원가입
def signup(uid, password, name, phone, email):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
                    insert into users(uid, password, name, phone, email) values(%s,%s,%s,%s,%s)
                    """,(uid, password, name, phone, email))
        conn.commit()
    finally:
        conn.close()

# 아이디로 비밀번호, 이름, 역할 반환함수
# 로그인 검증과 세션 정보 등록에 사용된다
def get_user(uid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("select password, name, role from users where uid = %s",(uid,))
    row = cur.fetchone()
    conn.close()
    return row

# 아이디로 내 계좌 선택
def get_my_acc(uid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
                select acc_no, balance, created_at
                from accounts
                where uid = %s
                """,(uid,))
    rows = cur.fetchall()
    conn.close()
    
    return rows

#계좌 개설
def create_acc(acc_no,uid,balance):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
                    insert into accounts(acc_no, uid, balance)
                    values(%s, %s, %s)
                    """,(acc_no, uid, balance))
        conn.commit()
    finally:
        conn.close()

# 계좌 단건 조회
def get_acc(acc_no):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("select acc_no, uid, balance from accounts where acc_no=%s", (acc_no,))
    row = cur.fetchone()
    conn.close()
    return row

# 입금, 출금
def transaction(acc_no, trans_type, amount, balance):
    conn = get_conn()
    cur = conn.cursor()
    # 계좌 테이블에서 잔액 업데이트
    cur.execute("""
                update accounts set
                balance = %s
                where acc_no = %s
                """,(balance, acc_no))
    cur.execute("""
                insert into transactions(acc_no, trans_type, amount, balance)
                values(%s, %s, %s, %s)
                """,(acc_no, trans_type, amount, balance))
    conn.commit()
    conn.close()

# 계좌 이체
def transfer(to_acc_no, acc_no, amount, to_balance, balance):
    conn = get_conn()
    cur = conn.cursor()
    # 내 계좌 테이블에서 잔액 업데이트
    cur.execute("""
                update accounts set
                balance = balance - %s
                where acc_no = %s
                """,(amount, acc_no))
    # 내 이체 내역을 거래내역 테이블에 삽입
    cur.execute("""
                insert into transactions(acc_no, trans_type, amount, balance)
                values(%s, %s, %s, %s)
                """,(acc_no, "이체(출금)", amount, balance))
    # 상대 계좌 테이블에서 잔액 업데이트
    cur.execute("""
                update accounts set
                balance = balance + %s
                where acc_no = %s
                """,(amount, to_acc_no))
    # 상대 이체 내역을 거래내역 테이블에 삽입
    cur.execute("""
                insert into transactions(acc_no, trans_type, amount, balance)
                values(%s, %s, %s, %s)
                """,(to_acc_no, "이체(입금)", amount, to_balance))
    
    conn.commit()
    conn.close()

# 계좌별 거래내역 조회
def get_trans_log(acc_no):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
                select
                trans_type, amount, balance, trans_date
                from transactions
                where acc_no = %s
                """,(acc_no,))
    rows = cur.fetchall()
    conn.close()
    
    return rows

# 모든 회원의 정보 선택
def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
                select uid, name, phone, email
                from users
                where uid != 'admin'
                """)
    rows = cur.fetchall()
    conn.close()
    
    return rows

# 모든 계좌 정보 선택
def get_all_accs():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("select * from accounts")
    rows = cur.fetchall()
    conn.close()
    
    return rows

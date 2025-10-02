import mysql.connector

# MySQL 기본 연결 설정 (데이터베이스를 지정하지 않고 접속)
base_config = {
    "host": "localhost",   # MySQL 서버 주소 (로컬)
    "user": "root",        # MySQL 계정
    "password": "1234"     # MySQL 비밀번호
}

# 사용할 데이터베이스 이름
DB_NAME = "bankdb"

# 커넥션과 커서 반환하는 함수
def conn_db():
    conn = mysql.connector.connect(database=DB_NAME, **base_config)
    cur = conn.cursor()
    return conn, cur

#테이블 생성
def init_db():
    # DB 생성 (없으면 자동 생성)
    conn = mysql.connector.connect(**base_config)
    cur = conn.cursor()
    cur.execute(f"create database if not exists {DB_NAME} default character set utf8mb4")
    conn.commit()
    conn.close()
    
    conn, cur = conn_db()
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
    
    conn.commit()
    conn.close()
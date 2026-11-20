from flask import Flask, request, jsonify
from flask_cors import CORS
from db import conn

app = Flask(__name__)
CORS(app)

@app.route("/register", methods=["POST"])

def register():

    try:

        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({
                "message": "資料不完整"
            }), 400

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )

        if cursor.fetchone():
            return jsonify({
                "message": "帳號已存在"
            }), 400

        cursor.execute(
            """
            INSERT INTO users
            (username,email,password,role_id)
            VALUES(%s,%s,%s,%s)
            """,
            (username, email, password, 2)
        )

        conn.commit()

        return jsonify({
            "message": "註冊成功"
        })

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username=%s
            AND password=%s
            """,
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            return jsonify({
                "message": "登入成功"
            }), 200

        return jsonify({
            "message": "帳號或密碼錯誤"
        }), 401

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
    
   


if __name__ == "__main__":
    app.run(debug=True)
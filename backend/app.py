<<<<<<< HEAD
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_conn
=======
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import conn
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc

app = Flask(__name__)
CORS(app)

<<<<<<< HEAD

@app.route("/register", methods=["POST"])
def register():
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        role_id = data.get("role_id", 2)

        if not username or not email or not password:
            return jsonify({"message": "資料不完整"}), 400

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            return jsonify({"message": "帳號或信箱已存在"}), 400

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (username, email, password, role_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, username, email, role_id
            """,
            (username, email, password_hash, role_id),
        )
        created_user = cursor.fetchone()
        conn.commit()

        return jsonify(
            {
                "message": "註冊成功",
                "user": {
                    "user_id": created_user[0],
                    "username": created_user[1],
                    "email": created_user[2],
                    "role_id": created_user[3],
                },
            }
        ), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/login", methods=["POST"])
def login():
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}

        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"message": "請輸入帳號與密碼"}), 400

        conn = get_conn()
=======
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

>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
        cursor = conn.cursor()

        cursor.execute(
            """
<<<<<<< HEAD
            SELECT u.id, u.username, u.email, u.password, u.role_id, r.name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.username = %s
            """,
            (username,),
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "帳號或密碼錯誤"}), 401

        user_id, db_username, db_email, stored_password, role_id, role_name = user

        is_valid = False
        if stored_password and (
            stored_password.startswith("scrypt:")
            or stored_password.startswith("pbkdf2:")
        ):
            is_valid = check_password_hash(stored_password, password)
        else:
            is_valid = stored_password == password

        if not is_valid:
            return jsonify({"message": "帳號或密碼錯誤"}), 401

        return jsonify(
            {
                "message": "登入成功",
                "user": {
                    "user_id": user_id,
                    "username": db_username,
                    "email": db_email,
                    "role_id": role_id,
                    "role_name": role_name,
                },
            }
        ), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT u.id, u.username, u.email, u.role_id, r.name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "找不到該使用者"}), 404

        return jsonify(
            {
                "user": {
                    "user_id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "role_id": user[3],
                    "role_name": user[4],
                }
            }
        ), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
=======
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
    
   
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc


if __name__ == "__main__":
    app.run(debug=True)
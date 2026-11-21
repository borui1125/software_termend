from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_conn

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        # 允許註冊時選擇身分：2=Teacher, 3=User（禁止前端直接註冊成 1=Admin）
        role_id = int(data.get("role_id", 3))
        if role_id not in (2, 3):
            role_id = 3

        if not username or not email or not password:
            return jsonify({"message": "資料不完整，請填寫帳號、信箱與密碼"}), 400

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
            INSERT INTO users (username, email, password, role_id, status)
            VALUES (%s, %s, %s, %s, 'approved')
            RETURNING id, username, email, role_id, status
            """,
            (username, email, password_hash, role_id),
        )
        created_user = cursor.fetchone()
        conn.commit()

        role_names = {1: "Admin", 2: "Teacher", 3: "User"}
        return jsonify({
            "message": "註冊成功",
            "user": {
                "user_id": created_user[0],
                "username": created_user[1],
                "email": created_user[2],
                "role_id": created_user[3],
                "role_name": role_names.get(created_user[3], "User"),
                "role": role_names.get(created_user[3], "User"),
                "status": created_user[4],
            },
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": f"伺服器錯誤：{str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route("/api/login", methods=["POST"])
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
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT u.id, u.username, u.email, u.password, u.role_id, r.name, u.status
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.username = %s
            """,
            (username,),
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "帳號或密碼錯誤"}), 401

        user_id, db_username, db_email, stored_password, role_id, role_name, status = user

        # 驗證密碼（相容加密密碼與預設測試帳號明碼）
        if stored_password and (
            stored_password.startswith("scrypt:") or stored_password.startswith("pbkdf2:")
        ):
            is_valid = check_password_hash(stored_password, password)
        else:
            is_valid = stored_password == password

        if not is_valid:
            return jsonify({"message": "帳號或密碼錯誤"}), 401

        return jsonify({
            "message": "登入成功",
            "user": {
                "user_id": user_id,
                "username": db_username,
                "email": db_email,
                "role_id": role_id,
                "role_name": role_name,
                "role": role_name,
                "status": status,
            },
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": f"伺服器錯誤：{str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route("/api/users", methods=["GET"])
@auth_bp.route("/api/admin/users", methods=["GET"])
def list_users():
    """管理員取得所有帳號清單"""
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, u.email, u.role_id, r.name, u.status, u.created_at
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.id ASC
            """
        )
        rows = cursor.fetchall()
        users = [
            {
                "user_id": row[0],
                "username": row[1],
                "email": row[2],
                "role_id": row[3],
                "role_name": row[4],
                "status": row[5],
                "created_at": row[6].strftime("%Y-%m-%d %H:%M") if row[6] else "",
            }
            for row in rows
        ]
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """調整帳號角色"""
    conn = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}
        role_id = data.get("role_id")

        conn = get_conn()
        cursor = conn.cursor()

        if role_id not in (1, 2, 3, "1", "2", "3"):
            return jsonify({"message": "無效的角色"}), 400

        cursor.execute(
            "UPDATE users SET role_id = %s, status = 'approved' WHERE id = %s",
            (int(role_id), user_id),
        )

        conn.commit()
        return jsonify({"message": "帳號角色已更新"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "帳號已刪除"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
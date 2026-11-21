from flask import Blueprint, jsonify
from db import get_conn

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/api/courses", methods=["GET"])
def get_courses():
    """取得課程排課清單"""
    conn = None
    cursor = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.course_name, c.teacher_id, u.username,
                   c.room_id, r.room_code, c.course_date, c.start_time, c.end_time, c.status
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            LEFT JOIN rooms r ON c.room_id = r.id
            ORDER BY c.course_date ASC, c.start_time ASC
            """
        )
        courses = [
            {
                "id": row[0],
                "course_name": row[1],
                "teacher_id": row[2],
                "teacher_name": row[3],
                "room_id": row[4],
                "room_code": row[5],
                "course_date": str(row[6]),
                "start_time": str(row[7])[:5],
                "end_time": str(row[8])[:5],
                "status": row[9],
            }
            for row in cursor.fetchall()
        ]
        return jsonify({"courses": courses}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# TODO (組員 C): 實作老師志願排課 CRUD、管理員指派與拖拉更新時間、時間衝突清單（含與已核准空間借用的衝突比對）
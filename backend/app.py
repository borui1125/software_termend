from flask import Flask, jsonify
from flask_cors import CORS

from routers.auth import auth_bp
from routers.spaces import spaces_bp
from routers.bookings import bookings_bp
from routers.courses import courses_bp

app = Flask(__name__)
CORS(app)

# 註冊各模組藍圖
app.register_blueprint(auth_bp)
app.register_blueprint(spaces_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(courses_bp)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "管院小幫手後端運行中"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    g,
    make_response,
    current_app,
)
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from database import get_db

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("admin.dashboard"))
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            access_payload = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "exp": datetime.now() + timedelta(minutes=15),
            }
            session_payload = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }

            access_token = jwt.encode(
                access_payload, current_app.config["SECRET_KEY"], algorithm="HS256"
            )
            session_token = jwt.encode(
                session_payload, current_app.config["SECRET_KEY"], algorithm="HS256"
            )

            resp = make_response(redirect(url_for("admin.dashboard")))
            resp.set_cookie("accesstoken", access_token, httponly=True)
            resp.set_cookie("sessiontoken", session_token, httponly=True)
            return resp
        else:
            error = "Sai tên đăng nhập hoặc mật khẩu."

    return render_template("login.html", error=error)


@user_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for("donvi.index")))
    resp.delete_cookie("accesstoken")
    resp.delete_cookie("sessiontoken")
    return resp

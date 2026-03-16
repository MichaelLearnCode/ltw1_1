from flask import Flask, request, g, Response
import jwt
from database import init_db, get_db
from datetime import datetime, timedelta, timezone

from user import user_bp
from donvi import donvi_bp
from admin import admin_bp

import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("MY_SECRET_KEY")

init_db()


@app.before_request
def check_auth():
    g.user = None
    access_token = request.cookies.get("accesstoken")
    session_token = request.cookies.get("sessiontoken")

    if access_token:
        try:
            data = jwt.decode(
                access_token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            g.user = data
            return
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

    if session_token:
        try:
            data = jwt.decode(
                session_token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            g.user = data
            g.needs_refresh = True
        except Exception:
            pass


@app.after_request
def refresh_token(response: Response):
    if getattr(g, "needs_refresh", False) and g.user:
        new_access = jwt.encode(
            {
                "id": g.user["id"],
                "username": g.user["username"],
                "role": g.user["role"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response.set_cookie("accesstoken", new_access, httponly=True)
    return response


app.register_blueprint(user_bp)
app.register_blueprint(donvi_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)

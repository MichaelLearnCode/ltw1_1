from flask import Blueprint, abort, render_template, g, redirect, request, url_for
from werkzeug.security import generate_password_hash
from database import get_db
from functools import wraps
from typing import Any
import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def require_role(*allowed_roles):
    """
    Decorator kiểm tra quyền.
    Ví dụ: @require_role('admin', 'collaborator')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user:
                return redirect(url_for("user.login"))
            if g.user.get("role") not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@admin_bp.route("/")
@require_role("collaborator", "admin")
def dashboard():
    return render_template("admin_base.html", user=g.user)


@admin_bp.route("/donvi1")
@require_role("collaborator", "admin")
def admin_donvi1():
    db = get_db()
    dvs1 = db.execute("SELECT * FROM don_vi_cap_1").fetchall()
    return render_template("admin_donvi1.html", dvs1=dvs1, user=g.user)


@admin_bp.route("/donvi2")
@require_role("collaborator", "admin")
def admin_donvi2():
    db = get_db()
    sql = """
        SELECT d2.*, d1.ten_don_vi as ten_dv1 
        FROM don_vi_cap_2 d2 
        JOIN don_vi_cap_1 d1 ON d2.don_vi_cap_1_id = d1.id
    """
    dvs2 = db.execute(sql).fetchall()
    return render_template("admin_donvi2.html", dvs2=dvs2, user=g.user)


@admin_bp.route("/donvi1/delete/<int:id>", methods=["POST"])
@require_role("collaborator", "admin")
def delete_donvi1(id):
    db = get_db()
    db.execute("DELETE FROM don_vi_cap_1 WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("admin.admin_donvi1"))


@admin_bp.route("/donvi2/delete/<int:id>", methods=["POST"])
@require_role("collaborator", "admin")
def delete_donvi2(id):
    db = get_db()
    db.execute("DELETE FROM don_vi_cap_2 WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("admin.admin_donvi2"))


@admin_bp.route("/donvi/create", methods=["GET", "POST"])
@require_role("collaborator", "admin")
def admin_taodonvi():
    db = get_db()

    if request.method == "POST":
        ten = request.form.get("ten")
        dia_diem = request.form.get("dia_diem")
        email = request.form.get("email")
        phone = request.form.get("phone")
        website = request.form.get("website")
        mo_ta = request.form.get("mo_ta")

        is_dv2 = request.form.get("is_dv2")
        dv1_id = request.form.get("dv1_id")

        image_url = None
        file_to_upload = request.files.get("image")

        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder="LTW1")
            image_url = upload_result.get("secure_url")

        if is_dv2:
            if not dv1_id:
                return "Vui lòng chọn Đơn vị cấp 1 cha."

            try:
                sql = """
                    INSERT INTO don_vi_cap_2 
                    (ten_don_vi, dia_diem, email, dien_thoai, website, mo_ta, don_vi_cap_1_id, image_url) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                db.execute(
                    sql,
                    (ten, dia_diem, email, phone, website, mo_ta, dv1_id, image_url),
                )
                db.commit()
                return redirect(url_for("admin.admin_donvi2"))
            except Exception as e:
                print(f"Error creating DV2: {e}")
                db.rollback()
                return "Lỗi khi tạo Đơn vị cấp 2."

        else:
            try:
                sql = """
                    INSERT INTO don_vi_cap_1 
                    (ten_don_vi, dia_diem, email, dien_thoai, website, mo_ta, image_url) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                db.execute(
                    sql, (ten, dia_diem, email, phone, website, mo_ta, image_url)
                )
                db.commit()
                return redirect(url_for("admin.admin_donvi1"))
            except Exception as e:
                print(f"Error creating DV1: {e}")
                db.rollback()
                return "Lỗi khi tạo Đơn vị cấp 1."

    dvs1 = db.execute("SELECT id, ten_don_vi FROM don_vi_cap_1").fetchall()
    return render_template("admin_taodonvi.html", dvs1=dvs1, user=g.user)


# Edit
@admin_bp.route("/donvi1/edit/<int:id>", methods=["GET", "POST"])
@require_role("collaborator", "admin")
def edit_donvi1(id):
    db = get_db()
    dv = db.execute("SELECT * FROM don_vi_cap_1 WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        ten = request.form.get("ten")
        dia_diem = request.form.get("dia_diem")
        email = request.form.get("email")
        phone = request.form.get("phone")
        website = request.form.get("website")
        mo_ta = request.form.get("mo_ta")

        image_url = dv["image_url"]
        file_to_upload = request.files.get("image")
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder="LTW1")
            image_url = upload_result.get("secure_url")

        db.execute(
            """
            UPDATE don_vi_cap_1 
            SET ten_don_vi=?, dia_diem=?, email=?, dien_thoai=?, website=?, mo_ta=?, image_url=?
            WHERE id=?
        """,
            (ten, dia_diem, email, phone, website, mo_ta, image_url, id),
        )
        db.commit()
        return redirect(url_for("admin.admin_donvi1"))

    return render_template("admin_suadonvi.html", dv=dv, is_dv2=False, user=g.user)


@admin_bp.route("/donvi2/edit/<int:id>", methods=["GET", "POST"])
@require_role("collaborator", "admin")
def edit_donvi2(id):
    db = get_db()
    dv = db.execute("SELECT * FROM don_vi_cap_2 WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        ten = request.form.get("ten")
        dia_diem = request.form.get("dia_diem")
        email = request.form.get("email")
        phone = request.form.get("phone")
        website = request.form.get("website")
        mo_ta = request.form.get("mo_ta")
        dv1_id = request.form.get("dv1_id")

        image_url = dv["image_url"]
        file_to_upload = request.files.get("image")
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload, folder="LTW1")
            image_url = upload_result.get("secure_url")

        db.execute(
            """
            UPDATE don_vi_cap_2 
            SET ten_don_vi=?, dia_diem=?, email=?, dien_thoai=?, website=?, mo_ta=?, image_url=?, don_vi_cap_1_id=?
            WHERE id=?
        """,
            (ten, dia_diem, email, phone, website, mo_ta, image_url, dv1_id, id),
        )
        db.commit()
        return redirect(url_for("admin.admin_donvi2"))

    dvs1 = db.execute("SELECT id, ten_don_vi FROM don_vi_cap_1").fetchall()
    return render_template(
        "admin_suadonvi.html", dv=dv, dvs1=dvs1, is_dv2=True, user=g.user
    )


@admin_bp.route("/users")
@require_role("admin")
def admin_user():
    db = get_db()
    users = db.execute("SELECT id, username, email, role FROM users").fetchall()
    return render_template("admin_user.html", users=users, user=g.user)


@admin_bp.route("/user/create", methods=["POST"])
@require_role("admin")
def create_user():
    db = get_db()
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    if not username or not password:
        return "Username và Password là bắt buộc", 400
    hashed_pw = generate_password_hash(password)

    try:
        db.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pw, role),
        )
        db.commit()
    except Exception as e:
        print(f"Lỗi thêm user: {e}")
        db.rollback()
        return "Tên tài khoản đã tồn tại", 400

    return redirect(url_for("admin.admin_user"))


@admin_bp.route("/user/edit", methods=["POST"])
@require_role("admin")
def edit_user():
    db = get_db()
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    if password:
        hashed_pw = generate_password_hash(password)
        sql = "UPDATE users SET username=?, email=?, password=?, role=? WHERE id=?"
        params = (username, email, hashed_pw, role, user_id)
    else:
        sql = "UPDATE users SET username=?, email=?, role=? WHERE id=?"
        params = (username, email, role, user_id)

    try:
        db.execute(sql, params)
        db.commit()
    except Exception as e:
        print(f"Lỗi sửa user: {e}")
        db.rollback()
        return "Lỗi cập nhật dữ liệu", 400

    return redirect(url_for("admin.admin_user"))


@admin_bp.route("/user/delete/<int:id>", methods=["POST"])
@require_role("admin")
def delete_user(id):
    db = get_db()
    if g.user["id"] == id:
        return "Bạn không thể tự xóa chính mình!", 400

    db.execute("DELETE FROM users WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("admin.admin_user"))

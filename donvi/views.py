from flask import Blueprint, redirect, render_template, request, jsonify, g, url_for
from database import get_db

donvi_bp = Blueprint("donvi", __name__)


@donvi_bp.route("/")
def index():
    if g.user and g.user.get("role") in ["admin", "collaborator"]:
        return redirect(url_for("admin.dashboard"))
    db = get_db()
    dvs1 = db.execute("SELECT * FROM don_vi_cap_1").fetchall()
    return render_template("index.html", dvs1=dvs1, user=g.user)


@donvi_bp.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])

    db = get_db()
    # Join tìm cả hai bảng
    sql = """
        SELECT id, ten_don_vi, 'donvi1' as type FROM don_vi_cap_1 WHERE ten_don_vi LIKE ?
        UNION
        SELECT id, ten_don_vi, 'donvi2' as type FROM don_vi_cap_2 WHERE ten_don_vi LIKE ?
        LIMIT 10
    """
    like_query = f"%{query}%"
    results = db.execute(sql, (like_query, like_query)).fetchall()
    return jsonify([dict(r) for r in results])


@donvi_bp.route("/donvi1/<int:id>")
def donvi1(id: int):
    db = get_db()
    dv1 = db.execute("SELECT * FROM don_vi_cap_1 WHERE id = ?", (id,)).fetchone()
    dvs2 = db.execute(
        "SELECT * FROM don_vi_cap_2 WHERE don_vi_cap_1_id = ?", (id,)
    ).fetchall()
    return render_template("donvi1.html", dv1=dv1, dvs2=dvs2, user=g.user)


@donvi_bp.route("/donvi2/<int:id>")
def donvi2(id: int):
    db = get_db()
    dv2 = db.execute("SELECT * FROM don_vi_cap_2 WHERE id = ?", (id,)).fetchone()
    if dv2:
        dv1 = db.execute(
            "SELECT * FROM don_vi_cap_1 WHERE id = ?", (dv2["don_vi_cap_1_id"],)
        ).fetchone()
    else:
        dv1 = None
    return render_template("donvi2.html", dv2=dv2, dv1=dv1, user=g.user)

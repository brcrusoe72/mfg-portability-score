"""Manufacturing Data Portability Score — Flask Web App."""

import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from portability_score.models import Base, Platform, Dimension, Score, UserReport
from portability_score.framework import DIMENSIONS, grade

app = Flask(__name__)

DB_PATH = "portability.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)


def get_platforms(session):
    return session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension)
    ).all()


# --- Web Routes ---

@app.route("/")
def index():
    session = Session()
    platforms = get_platforms(session)
    platforms.sort(key=lambda p: p.overall_score, reverse=True)
    dimensions = DIMENSIONS
    session.close()
    return render_template("index.html", platforms=platforms, dimensions=dimensions, grade=grade)


@app.route("/platform/<slug>")
def platform_detail(slug):
    session = Session()
    platform = session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension),
        joinedload(Platform.reports),
    ).filter_by(slug=slug).first_or_404()
    dimensions = DIMENSIONS
    session.close()
    return render_template("platform.html", platform=platform, dimensions=dimensions, grade=grade)


@app.route("/compare")
def compare():
    ids = request.args.get("ids", "")
    if not ids:
        session = Session()
        platforms = get_platforms(session)
        platforms.sort(key=lambda p: p.overall_score, reverse=True)
        session.close()
        return render_template("compare_select.html", platforms=platforms)

    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    session = Session()
    platforms = session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension)
    ).filter(Platform.id.in_(id_list)).all()
    dimensions = DIMENSIONS
    session.close()
    return render_template("compare.html", platforms=platforms, dimensions=dimensions, grade=grade)


@app.route("/submit", methods=["GET", "POST"])
def submit_report():
    session = Session()
    if request.method == "POST":
        report = UserReport(
            platform_id=int(request.form["platform_id"]),
            author_name=request.form.get("author_name", "").strip() or "Anonymous",
            author_role=request.form.get("author_role", "").strip(),
            experience=request.form["experience"],
            rating=int(request.form.get("rating", 3)),
        )
        session.add(report)
        session.commit()
        session.close()
        return redirect(url_for("index"))

    platforms = session.query(Platform).order_by(Platform.name).all()
    session.close()
    return render_template("submit.html", platforms=platforms)


# --- API Routes ---

@app.route("/api/platforms")
def api_platforms():
    session = Session()
    platforms = get_platforms(session)
    result = [p.to_dict() for p in platforms]
    session.close()
    return jsonify(result)


@app.route("/api/platforms/<int:pid>")
def api_platform_detail(pid):
    session = Session()
    platform = session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension)
    ).get(pid)
    if not platform:
        return jsonify({"error": "Not found"}), 404
    result = platform.to_dict(include_scores=True)
    session.close()
    return jsonify(result)


@app.route("/api/compare")
def api_compare():
    ids = request.args.get("ids", "")
    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    if not id_list:
        return jsonify({"error": "Provide ?ids=1,2,3"}), 400

    session = Session()
    platforms = session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension)
    ).filter(Platform.id.in_(id_list)).all()
    result = [p.to_dict(include_scores=True) for p in platforms]
    session.close()
    return jsonify(result)


@app.route("/api/reports", methods=["POST"])
def api_submit_report():
    data = request.get_json()
    if not data or "platform_id" not in data or "experience" not in data:
        return jsonify({"error": "platform_id and experience required"}), 400

    session = Session()
    report = UserReport(
        platform_id=data["platform_id"],
        author_name=data.get("author_name", "Anonymous"),
        author_role=data.get("author_role", ""),
        experience=data["experience"],
        rating=data.get("rating", 3),
    )
    session.add(report)
    session.commit()
    rid = report.id
    session.close()
    return jsonify({"id": rid, "status": "submitted"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

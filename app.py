"""Manufacturing Data Portability Score — Flask Web App."""

import json
from flask import Flask, abort, render_template, request, jsonify, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from portability_score.models import Base, Platform, Dimension, Score, UserReport
from portability_score.framework import DIMENSIONS, grade

app = Flask(__name__)

DB_PATH = "portability.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)

MAX_EXPERIENCE_LENGTH = 10_000


def get_platforms(session):
    return session.query(Platform).options(
        joinedload(Platform.scores).joinedload(Score.dimension)
    ).all()


def _integer_field(data, name, default=None):
    value = data.get(name, default)
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _text_field(data, name, max_length, *, required=False, default=""):
    value = data.get(name, default)
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{name} is required")
    if len(value) > max_length:
        raise ValueError(f"{name} must be at most {max_length} characters")
    return value


def build_user_report(data):
    """Validate untrusted form/JSON data before creating a report."""
    platform_id = _integer_field(data, "platform_id")
    if platform_id <= 0:
        raise ValueError("platform_id must be a positive integer")

    rating = _integer_field(data, "rating", 3)
    if not 1 <= rating <= 5:
        raise ValueError("rating must be between 1 and 5")

    return UserReport(
        platform_id=platform_id,
        author_name=_text_field(
            data, "author_name", 200, default="Anonymous"
        ) or "Anonymous",
        author_role=_text_field(data, "author_role", 200),
        experience=_text_field(
            data,
            "experience",
            MAX_EXPERIENCE_LENGTH,
            required=True,
        ),
        rating=rating,
    )


# --- Web Routes ---

@app.route("/")
def index():
    with Session() as session:
        platforms = get_platforms(session)
        platforms.sort(key=lambda p: p.overall_score, reverse=True)
        dimensions = DIMENSIONS
    return render_template("index.html", platforms=platforms, dimensions=dimensions, grade=grade)


@app.route("/platform/<slug>")
def platform_detail(slug):
    with Session() as session:
        platform = session.query(Platform).options(
            joinedload(Platform.scores).joinedload(Score.dimension),
            joinedload(Platform.reports),
        ).filter_by(slug=slug).first()
        if platform is None:
            abort(404)
        dimensions = DIMENSIONS
    return render_template("platform.html", platform=platform, dimensions=dimensions, grade=grade)


@app.route("/compare")
def compare():
    ids = request.args.get("ids", "")
    if not ids:
        with Session() as session:
            platforms = get_platforms(session)
            platforms.sort(key=lambda p: p.overall_score, reverse=True)
        return render_template("compare_select.html", platforms=platforms)

    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    with Session() as session:
        platforms = session.query(Platform).options(
            joinedload(Platform.scores).joinedload(Score.dimension)
        ).filter(Platform.id.in_(id_list)).all()
        dimensions = DIMENSIONS
    return render_template("compare.html", platforms=platforms, dimensions=dimensions, grade=grade)


@app.route("/submit", methods=["GET", "POST"])
def submit_report():
    if request.method == "POST":
        try:
            report = build_user_report(request.form)
        except ValueError as exc:
            abort(400, description=str(exc))
        with Session() as session:
            if session.get(Platform, report.platform_id) is None:
                abort(404, description="Platform not found")
            session.add(report)
            session.commit()
        return redirect(url_for("index"))

    with Session() as session:
        platforms = session.query(Platform).order_by(Platform.name).all()
    return render_template("submit.html", platforms=platforms)


# --- API Routes ---

@app.route("/api/platforms")
def api_platforms():
    with Session() as session:
        platforms = get_platforms(session)
        result = [p.to_dict() for p in platforms]
    return jsonify(result)


@app.route("/api/platforms/<int:pid>")
def api_platform_detail(pid):
    with Session() as session:
        platform = session.query(Platform).options(
            joinedload(Platform.scores).joinedload(Score.dimension)
        ).filter_by(id=pid).first()
        if not platform:
            return jsonify({"error": "Not found"}), 404
        result = platform.to_dict(include_scores=True)
    return jsonify(result)


@app.route("/api/compare")
def api_compare():
    ids = request.args.get("ids", "")
    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    if not id_list:
        return jsonify({"error": "Provide ?ids=1,2,3"}), 400

    with Session() as session:
        platforms = session.query(Platform).options(
            joinedload(Platform.scores).joinedload(Score.dimension)
        ).filter(Platform.id.in_(id_list)).all()
        result = [p.to_dict(include_scores=True) for p in platforms]
    return jsonify(result)


@app.route("/api/reports", methods=["POST"])
def api_submit_report():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400
    try:
        report = build_user_report(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    with Session() as session:
        if session.get(Platform, report.platform_id) is None:
            return jsonify({"error": "Platform not found"}), 404
        session.add(report)
        session.commit()
        rid = report.id
    return jsonify({"id": rid, "status": "submitted"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)


import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, g


BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["DATABASE"] = os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "instance" / "aceest.db")
    )

    if test_config:
        app.config.update(test_config)

    # Initialize database
    Path(app.config["DATABASE"]).parent.mkdir(
        parents=True, exist_ok=True
    )

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age > 0),
                weight REAL NOT NULL CHECK(weight > 0)
            )
        """)
        db.commit()

    with app.app_context():
        init_db()

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "application": "ACEest Fitness & Gym",
            "message": "Welcome to ACEest Fitness & Gym",
            "status": "running"
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"})

    @app.route("/clients", methods=["GET"])
    def get_clients():
        db = get_db()
        rows = db.execute(
            "SELECT id, name, age, weight FROM clients ORDER BY id"
        ).fetchall()

        clients = [dict(row) for row in rows]
        return jsonify(clients)

    @app.route("/clients", methods=["POST"])
    def add_client():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "A valid JSON request body is required"
            }), 400

        required_fields = ["name", "age", "weight"]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"{field} is required"
                }), 400

        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({
                "error": "Name must be a non-empty string"
            }), 400

        try:
            age = int(data["age"])
            weight = float(data["weight"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "Age must be an integer and weight must be numeric"
            }), 400

        if isinstance(data["age"], bool) or age <= 0:
            return jsonify({
                "error": "Age must be a positive integer"
            }), 400

        if weight <= 0:
            return jsonify({
                "error": "Weight must be greater than zero"
            }), 400

        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO clients (name, age, weight)
            VALUES (?, ?, ?)
            """,
            (name.strip(), age, weight)
        )
        db.commit()

        client = {
            "id": cursor.lastrowid,
            "name": name.strip(),
            "age": age,
            "weight": weight
        }

        return jsonify(client), 201

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

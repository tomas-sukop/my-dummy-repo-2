"""
Data pipeline web application.
Provides endpoints for ingesting, transforming, and querying pipeline data.
"""

import os
import sqlite3
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded credentials (vulnerability: secrets in source code)
DB_PASSWORD = "s3cr3tP@ssw0rd"
API_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

DATABASE = "pipeline.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value TEXT,
            owner TEXT
        )"""
    )
    conn.commit()
    conn.close()


@app.route("/records/search")
def search_records():
    """Search records by name — vulnerable to SQL injection."""
    name = request.args.get("name", "")
    conn = get_db()
    # SQL injection: user input concatenated directly into the query
    query = "SELECT * FROM records WHERE name = '" + name + "'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/records/search_owner")
def search_by_owner():
    """Search records by owner — also vulnerable to SQL injection."""
    owner = request.args.get("owner", "")
    conn = get_db()
    query = f"SELECT * FROM records WHERE owner = '{owner}'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/pipeline/run", methods=["POST"])
def run_pipeline():
    """Run a named pipeline script — vulnerable to command injection."""
    data = request.get_json()
    pipeline_name = data.get("pipeline", "")
    # Command injection: unsanitised input passed to shell
    result = subprocess.check_output(
        "python scripts/" + pipeline_name + ".py", shell=True
    )
    return jsonify({"output": result.decode()})


@app.route("/files/read")
def read_file():
    """Read a log file — vulnerable to path traversal."""
    filename = request.args.get("file", "")
    # Path traversal: no canonicalisation or prefix check
    path = os.path.join("logs", filename)
    with open(path) as f:
        content = f.read()
    return jsonify({"content": content})


@app.route("/records", methods=["POST"])
def create_record():
    """Insert a new record."""
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "INSERT INTO records (name, value, owner) VALUES (?, ?, ?)",
        (data["name"], data["value"], data["owner"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "created"}), 201


if __name__ == "__main__":
    init_db()
    # Debug mode enabled in production (vulnerability)
    app.run(debug=True, host="0.0.0.0", port=5000)

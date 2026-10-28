import os
import time

import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request

app = Flask(__name__)

# Database configuration from Docker Compose environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME", "three_tier_db"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", ""),
    "connection_timeout": 5,
}


def get_connection():
    """Create a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def query_with_retry(sql, params=None, fetch=False):
    """
    Execute a SQL statement with retry handling.

    fetch=True:
        Fetch and return rows as dictionaries.

    fetch=False:
        Drain any returned rows, commit the transaction,
        and return None. Useful for INSERT, UPDATE, and DELETE.
    """
    last_error = None

    for attempt in range(10):
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor(
                dictionary=True,
                buffered=True,
            )

            cursor.execute(sql, params or ())

            if fetch:
                return cursor.fetchall()

            # Consume results for statements that return rows,
            # including SELECT statements such as SELECT 1.
            if cursor.with_rows:
                cursor.fetchall()

            connection.commit()
            return None

        except Error as exc:
            last_error = exc

            # Retry after a short delay.
            if attempt < 9:
                time.sleep(2)

        finally:
            if cursor is not None:
                cursor.close()

            if connection is not None:
                connection.close()

    raise last_error


@app.get("/")
def root():
    """Basic backend status endpoint."""
    return jsonify(
        message="Three-tier application API",
        status="running",
    )


@app.get("/api/health")
def health():
    """Check whether the backend can communicate with MySQL."""
    try:
        query_with_retry("SELECT 1")
        return jsonify(
            backend="healthy",
            database="connected",
        ), 200

    except Error:
        app.logger.exception("Database health check failed")
        return jsonify(
            error="Database unavailable",
        ), 503


@app.get("/api/items")
def get_items():
    """Retrieve all items from the database."""
    try:
        items = query_with_retry(
            "SELECT id, name FROM items ORDER BY id DESC",
            fetch=True,
        )

        return jsonify(items=items), 200

    except Error:
        app.logger.exception("Unable to read items")
        return jsonify(
            error="Unable to read items",
        ), 503


@app.post("/api/items")
def create_item():
    """Validate and insert a new item."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify(
            error="A non-empty name is required",
        ), 400

    name = name.strip()

    if len(name) > 200:
        return jsonify(
            error="Name must be 200 characters or fewer",
        ), 400

    try:
        query_with_retry(
            "INSERT INTO items (name) VALUES (%s)",
            (name,),
        )

        return jsonify(
            message="Item created",
            name=name,
        ), 201

    except Error:
        app.logger.exception("Unable to save item")
        return jsonify(
            error="Unable to save item",
        ), 503

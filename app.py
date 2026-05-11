from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras

DEFAULT_DB_CONFIG = {
    "dbname": "library_db",
    "user": "postgres",
    "password": "secret",
    "host": "localhost",
    "port": 5432,
}

def create_app(db_config=None):
    app = Flask(__name__)
    config = db_config or DEFAULT_DB_CONFIG

    def get_conn():
        return psycopg2.connect(**config)

    # AUTHORS
    @app.route("/api/authors", methods=["POST"])
    def create_author():
        data = request.json
        if not data or not data.get("name"):
            return jsonify({"error": "field 'name' is required"}), 400
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("INSERT INTO authors (name, birth_year) VALUES (%s, %s) RETURNING *",
                    (data["name"], data.get("birth_year")))
        author = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(author), 201

    @app.route("/api/authors", methods=["GET"])
    def get_authors():
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM authors ORDER BY id")
        authors = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(authors), 200

    @app.route("/api/authors/<int:author_id>", methods=["GET"])
    def get_author(author_id):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM authors WHERE id=%s", (author_id,))
        author = cur.fetchone()
        cur.close()
        conn.close()
        if not author:
            return jsonify({"error": "Author not found"}), 404
        return jsonify(author), 200

    @app.route("/api/authors/<int:author_id>", methods=["DELETE"])
    def delete_author(author_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM authors WHERE id=%s", (author_id,))
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Author not found"}), 404
        conn.commit()
        cur.close()
        conn.close()
        return "", 204

    # BOOKS
    @app.route("/api/books", methods=["POST"])
    def create_book():
        data = request.json
        if not data or not data.get("title") or not data.get("created_by"):
            return jsonify({"error": "fields 'title' and 'created_by' are required"}), 400

        author_id = data.get("author_id")
        if author_id:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM authors WHERE id=%s", (author_id,))
            if not cur.fetchone():
                conn.close()
                return jsonify({"error": f"Author with id {author_id} not found"}), 400
            cur.close()
            conn.close()

        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""INSERT INTO books (title, genre, year_published, author_id, created_by)
                       VALUES (%s, %s, %s, %s, %s) RETURNING *""",
                    (data["title"], data.get("genre"), data.get("year_published"),
                     author_id, data["created_by"]))
        book = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(book), 201

    @app.route("/api/books", methods=["GET"])
    def get_books():
        genre = request.args.get("genre")
        author_id = request.args.get("author_id")
        q = request.args.get("q")

        query = "SELECT * FROM books WHERE TRUE"
        params = []
        if genre:
            query += " AND genre=%s"
            params.append(genre)
        if author_id:
            query += " AND author_id=%s"
            params.append(author_id)
        if q:
            query += " AND title ILIKE %s"
            params.append(f"%{q}%")

        query += " ORDER BY id"

        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, tuple(params))
        books = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(books), 200

    @app.route("/api/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM books WHERE id=%s", (book_id,))
        book = cur.fetchone()
        cur.close()
        conn.close()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(book), 200

    @app.route("/api/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
        if cur.rowcount == 0:
            conn.close()
            return jsonify({"error": "Book not found"}), 404
        conn.commit()
        cur.close()
        conn.close()
        return "", 204

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

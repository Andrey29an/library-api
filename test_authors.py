class TestAuthors:
    def test_get_authors_empty(self, client):
        response = client.get("/api/authors")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_author(self, client):
        response = client.post("/api/authors", json={"name": "Тарас Шевченко", "birth_year": 1814})
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Тарас Шевченко"
        assert data["birth_year"] == 1814
        assert "id" in data

    def test_create_author_without_name(self, client):
        response = client.post("/api/authors", json={})
        assert response.status_code == 400

    def test_get_author_by_id(self, client):
        author = client.post("/api/authors", json={"name": "Леся Українка"}).get_json()
        response = client.get(f"/api/authors/{author['id']}")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Леся Українка"

    def test_get_author_not_found(self, client):
        response = client.get("/api/authors/999")
        assert response.status_code == 404

    def test_delete_author(self, client):
        author = client.post("/api/authors", json={"name": "Іван Франко"}).get_json()
        response = client.delete(f"/api/authors/{author['id']}")
        assert response.status_code == 204

    def test_delete_author_not_found(self, client):
        response = client.delete("/api/authors/999")
        assert response.status_code == 404

class TestAuthorBooks:
    def test_get_author_books_empty(self, client):
        author = client.post("/api/authors", json={"name": "Леся Українка"}).get_json()
        response = client.get(f"/api/authors/{author['id']}/books")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_author_books_not_found(self, client):
        response = client.get("/api/authors/999/books")
        assert response.status_code == 404

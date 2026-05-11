class TestBooks:
    def test_get_books_empty(self, client):
        response = client.get("/api/books")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_book(self, client):
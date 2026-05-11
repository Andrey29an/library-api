class TestBooks:
    def test_get_books_empty(self, client):
        response = client.get("/api/books")
        assert response.status_code == 200
        assert response.get_json() == []


    def test_create_book_default_status(self, client):
        """Книга створюється зі статусом за замовчуванням"""
        response = client.post("/api/books", json={
            "title": "Test Book",
            "created_by": "Ім'я Прізвище",
        })
        assert response.status_code == 201
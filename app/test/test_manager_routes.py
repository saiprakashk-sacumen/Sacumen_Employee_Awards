def test_get_approved_managers(client):
    # Insert a sample manager
    db = next(app.dependency_overrides[get_db]())
    from app.models import User
    manager = User(email="manager@test.com", role="manager", is_approved=True)
    db.add(manager)
    db.commit()

    response = client.get("/managers/approved")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "manager@test.com"

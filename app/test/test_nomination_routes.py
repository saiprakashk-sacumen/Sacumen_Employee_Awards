def test_list_nominations(client):
    # Insert a sample nomination
    db = next(app.dependency_overrides[get_db]())
    from app.models import User, Nomination
    manager = User(email="manager@test.com", role="manager", is_approved=True)
    db.add(manager)
    db.commit()

    nomination = Nomination(title="Best Innovator", employee_id=1, manager_id=manager.id)
    db.add(nomination)
    db.commit()

    response = client.get("/nominations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Best Innovator"

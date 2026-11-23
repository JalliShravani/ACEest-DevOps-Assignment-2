
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    database_path = tmp_path / "test_aceest.db"

    test_app = create_app({
        "TESTING": True,
        "DATABASE": str(database_path)
    })

    with test_app.test_client() as test_client:
        yield test_client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["application"] == "ACEest Fitness & Gym"
    assert data["status"] == "running"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_get_clients_empty(client):
    response = client.get("/clients")

    assert response.status_code == 200
    assert response.get_json() == []


def test_add_client(client):
    client_data = {
        "name": "Test User",
        "age": 25,
        "weight": 60
    }

    response = client.post("/clients", json=client_data)

    assert response.status_code == 201

    data = response.get_json()

    assert data["name"] == "Test User"
    assert data["age"] == 25
    assert data["weight"] == 60
    assert "id" in data


def test_add_client_missing_field(client):
    client_data = {
        "name": "Test User",
        "age": 25
    }

    response = client.post("/clients", json=client_data)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_add_client_invalid_name(client):
    response = client.post("/clients", json={
        "name": " ",
        "age": 25,
        "weight": 60
    })

    assert response.status_code == 400


def test_add_client_invalid_age(client):
    response = client.post("/clients", json={
        "name": "Test User",
        "age": -5,
        "weight": 60
    })

    assert response.status_code == 400


def test_add_client_invalid_weight(client):
    response = client.post("/clients", json={
        "name": "Test User",
        "age": 25,
        "weight": 0
    })

    assert response.status_code == 400


def test_add_client_non_numeric_values(client):
    response = client.post("/clients", json={
        "name": "Test User",
        "age": "abc",
        "weight": "unknown"
    })

    assert response.status_code == 400


def test_client_persistence(client):
    client.post("/clients", json={
        "name": "Persistent User",
        "age": 28,
        "weight": 65
    })

    response = client.get("/clients")

    assert response.status_code == 200

    clients = response.get_json()

    assert len(clients) == 1
    assert clients[0]["name"] == "Persistent User"

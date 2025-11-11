import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from urllib.parse import quote

import src.app as appmod

client = TestClient(appmod.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Keep tests isolated by restoring the in-memory activities after each test
    backup = deepcopy(appmod.activities)
    yield
    appmod.activities.clear()
    appmod.activities.update(deepcopy(backup))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # A known activity should be present
    assert "Chess Club" in data


def test_signup_and_duplicate():
    email = "pytest_user@example.com"
    activity = "Chess Club"
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"

    r1 = client.post(path)
    assert r1.status_code == 200
    assert "Signed up" in r1.json().get("message", "")

    # second signup should fail with 400
    r2 = client.post(path)
    assert r2.status_code == 400


def test_unregister_participant():
    email = "to_remove@example.com"
    activity = "Programming Class"

    signup_path = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(signup_path)
    assert r.status_code == 200

    delete_path = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    rdel = client.delete(delete_path)
    assert rdel.status_code == 200
    assert "Removed" in rdel.json().get("message", "")

    # deleting again should return 404
    rdel2 = client.delete(delete_path)
    assert rdel2.status_code == 404

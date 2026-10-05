from app import routes


def fake_workout(**kwargs):

    return (
        "DAY 1\n"
        "Warm-up: 5 minutes\n"
        "Main: Squats 3x10\n"
        "Cooldown: 5 minutes\n\n"
        "DAY 2\n"
        "Recovery walk."
    )


def fake_tip(**kwargs):

    return (
        "Stay hydrated and include a balanced meal "
        "with protein and carbohydrates after training."
    )


def fake_update(**kwargs):

    return (
        "UPDATED DAY 1\n"
        "Reduced volume based on feedback.\n\n"
        "DAY 2\n"
        "Easy cardio and mobility."
    )


def test_health():

    from .conftest import client

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home_page():

    from .conftest import client

    response = client.get("/")

    assert response.status_code == 200

    assert "Create your plan" in response.text


def test_create_plan_api(
    monkeypatch,
):

    from .conftest import client

    monkeypatch.setattr(
        routes,
        "generate_workout_gemini",
        fake_workout,
    )

    monkeypatch.setattr(
        routes,
        "generate_nutrition_tip_with_flash",
        fake_tip,
    )

    payload = {
        "user_id": "TEST001",
        "name": "Test User",
        "age": 25,
        "weight": 70,
        "goal": "muscle gain",
        "intensity": "medium",
    }

    response = client.post(
        "/api/plans",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == "TEST001"

    assert "DAY 1" in data["original_plan"]


def test_feedback_update(
    monkeypatch,
):

    from .conftest import client

    monkeypatch.setattr(
        routes,
        "update_workout_plan",
        fake_update,
    )

    response = client.post(
        "/api/plans/TEST001/feedback",
        json={
            "feedback":
                "Make the plan easier."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "updated_plan"
    ].startswith("UPDATED")

    assert data[
        "feedback"
    ] == "Make the plan easier."


def test_admin_page():

    from .conftest import client

    response = client.get(
        "/view-all-users"
    )

    assert response.status_code == 200

    assert "Test User" in response.text
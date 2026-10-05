from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=50,
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: str = Field(
        min_length=2,
        max_length=100,
    )

    intensity: str = Field(
        min_length=3,
        max_length=20,
    )

    @field_validator(
        "user_id",
        "name",
        "goal",
        "intensity",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value


class FeedbackRequest(BaseModel):

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )

    @field_validator("feedback")
    @classmethod
    def strip_feedback(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Feedback cannot be empty."
            )

        return value


class PlanResponse(BaseModel):

    user_id: str
    name: str
    age: int
    weight: float
    goal: str
    intensity: str
    original_plan: str
    updated_plan: str | None
    nutrition_tip: str
    feedback: str | None

    model_config = {
        "from_attributes": True
    }


class HealthResponse(BaseModel):

    status: str
    service: str
from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .database import (
    get_all_users,
    get_db,
    get_user,
    save_user,
    update_plan,
)

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .schemas import (
    FeedbackRequest,
    HealthResponse,
    PlanResponse,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


def ctx(request: Request, **kwargs):
    return {
        "request": request,
        **kwargs,
    }


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=ctx(
            request,
            error=None,
        ),
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout_form(
    request: Request,

    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        if get_user(db, data.user_id):

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context=ctx(
                    request,
                    error=(
                        f"User ID '{data.user_id}' already exists. "
                        "Use a different User ID."
                    ),
                ),
                status_code=409,
            )

        workout_plan = generate_workout_gemini(
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                goal=data.goal,
                intensity=data.intensity,
            )
        )

        user = save_user(
            db,

            user_id=data.user_id,
            name=data.name,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,

            original_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context=ctx(
                request,
                user=user,
                current_plan=user.original_plan,
                is_updated=False,
                message=None,
                error=None,
            ),
        )

    except (
        ValidationError,
        ValueError,
    ) as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=ctx(
                request,
                error=str(exc),
            ),
            status_code=422,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=ctx(
                request,
                error=f"AI generation failed: {exc}",
            ),
            status_code=500,
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback_form(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        user_id,
    )

    if not user:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=ctx(
                request,
                error=(
                    f"No user found with User ID "
                    f"'{user_id}'."
                ),
            ),
            status_code=404,
        )

    try:

        data = FeedbackRequest(
            feedback=feedback,
        )

        current_plan = (
            user.updated_plan
            or user.original_plan
        )

        revised_plan = update_workout_plan(
            original_plan=current_plan,
            feedback=data.feedback,
        )

        update_plan(
            db,
            user,
            revised_plan,
            data.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context=ctx(
                request,
                user=user,
                current_plan=revised_plan,
                is_updated=True,
                message=(
                    "Your workout plan has "
                    "been updated successfully."
                ),
                error=None,
            ),
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context=ctx(
                request,
                user=user,
                current_plan=(
                    user.updated_plan
                    or user.original_plan
                ),
                is_updated=bool(
                    user.updated_plan
                ),
                message=None,
                error=(
                    f"Could not update the plan: "
                    f"{exc}"
                ),
            ),
            status_code=500,
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context=ctx(
            request,
            users=get_all_users(db),
        ),
    )


# -----------------------------
# REST API
# -----------------------------

@router.get(
    "/api/health",
    response_model=HealthResponse,
)
def health():

    return {
        "status": "ok",
        "service": "FitBuddy API",
    }


@router.post(
    "/api/plans",
    response_model=PlanResponse,
    status_code=201,
)
def create_plan_api(
    payload: UserInput,
    db: Session = Depends(get_db),
):

    if get_user(
        db,
        payload.user_id,
    ):

        raise HTTPException(
            status_code=409,
            detail="User ID already exists.",
        )

    try:

        workout_plan = generate_workout_gemini(
            name=payload.name,
            age=payload.age,
            weight=payload.weight,
            goal=payload.goal,
            intensity=payload.intensity,
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                goal=payload.goal,
                intensity=payload.intensity,
            )
        )

        user = save_user(
            db,

            user_id=payload.user_id,
            name=payload.name,
            age=payload.age,
            weight=payload.weight,
            goal=payload.goal,
            intensity=payload.intensity,

            original_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        return PlanResponse.model_validate(
            user
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get(
    "/api/plans",
    response_model=list[PlanResponse],
)
def list_plans_api(
    db: Session = Depends(get_db),
):

    return [
        PlanResponse.model_validate(user)
        for user in get_all_users(db)
    ]


@router.get(
    "/api/plans/{user_id}",
    response_model=PlanResponse,
)
def get_plan_api(
    user_id: str,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return PlanResponse.model_validate(
        user
    )


@router.post(
    "/api/plans/{user_id}/feedback",
    response_model=PlanResponse,
)
def update_plan_api(
    user_id: str,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    try:

        current_plan = (
            user.updated_plan
            or user.original_plan
        )

        revised_plan = update_workout_plan(
            original_plan=current_plan,
            feedback=payload.feedback,
        )

        update_plan(
            db,
            user,
            revised_plan,
            payload.feedback,
        )

        return PlanResponse.model_validate(
            user
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
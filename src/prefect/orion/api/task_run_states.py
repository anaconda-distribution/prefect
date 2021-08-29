from typing import List
from uuid import UUID

import sqlalchemy as sa
from fastapi import Body, Depends, HTTPException, Path

from prefect.orion import models, schemas
from prefect.orion.api import dependencies
from prefect.orion.utilities.server import OrionRouter

router = OrionRouter(prefix="/task_run_states", tags=["Task Run States"])


@router.post("/")
async def create_task_run_state(
    task_run_id: UUID = Body(...),
    state: schemas.actions.StateCreate = Body(...),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.states.State:
    """
    Create a task run state, disregarding orchestration logic
    """
    return await models.task_run_states.create_task_run_state(
        session=session,
        state=state,
        task_run_id=task_run_id,
        apply_orchestration_rules=False,
    )


@router.get("/{id}")
async def read_task_run_state(
    task_run_state_id: UUID = Path(
        ..., description="The task run state id", alias="id"
    ),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.states.State:
    """
    Get a task run state by id
    """
    task_run_state = await models.task_run_states.read_task_run_state(
        session=session, task_run_state_id=task_run_state_id
    )
    if not task_run_state:
        raise HTTPException(status_code=404, detail="Flow run state not found")
    return task_run_state


@router.get("/")
async def read_task_run_states(
    task_run_id: UUID,
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> List[schemas.states.State]:
    """
    Get states associated with a task run
    """
    return await models.task_run_states.read_task_run_states(
        session=session, task_run_id=task_run_id
    )

"""
REST API router for Workflow Triggers and Webhook Engine.
Exposes CRUD operations for trigger rules, execution logs, and event trigger dispatches.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.core.domain.models import (
    WorkflowTriggerCreate,
    WorkflowTriggerUpdate,
    WorkflowTriggerResponse,
    WorkflowLogResponse,
    WorkflowEventTriggerRequest,
)
from src.infrastructure.repositories.workflows import create_workflow_trigger, list_workflow_triggers, get_workflow_trigger, update_workflow_trigger, delete_workflow_trigger, list_workflow_logs
from src.domain.workflow_engine import WorkflowEngine
from src.infrastructure.webhook_dispatcher import WebhookDispatcher

router = APIRouter(tags=["workflows"])


@router.post("/api/v1/workflows/triggers", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@router.post("/api/workflows/triggers", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_trigger_endpoint(req: WorkflowTriggerCreate):
    """Create a new workflow trigger rule."""
    is_act = req.is_active if req.is_active is not None else True
    trigger = create_workflow_trigger(
        name=req.name,
        event_type=req.event_type,
        webhook_url=req.webhook_url,
        condition_pattern=req.condition_pattern or "",
        secret_header=req.secret_header or "",
        is_active=is_act,
    )
    return trigger


@router.get("/api/v1/workflows/triggers", response_model=List[Dict[str, Any]])
@router.get("/api/workflows/triggers", response_model=List[Dict[str, Any]])
def list_triggers_endpoint(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    active_only: bool = Query(False, description="Filter active triggers only"),
):
    """List all registered workflow triggers."""
    triggers = list_workflow_triggers(event_type=event_type, active_only=active_only)
    return triggers


@router.get("/api/v1/workflows/triggers/{trigger_id}", response_model=Dict[str, Any])
@router.get("/api/workflows/triggers/{trigger_id}", response_model=Dict[str, Any])
def get_trigger_endpoint(trigger_id: int):
    """Get a single workflow trigger by ID."""
    trigger = get_workflow_trigger(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")
    return trigger


@router.put("/api/v1/workflows/triggers/{trigger_id}", response_model=Dict[str, Any])
@router.put("/api/workflows/triggers/{trigger_id}", response_model=Dict[str, Any])
def update_trigger_endpoint(trigger_id: int, trigger_update: WorkflowTriggerUpdate):
    """Update a workflow trigger rule.
    ponytail: Returns Dict[str, Any] like the other endpoints in this file.
    """
    updated_trigger = update_workflow_trigger(trigger_id, trigger_update)
    if not updated_trigger:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")
    return updated_trigger


@router.delete("/api/v1/workflows/triggers/{trigger_id}")
@router.delete("/api/workflows/triggers/{trigger_id}")
def delete_trigger_endpoint(trigger_id: int):
    """Delete a workflow trigger rule."""
    success = delete_workflow_trigger(trigger_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow trigger not found")
    return {"status": "deleted", "trigger_id": trigger_id, "id": trigger_id}


@router.post("/api/v1/workflows/trigger-event")
@router.post("/api/workflows/trigger-event")
@router.post("/api/workflows/test")
@router.post("/api/v1/workflows/test")
def trigger_event_endpoint(req: WorkflowEventTriggerRequest):
    """Dispatch event or trigger test webhook execution."""
    if req.trigger_id is not None:
        trigger = get_workflow_trigger(req.trigger_id)
        if not trigger:
            raise HTTPException(status_code=404, detail="Workflow trigger not found")
        event_type = req.event_type or trigger.get("event_type", "test_event")
        payload = req.payload or {"message": "Test webhook payload", "trigger_id": req.trigger_id}
        res = WebhookDispatcher.dispatch_sync(
            trigger_id=trigger["id"],
            webhook_url=trigger["webhook_url"],
            payload=payload,
            secret_header=trigger.get("secret_header", ""),
            event_type=event_type
        )
        return {
            "status": "dispatched",
            "log_id": res.get("log_id"),
            "matching_triggers": 1,
            "results": [res]
        }
    
    event_type = req.event_type or "test_event"
    payload = req.payload or {"message": "Test event payload"}
    results = WorkflowEngine.process_event(event_type=event_type, payload=payload, sync_dispatch=True)
    log_id = results[0].get("log_id") if results and "log_id" in results[0] else None
    return {
        "status": "dispatched",
        "log_id": log_id,
        "matching_triggers": len(results),
        "results": results
    }


@router.get("/api/v1/workflows/logs", response_model=List[Dict[str, Any]])
@router.get("/api/workflows/logs", response_model=List[Dict[str, Any]])
def list_logs_endpoint(
    trigger_id: Optional[int] = Query(None, description="Filter logs by trigger ID"),
    limit: int = Query(100, description="Max logs limit"),
):
    """Retrieve execution logs for workflow trigger dispatches."""
    logs = list_workflow_logs(trigger_id=trigger_id, limit=limit)
    return logs

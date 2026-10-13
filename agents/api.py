"""FastAPI interface for legacy supervisory audits and deterministic fibrosis scores."""
import hmac
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from nafld_mash_fibrosis_agent.fibrosis import assess_fibrosis
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor


supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="MASLD Fibrosis Calculator and Legacy Audit API",
    description="Deterministic FIB-4/NFS calculation; separate legacy generic audit endpoints.",
    version="2.1.0",
)


class FibrosisRequest(BaseModel):
    age: float = Field(..., description="Completed years (18–120)")
    ast: float = Field(..., description="AST in U/L")
    alt: float = Field(..., description="ALT in U/L")
    platelets: float = Field(..., description="Platelets in 10^9/L")
    bmi: Optional[float] = Field(default=None, description="BMI in kg/m^2 (NFS)")
    albumin: Optional[float] = Field(default=None, description="Albumin in g/dL (NFS)")
    impaired_fasting_glucose_or_diabetes: Optional[bool] = None


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "nafld-mash-fibrosis-agent", "version": "2.1.0"}


@app.post("/api/fibrosis")
def api_fibrosis(payload: FibrosisRequest):
    try:
        return assess_fibrosis(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/metrics")
def metrics():
    return {
        "legacy_dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException:
        raise HTTPException(status_code=422, detail="Rejected potentially sensitive identifier") from None


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Rejected potentially sensitive input") from None


@app.get("/api/audit/logs")
def api_audit_logs(authorization: Optional[str] = Header(default=None)):
    """Protect audit metadata; the separate token must be set explicitly."""
    expected = os.getenv("AUDIT_LOG_READ_TOKEN")
    candidate = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected or len(expected) < 24 or not hmac.compare_digest(candidate, expected):
        raise HTTPException(status_code=403, detail="Audit metadata unavailable")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}

"""
Pydantic v2 schemas and data definitions for Nafld Mash Fibrosis Agent.
Domain: Gastroenterology & Hepatology Systems
Standard: AASLD / ACG / Chicago Classification v4.0
"""
import datetime
import math
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


def _validate_finite_float(v: float, field_name: str) -> float:
    """Ensure metric values are finite (not NaN or Inf)."""
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"{field_name} must be a finite number, got {v}")
    return v


def _validate_identifier(v: str, field_name: str) -> str:
    """Validate string identifiers for length and basic safety."""
    if not v or not v.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace")
    if len(v) > 256:
        raise ValueError(f"{field_name} exceeds maximum length of 256 characters")
    return v.strip()


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier")
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target")
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        return _validate_identifier(v, "task_id")

    @field_validator("target_identifier")
    @classmethod
    def validate_target_identifier(cls, v: str) -> str:
        return _validate_identifier(v, "target_identifier")

    @field_validator("primary_metric")
    @classmethod
    def validate_primary_metric(cls, v: float) -> float:
        return _validate_finite_float(v, "primary_metric")

    @field_validator("secondary_metric")
    @classmethod
    def validate_secondary_metric(cls, v: float) -> float:
        return _validate_finite_float(v, "secondary_metric")

    @field_validator("status_descriptor")
    @classmethod
    def validate_status_descriptor(cls, v: str) -> str:
        return _validate_identifier(v, "status_descriptor")


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "AASLD / ACG / Chicago Classification v4.0"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "nafld-mash-fibrosis-agent"
    domain: str = "Gastroenterology & Hepatology Systems"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "AASLD / ACG / Chicago Classification v4.0"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

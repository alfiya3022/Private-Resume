import time
import uuid
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional

logger = logging.getLogger("Verity.diagnostics")


class ProcessingDiagnostics:
    """Collects and reports timing, stage progression, and errors for resume processing

    without logging PII or sensitive candidate data.
    """

    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or f"proc-{uuid.uuid4().hex[:8]}"
        self.stages: Dict[str, Dict[str, Any]] = {}
        self.start_time = time.perf_counter()
        self.errors: list[Dict[str, Any]] = []

    @contextmanager
    def track_stage(self, stage_name: str, **metadata):
        """Context manager to measure and log a processing stage."""
        stage_start = time.perf_counter()
        status = "SUCCESS"
        error_info = None
        try:
            yield
        except Exception as exc:
            status = "FAILED"
            error_info = {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            self.errors.append({
                "stage": stage_name,
                **error_info,
            })
            raise exc
        finally:
            duration_ms = round((time.perf_counter() - stage_start) * 1000, 2)
            stage_record = {
                "duration_ms": duration_ms,
                "status": status,
                **metadata,
            }
            if error_info:
                stage_record["error"] = error_info
            self.stages[stage_name] = stage_record
            logger.info(
                f"[{self.correlation_id}] [{stage_name}] status={status} duration={duration_ms}ms metadata={metadata}"
            )

    def log_ollama_call(
        self,
        operation: str,
        model: str,
        duration_ms: float,
        input_chars: int,
        output_chars: int,
        success: bool,
        error_category: Optional[str] = None,
        retries: int = 0,
    ):
        """Logs structured diagnostic details for an Ollama invocation."""
        record = {
            "operation": operation,
            "model": model,
            "duration_ms": round(duration_ms, 2),
            "input_chars": input_chars,
            "output_chars": output_chars,
            "success": success,
            "error_category": error_category,
            "retries": retries,
        }
        level = logging.INFO if success else logging.WARNING
        logger.log(
            level,
            f"[{self.correlation_id}] [Ollama] op={operation} model={model} duration={record['duration_ms']}ms "
            f"chars={input_chars}->{output_chars} success={success} error={error_category}",
        )
        return record

    def get_summary(self) -> Dict[str, Any]:
        """Returns the complete diagnostic profile."""
        total_duration_ms = round((time.perf_counter() - self.start_time) * 1000, 2)
        return {
            "correlation_id": self.correlation_id,
            "total_duration_ms": total_duration_ms,
            "stages": self.stages,
            "errors": self.errors,
            "error_count": len(self.errors),
        }

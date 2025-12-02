import logging
from typing import Optional

try:
    # optional imports; instrumentation is best-effort
    from opencensus.ext.fastapi import FastAPIInstrumentor
    from opencensus.ext.azure.trace_exporter import AzureExporter
except Exception:
    FastAPIInstrumentor = None
    AzureExporter = None

logger = logging.getLogger("telemetry")


def init_telemetry(app, instrumentation_key: Optional[str]):
    """
    Initialize Application Insights telemetry (traces/requests). If the
    instrumentation_key is missing, this is a no-op.
    """
    if not instrumentation_key:
        logger.warning("No APPINSIGHTS key found; telemetry is disabled.")
        return

    if FastAPIInstrumentor is None or AzureExporter is None:
        logger.warning("opencensus packages not available; telemetry not initialized.")
        return

    try:
        exporter = AzureExporter(instrumentation_key=instrumentation_key)
        FastAPIInstrumentor.instrument_app(app, exporter=exporter)
        logger.info("Telemetry initialized for Application Insights")
    except Exception as e:
        logger.exception("Failed to initialize telemetry: %s", e)

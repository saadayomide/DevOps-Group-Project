"""Prometheus metrics for the Product Comparison API.

Defines counters and histograms used by the refresh flow and scheduler.
"""

from prometheus_client import Counter, Histogram

# Counters
REFRESH_RUNS_TOTAL = Counter("refresh_runs_total", "Total shopping list refresh runs")
REFRESH_ERRORS_TOTAL = Counter("refresh_errors_total", "Errors during refresh runs")
OFFERS_SCANNED_TOTAL = Counter("offers_scanned_total", "Offers scanned by matching engine")
BEST_SELECTED_TOTAL = Counter("best_selected_total", "Times a best offer was selected")

# Histograms
REFRESH_DURATION_SECONDS = Histogram(
    "refresh_duration_seconds", "Duration of a shopping list refresh run"
)

# Monitoring & Application Insights Setup

## Application Insights Configuration

### 1. Connect Application Insights to App Service

1. **Create Application Insights Resource** (if not already created):
   - Azure Portal → Create Resource → Application Insights
   - Select your subscription and resource group
   - Name: `shopsmart-insights`
   - Application Type: `General`
   - Region: Same as your App Service

2. **Link to App Service**:
   - Navigate to your App Service (`shopsmart-backend-staging`)
   - Settings → Application Insights → Enable
   - Select the Application Insights resource created above
   - Click "Apply"

3. **Set Instrumentation Key**:
   - Copy the Instrumentation Key from Application Insights resource
   - Add to App Service Configuration:
     - Settings → Configuration → Application Settings
     - Add: `APPINSIGHTS_INSTRUMENTATION_KEY` = `<your-key>`
   - Or set via environment variable in deployment

### 2. Custom Properties Logged

The `/compare` endpoint logs the following custom properties (see `api/app/routes/compare.py`):

- `items_requested`: Number of items in the request
- `items_matched`: Number of items successfully matched to products
- `items_unmatched`: Number of items not found in database
- `stores_count`: Number of stores requested

These properties are logged via structured logging and appear in Application Insights as custom dimensions.

### 3. Structured Logging

All requests are logged with structured payloads via `LoggingMiddleware`:

```python
{
    "endpoint": "/api/v1/compare",
    "method": "POST",
    "status": 200,
    "duration_ms": 45.23,
    "error": null  # Only present if status >= 400
}
```

## Azure Portal Dashboard Setup

### 1. Create Dashboard

1. Azure Portal → Dashboards → New dashboard
2. Name: "ShopSmart Monitoring Dashboard"

### 2. Pin Metrics

Add the following metrics from your App Service:

#### Request Count
- Metric: `Requests`
- Aggregation: `Count`
- Time Range: Last 24 hours
- Pin to dashboard

#### p95 Latency
- Metric: `ResponseTime`
- Aggregation: `95th percentile`
- Time Range: Last 24 hours
- Pin to dashboard

#### Failure Rate
- Metric: `Http5xx`
- Aggregation: `Count`
- Time Range: Last 24 hours
- Create calculation: `Http5xx / Requests * 100` (percentage)
- Pin to dashboard

### 3. Application Insights Queries

Add Application Insights query tiles:

#### Custom Properties Query
```kusto
requests
| where name == "POST /api/v1/compare"
| extend items_requested = toint(customDimensions.items_requested)
| extend items_matched = toint(customDimensions.items_matched)
| extend items_unmatched = toint(customDimensions.items_unmatched)
| summarize
    avg_items_requested = avg(items_requested),
    avg_items_matched = avg(items_matched),
    avg_items_unmatched = avg(items_unmatched)
    by bin(timestamp, 1h)
| render timechart
```

#### Latency Distribution
```kusto
requests
| where name == "POST /api/v1/compare"
| summarize
    p50 = percentile(duration, 50),
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99)
    by bin(timestamp, 1h)
| render timechart
```

## Availability Test Setup

### 1. Create Availability Test

1. Application Insights → Availability → Add test
2. Test Name: `ShopSmart Health Check`
3. Test Type: `URL ping test`
4. URL: `https://shopsmart-backend-staging.azurewebsites.net/health`
5. Success Criteria: HTTP status code = 200, Response contains "ok"
6. Test Frequency: Every 5 minutes
7. Test Locations: Select 3-5 Azure regions
8. Enable Alert: Yes
9. Alert if: < 99% availability over 5 minutes

### 2. Alert Rules

Create alert rules for:

- **Availability < 99%**: Alert when availability drops below 99%
- **p95 Latency > 500ms**: Alert when p95 latency exceeds 500ms
- **Error Rate > 1%**: Alert when error rate exceeds 1%

### 3. Action Groups

Configure action groups to:
- Send email notifications to team
- Send SMS for critical alerts
- Trigger webhooks for integration with Slack/Teams

## Log Queries for Troubleshooting

### High Unmatched Items
```kusto
requests
| where name == "POST /api/v1/compare"
| extend unmatched = toint(customDimensions.items_unmatched)
| where unmatched > 0
| project timestamp, url, unmatched, customDimensions
| order by timestamp desc
```

### Slow Requests
```kusto
requests
| where name == "POST /api/v1/compare"
| where duration > 1000  // > 1 second
| project timestamp, duration, url, resultCode
| order by duration desc
```

### Error Analysis
```kusto
requests
| where resultCode >= 400
| summarize count() by resultCode, name
| order by count_ desc
```

## SLO Tracking

See `docs/SLO.md` for Service Level Objectives definition and tracking.

## References

- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Availability Tests](https://docs.microsoft.com/azure/azure-monitor/app/monitor-web-app-availability)
- [Kusto Query Language](https://docs.microsoft.com/azure/data-explorer/kusto/query/)

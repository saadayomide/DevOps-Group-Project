# Service Level Objectives (SLO)

## Definition

**ShopSmart's `/compare` endpoint maintains:**
- **p95 latency < 500ms** for our dataset (10 products × 3 stores = 30 price records)
- **99% availability** during demo week

## Measurement Period

- **Demo Week**: [Specify dates]
- **Measurement Window**: Rolling 24-hour window
- **Target**: Maintain SLO for 95% of measurement windows

## Metrics

### Latency (p95)

- **Metric**: `ResponseTime` (95th percentile)
- **Source**: Application Insights → App Service metrics
- **Query**:
  ```kusto
  requests
  | where name == "POST /api/v1/compare"
  | summarize p95 = percentile(duration, 95) by bin(timestamp, 1h)
  | where p95 > 500  // Violations
  ```

- **Target**: p95 < 500ms
- **Violation**: p95 >= 500ms for any 1-hour window

### Availability

- **Metric**: Availability percentage
- **Source**: Application Insights Availability Tests
- **Test**: `/health` endpoint ping every 5 minutes from 3+ regions
- **Calculation**: `(Successful requests / Total requests) * 100`

- **Target**: >= 99%
- **Violation**: < 99% availability over any 5-minute window

## Tracking

### Dashboard Queries

#### Current SLO Status
```kusto
// p95 Latency Status
requests
| where name == "POST /api/v1/compare"
| where timestamp > ago(24h)
| summarize
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99),
    count = count()
| extend status = iff(p95 < 500, "✅ PASS", "❌ FAIL")
| project status, p95, p99, count
```

#### Availability Status
```kusto
availabilityResults
| where name == "ShopSmart Health Check"
| where timestamp > ago(24h)
| summarize
    total = count(),
    success = countif(success == true),
    availability = (countif(success == true) * 100.0 / count())
| extend status = iff(availability >= 99, "✅ PASS", "❌ FAIL")
| project status, availability, total, success
```

### Weekly SLO Report

Track the following weekly:

1. **p95 Latency Compliance**
   - Hours meeting target: X / 168 (hours in week)
   - Compliance rate: (X / 168) * 100%

2. **Availability Compliance**
   - 5-minute windows meeting target: X / 2016 (windows in week)
   - Compliance rate: (X / 2016) * 100%

3. **Overall SLO Compliance**
   - Combined: Both metrics must pass for SLO to be met
   - Target: 95% of measurement windows meet both criteria

## Alerting

### Alert Rules

1. **p95 Latency Violation**
   - Condition: p95 latency > 500ms for 15 minutes
   - Severity: Warning
   - Action: Notify team via email

2. **Availability Violation**
   - Condition: Availability < 99% for 5 minutes
   - Severity: Critical
   - Action: Notify team via email + SMS

3. **SLO At Risk**
   - Condition: p95 > 450ms OR availability < 99.5% for 1 hour
   - Severity: Warning
   - Action: Notify team via email

## Remediation

### If p95 Latency Violated

1. Check Application Insights for slow requests
2. Review database query performance
3. Check for resource constraints (CPU, memory)
4. Consider:
   - Database query optimization
   - Caching frequently accessed data
   - Scaling up App Service plan

### If Availability Violated

1. Check Application Insights availability test results
2. Review error logs for 5xx errors
3. Check App Service health status
4. Consider:
   - Restart App Service
   - Check database connectivity
   - Review recent deployments

## Historical Tracking

### Week 1 (Demo Week)
- **p95 Latency**: [Track daily]
- **Availability**: [Track daily]
- **SLO Compliance**: [Calculate]

### Post-Demo
- Continue tracking for production readiness
- Adjust targets based on actual usage patterns
- Document any SLO violations and root causes

## Notes

- SLO targets are conservative for demo week (small dataset)
- Production targets may need adjustment based on:
  - Dataset size growth
  - Concurrent user load
  - Geographic distribution
- Regular review and adjustment of SLO targets is recommended

# High Memory Usage Runbook

## Symptoms

High memory usage means that the node is close to exhausting available memory. This may cause slowdowns, crashes, restarts, or unstable service behavior.

## Common Causes

- Memory leak
- Large data processing job
- Too many active sessions
- Inefficient caching
- Misconfigured service
- Long-running process consuming memory

## Recommended Checks

1. Check memory usage trend for the affected node.
2. Check whether memory usage is increasing over time.
3. Compare memory usage with CPU usage.
4. Review recent deployments or configuration changes.
5. Inspect logs for out-of-memory warnings.
6. Restart only if operationally safe and approved.

## Escalation

Escalate if memory usage continues increasing or if the node restarts unexpectedly.

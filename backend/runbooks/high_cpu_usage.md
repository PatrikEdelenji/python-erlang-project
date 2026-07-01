# High CPU Usage Runbook

## Symptoms

High CPU usage means that the node is under heavy processing load. This can cause latency, dropped packets, delayed metric reporting, and unstable behavior.

## Common Causes

- Too many requests
- Expensive background process
- Infinite loop or inefficient code
- Traffic spike
- Misconfigured service
- Resource leak

## Recommended Checks

1. Check recent CPU usage for the affected node.
2. Compare CPU usage with memory usage.
3. Check whether high CPU started suddenly or gradually.
4. Check whether high CPU correlates with high latency.
5. Review recent deployments.
6. Inspect running processes on the node.

## Escalation

Escalate if CPU remains above the threshold for more than 10 minutes or causes other alerts such as high latency or packet loss.

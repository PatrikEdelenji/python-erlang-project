# High Latency Runbook

## Symptoms

High latency means that a network node is responding slower than expected. Users may experience delayed responses, slow application performance, or unstable service quality.

## Common Causes

- Network congestion
- Routing issues
- Overloaded node CPU
- Misconfigured network paths
- External service dependency slowdown
- Packet retransmissions

## Recommended Checks

1. Check recent latency metrics for the affected node.
2. Compare the node latency with other nodes in the same region.
3. Check whether CPU usage is also high.
4. Check for packet loss, because packet loss can increase latency.
5. Review recent deployments or configuration changes.
6. Inspect network routing and interface errors.

## Escalation

Escalate if latency remains above the threshold for more than 15 minutes or affects multiple nodes in the same region.

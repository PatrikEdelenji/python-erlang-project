# Packet Loss Runbook

## Symptoms

Packet loss means that some network packets do not reach their destination. This can cause retries, slow connections, broken sessions, and unstable service quality.

## Common Causes

- Network congestion
- Faulty network interface
- Bad routing path
- Overloaded node
- Physical link problems
- Firewall or traffic shaping issues

## Recommended Checks

1. Check packet loss percentage for the affected node.
2. Compare packet loss with nearby or related nodes.
3. Inspect network interface errors.
4. Check whether latency is also high.
5. Check whether throughput dropped recently.
6. Review recent network configuration changes.

## Escalation

Escalate if packet loss is above the threshold for several consecutive measurements or affects multiple nodes.

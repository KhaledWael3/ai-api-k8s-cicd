# Loki logging notes

## How logs flow

Every container writes to stdout. The kubelet stores those streams as files on the node. Promtail runs as a DaemonSet, meaning one agent pod per node, tails those files, attaches labels like namespace, pod and app, and pushes them to Loki. Loki indexes only the labels, not the log text, which is why it is far lighter than an ELK stack. Grafana queries Loki with LogQL and renders the results next to Prometheus metrics in the same dashboard.

Flow in one line: app stdout, kubelet log files, Promtail (per node agent), Loki (store), Grafana (query and view).

## Example LogQL queries

All logs from the app pods:

    {namespace="default", pod=~"ai-api.*"}

Only errors, filtered by text:

    {namespace="default", pod=~"ai-api.*"} |= "ERROR"

Rate of Gemini failures over 5 minutes, usable in a graph panel:

    sum(count_over_time({namespace="default", pod=~"ai-api.*"} |= "Gemini call failed" [5m]))

## Azure mapping

LogQL is to Loki what KQL is to Log Analytics. In Azure the equivalent stack is Container Insights shipping AKS container logs into a Log Analytics workspace, queried with KQL in Azure Monitor.

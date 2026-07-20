# HPA load test demo

Goal: show the HorizontalPodAutoscaler scaling the app from 2 to 5 replicas under CPU load, live.

## Terminal 1: watch the autoscaler

    kubectl get hpa -w

Or in k9s type :hpa and keep it on screen. Watch the TARGETS column, it shows current CPU percent against the 70 percent target.

## Terminal 2: generate load

    kubectl run load --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://ai-api-service/health > /dev/null; done"

This starts a pod that hammers the service in a loop. Add a second one named load2 if CPU does not pass 70 percent.

## What to expect

1. Within about a minute the TARGETS value climbs past 70 percent.
2. REPLICAS steps up, 2 to 3 to 5, new pods appear (watch them in k9s or the Grafana CPU panel).
3. Request rate and CPU rise in the Grafana dashboard, logs keep streaming in the Loki panel.

## Cleanup and scale down

    kubectl delete pod load

CPU drops quickly but REPLICAS stays at 5 for about 5 minutes. That is the HPA stabilization window, a deliberate delay that prevents flapping when load is bursty. Then it steps back down to 2. Mention this in the interview, it shows you know autoscaling is dampened on the way down by design.

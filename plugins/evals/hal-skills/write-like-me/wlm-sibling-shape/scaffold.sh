#!/usr/bin/env bash
set -euo pipefail
# Two published posts from vinta.ws as sibling notes: a short how-to and a long tutorial
mkdir -p notes/Programming/Networking notes/Programming/Kubernetes
cat > "notes/Programming/Networking/Cloudflare Quick Tunnel (TryCloudflare).md" <<'NOTE_EOF'
# Cloudflare Quick Tunnel (TryCloudflare)

#blog-post #cloudflare

Expose your local server to the Internet with one `cloudflared` command (just like `ngrok`). No account registration needed, no installation required (via `docker run`), and free.

```
# assume your local server is at http://localhost:3000
docker run --rm -it cloudflare/cloudflared tunnel --url http://localhost:3000

# if your local server is running inside a Docker container
docker run --rm -it cloudflare/cloudflared tunnel --url http://host.docker.internal:3000
```

ref:
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/

You will see something like this in console:

```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://YOUR_RANDOM_QUICK_TUNNEL_NAME.trycloudflare.com                                   |
+--------------------------------------------------------------------------------------------+
```

Then you're all set.

However, be aware that Google may index your `xxx.trycloudflare.com` sites. Try searching `site:trycloudflare.com` on Google if you don't believe me.
NOTE_EOF
cat > "notes/Programming/Kubernetes/Stop Paying for Kubernetes Load Balancers Use Cloudflare Tunnel Instead.md" <<'NOTE_EOF'
# Stop Paying for Kubernetes Load Balancers: Use Cloudflare Tunnel Instead

#blog-post #cloudflare #kubernetes

To expose services in a Kubernetes cluster, you typically need an Ingress backed by a cloud provider's load balancer, and often a NAT Gateway. For small projects, these costs add up fast (though someone may argue small projects shouldn't use Kubernetes at all).

What if you could ditch the Ingress, Load Balancer, and Public IP entirely? Enter Cloudflare Tunnel (by the way, it costs $0).

## How Cloudflare Tunnel Works

Cloudflare Tunnel relies on a lightweight daemon called `cloudflared` that runs within your cluster to establish secure, persistent outbound connections to Cloudflare's global network (edge servers). Instead of accepting incoming connections, your server runs cloudflared to dial out and establish a secure tunnel with Cloudflare. Then it creates a bidirectional tunnel that allows Cloudflare to route requests to your private services while blocking all direct inbound access to your origin servers.

So basically Cloudflare Tunnel acts as a reverse proxy that routes traffic from Cloudflare edge servers to your private services: Internet -> Cloudflare Edge Server -> Tunnel -> `cloudflared` -> Service -> Pod.

ref:
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/

## Create a Tunnel

A tunnel links your origin to Cloudflare's global network. It is a logical connection that enables secure, persistent outbound connections to Cloudflare's global network (Cloudflare Edge Servers).

- Go to https://one.dash.cloudflare.com/ -> Networks -> Connectors -> Create a tunnel -> Select cloudflared

- Tunnel name: `your-tunnel-name`

- Choose an operating system: `Docker`

Instead of running any installation command, simply copy the token (starts with `eyJ...`). We will use it later.

ref:
https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/deployment-guides/kubernetes/

## Configure Published Application Routes

First of all, make sure you host your domains on Cloudflare, so the following setup can update your domain's DNS records automatically.

Assume you have the following Services in your Kubernetes cluster:

```
apiVersion: v1
kind: Service
metadata:
  name: my-blog
spec:
  selector:
    app: my-blog
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: http
```

You need to configure your published application routes based on your Services, for instance:

- Route 1:

- Domain: `example.com`

- Path: `blog`

- Type: `HTTP`

- URL: `my-blog.default:80` => format: `your-service.your-namespace:your-service-port`

- Route 2:

- Domain: `example.com`

- Path: `(leave it blank)`

- Type: `HTTP`

- URL: `frontend.default:80` => format: `your-service.your-namespace:your-service-port`

## Deploy `cloudflared` to Kubernetes

We will deploy `cloudflared` as a Deployment in Kubernetes. It acts as a connector that routes traffic from Cloudflare's global network directly to your private services. You don't need to expose any of your services to the public Internet.

```
apiVersion: v1
kind: Secret
metadata:
  name: cloudflared-tunnel-token
stringData:
  token: YOUR_TUNNEL_TOKEN
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tunnel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tunnel
  template:
    metadata:
      labels:
        app: tunnel
    spec:
      terminationGracePeriodSeconds: 25
      nodeSelector:
        cloud.google.com/compute-class: "autopilot-spot"
      securityContext:
        sysctls:
          # Allows ICMP traffic (ping, traceroute) to resources behind cloudflared
          - name: net.ipv4.ping_group_range
            value: "65532 65532"
      containers:
        - name: cloudflared
          image: cloudflare/cloudflared:latest
          command:
            - cloudflared
            - tunnel
            - --no-autoupdate
            - --loglevel
            - debug
            - --metrics
            - 0.0.0.0:2000
            - run
          env:
            - name: TUNNEL_TOKEN
              valueFrom:
                secretKeyRef:
                  name: cloudflared-tunnel-token
                  key: token
          livenessProbe:
            httpGet:
              # Cloudflared has a /ready endpoint which returns 200 if and only if it has an active connection to Cloudflare's network
              path: /ready
              port: 2000
            failureThreshold: 1
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: 50m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
```

ref:
https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/cloudflared-parameters/run-parameters/

```
kubectl apply -f cloudflared/deployment.yml
```

That's it! Check the Cloudflare dashboard, and you should see your tunnel status as HEALTHY.

You can now safely delete your Ingress and the underlying load balancer. You don't need them anymore. Enjoy your secure, cost-effective cluster!
NOTE_EOF
printf '# %s\n' "Use Cloudflare Access to Protect Your Website/Service If You Don't Bother to Build a Login Page" > "notes/Programming/Networking/Use Cloudflare Access to Protect Your Website or Service.md"

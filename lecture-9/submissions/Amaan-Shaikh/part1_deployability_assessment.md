# Part 1.1 – Deployability Assessment

## Five Deployability Risks (Baseline)

| Risk | Description | Mitigation in Target |
|------|-------------|---------------------|
| **Host drift** | VMs configured manually; subtle differences between hosts | Immutable container images; infrastructure as code (Terraform + K8s manifests) |
| **Config on disk** | `.env` files edited directly on VMs; secrets in git history | Kubernetes Secrets + external secret store (e.g., AWS Secrets Manager) |
| **Slow rollbacks** | Reverting a bad deploy requires SSH + manual steps + service restart | `kubectl rollout undo` – instant revert to previous ReplicaSet |
| **Local file coupling** | Menu images stored on VM disk (`/var/citybite/uploads`) – not portable | PVC or object storage (S3) – decoupled from compute |
| **Unclear ownership** | Who changed what? No audit trail | GitOps (ArgoCD) or CI pipeline – every change is a PR |

## What Becomes Harder

| Harder Aspect | Mitigation |
|---------------|------------|
| **Local debugging** of distributed issues | Use `kubectl port-forward` + `kubectl logs`; ephemeral namespaces; Telepresence for local-to-cluster debugging |
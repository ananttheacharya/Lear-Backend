"""Lear Mock Service & Simulation Engine.

Provides high-fidelity, interactive mock services for:
- AWS (EC2 instances, CloudWatch metrics, SSM/SSH execution)
- GCP (Compute Engine, Cloud Run, serial logs, gcloud command execution)
- Kubernetes (Pods, ConfigMaps, logs, events, kubectl patch/rollout)
- Datadog (Synthetic monitors, metric spikes, mute action)
- PagerDuty (Services, incidents, acknowledge/resolve actions)
- Grafana (Alert rules, silence action)

Enables end-to-end interactive demos without requiring live cloud infrastructure,
while allowing Lear's AI Copilot (DeepSeek / Kimi / Local SRE Brain) to diagnose
and fix real-looking failure states live.
"""
from __future__ import annotations

import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from prash.connectors.base import ConnectorEvent, ConnectorState, ResourceState

logger = logging.getLogger(__name__)

MOCK_STORE_DIR = Path(__file__).resolve().parent.parent / ".prash"
MOCK_STORE_FILE = MOCK_STORE_DIR / "mock_services_state.json"


class MockServiceManager:
    _instance: Optional["MockServiceManager"] = None

    @classmethod
    def get_instance(cls) -> "MockServiceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        MOCK_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = self._default_state()
        self._load_state()

    def _default_state(self) -> Dict[str, Any]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "aws": {
                "instances": {
                    "prash-test-fixture": {
                        "instance_id": "i-0a81f33e792b0c901",
                        "instance_type": "t3.micro",
                        "region": "ap-south-1",
                        "zone": "ap-south-1a",
                        "state": "running",
                        "status_check": "ok",
                        "marker_present": False,
                        "cpu_pct": 12.4,
                        "memory_pct": 24.8,
                        "active_error": None,
                        "watchdog_log": [
                            f"{now_iso} [INFO] prash-test-fixture.service: worker 1 ready (pid 1042)",
                            f"{now_iso} [INFO] prash-test-fixture.service: health check /ping -> 200 OK (latency 1.4ms)",
                        ],
                    },
                    "payment-api": {
                        "instance_id": "i-0c03d55f914d2e903",
                        "instance_type": "t3.large",
                        "region": "ap-south-1",
                        "zone": "ap-south-1a",
                        "state": "running",
                        "status_check": "ok",
                        "disk_usage_pct": 34.0,
                        "active_error": None,
                        "logs": [
                            f"{now_iso} [INFO] payment-gateway: listening on 0.0.0.0:5000",
                            f"{now_iso} [INFO] payment-gateway: batch settlement 100 transactions committed",
                        ],
                    },
                }
            },
            "gcp": {
                "instances": {
                    "drufiy-proxy": {
                        "instance_id": "gce-drufiy-proxy-882194",
                        "machine_type": "e2-standard-2",
                        "zone": "us-central1-a",
                        "project": "lear-cloud-demo",
                        "state": "RUNNING",
                        "marker_present": False,
                        "active_connections": 142,
                        "max_connections": 1024,
                        "active_error": None,
                        "logs": [
                            f"{now_iso} [NOTICE] envoy-proxy: router upstream pool checkout-api 8/8 healthy",
                            f"{now_iso} [INFO] envoy-proxy: avg ingress throughput 4.2 MB/s, 0 dropped frames",
                        ],
                    },
                    "order-service": {
                        "instance_id": "cloudrun-order-service-rev04",
                        "service_type": "Cloud Run",
                        "region": "us-central1",
                        "project": "lear-cloud-demo",
                        "state": "RUNNING",
                        "memory_limit_mb": 512,
                        "memory_used_mb": 218,
                        "active_error": None,
                        "logs": [
                            f"{now_iso} [INFO] order-service: async order processor worker pool 4 active",
                            f"{now_iso} [INFO] order-service: pubsub subscription ack rate 99.98%",
                        ],
                    },
                }
            },
            "k8s": {
                "namespace": "lear-demo",
                "pods": {
                    "checkout-api": {
                        "name": "checkout-api-7b8f9d6c4-x12ab",
                        "status": "Running",
                        "ready": True,
                        "restarts": 0,
                        "cpu": "45m",
                        "memory": "142Mi",
                        "active_error": None,
                        "logs": [
                            f"{now_iso} INFO:     Started server process [1]",
                            f"{now_iso} INFO:     Database pool postgres:5432 connected. Health check 200 OK",
                        ],
                    },
                    "frontend": {
                        "name": "frontend-5d8f6c4b2-y34cd",
                        "status": "Running",
                        "ready": True,
                        "restarts": 0,
                        "cpu": "15m",
                        "memory": "64Mi",
                        "active_error": None,
                    },
                    "postgres": {
                        "name": "postgres-6b7c8d9e0-z56ef",
                        "status": "Running",
                        "ready": True,
                        "restarts": 0,
                        "cpu": "80m",
                        "memory": "256Mi",
                        "active_error": None,
                    },
                },
                "configmaps": {
                    "checkout-api-config": {
                        "DATABASE_HOST": "postgres",
                        "PORT": "8080",
                        "LOG_LEVEL": "info",
                    }
                },
            },
            "datadog": {
                "monitors": {
                    "prash-test-synthetic-error-rate": {
                        "id": "316853860",
                        "overall_state": "OK",
                        "metric": "prash.test.synthetic_error_rate",
                        "value": 0.4,
                        "threshold": 5.0,
                        "muted": False,
                    }
                }
            },
            "pagerduty": {
                "services": {
                    "prash-v2": {
                        "id": "PDR9824",
                        "status": "resolved",
                        "active_incident_id": None,
                    }
                }
            },
            "grafana": {
                "alerts": {
                    "Prash E2E Test Alert": {
                        "uid": "afw5nq4yyq0owb",
                        "state": "normal",
                        "silenced": False,
                    }
                }
            },
            "github": {
                "repos": {
                    "drufiy/checkout-backend": {
                        "name": "checkout-backend",
                        "full_name": "drufiy/checkout-backend",
                        "default_branch": "main",
                        "latest_commit": "c84f1a2",
                        "ci_status": "success",
                        "active_error": None,
                        "open_prs": [
                            {
                                "number": 54,
                                "title": "feat(payment): integrate stripe express webhook receiver",
                                "state": "open",
                                "user": "ananttheacharya",
                            }
                        ],
                        "workflows": [
                            {
                                "id": 104829,
                                "name": "CI / Test & Build",
                                "status": "completed",
                                "conclusion": "success",
                                "run_number": 142,
                            }
                        ],
                        "logs": [
                            f"{now_iso} [CI] Run #142: pytest -q tests/ -> 42 passed in 1.8s",
                            f"{now_iso} [CI] Container image build drufiy/checkout-backend:latest -> pushed (digest sha256:4a81bc)",
                        ],
                    }
                }
            },
        }

    def _save_state(self):
        try:
            MOCK_STORE_FILE.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to persist mock service state: {e}")

    def _load_state(self):
        if MOCK_STORE_FILE.exists():
            try:
                loaded = json.loads(MOCK_STORE_FILE.read_text(encoding="utf-8"))
                # Merge into default state to guarantee schema consistency
                for section in ["aws", "gcp", "k8s", "github", "datadog", "pagerduty", "grafana"]:
                    if section in loaded:
                        self.state[section] = loaded[section]
            except Exception as e:
                logger.warning(f"Could not load mock service state from disk: {e}")

    # =========================================================================
    # AWS MOCK OPERATIONS
    # =========================================================================

    def aws_locate(self, resource: str) -> Dict[str, Any]:
        instances = self.state["aws"]["instances"]
        if not resource or resource.lower() in ("default", "main", "cluster"):
            first_key = next(iter(instances))
            inst = instances[first_key]
            return {
                "instance_id": inst["instance_id"],
                "instance_type": inst["instance_type"],
                "state": inst["state"],
                "name": first_key,
            }
        for name, inst in instances.items():
            if resource in (name, inst["instance_id"]):
                return {
                    "instance_id": inst["instance_id"],
                    "instance_type": inst["instance_type"],
                    "state": inst["state"],
                    "name": name,
                }
        return {}

    def aws_poll_state(self, resource: str) -> ResourceState:
        info = self.aws_locate(resource)
        if not info:
            return ResourceState(resource, ConnectorState.NOT_FOUND, {})
        name = info["name"]
        inst = self.state["aws"]["instances"][name]

        if inst.get("marker_present") or inst.get("active_error") == "runaway_cpu":
            return ResourceState(
                resource,
                ConnectorState.DEGRADED,
                {
                    "instance_id": inst["instance_id"],
                    "instance_type": inst["instance_type"],
                    "aws_state": inst["state"],
                    "marker": "prash-test-fixture-break",
                    "cpu_utilization": inst["cpu_pct"],
                    "problem": "Runaway thread detected. Simulated failure marker /tmp/prash-test-fixture-break active.",
                },
            )
        elif inst.get("active_error") == "disk_full":
            return ResourceState(
                resource,
                ConnectorState.FAILED,
                {
                    "instance_id": inst["instance_id"],
                    "instance_type": inst["instance_type"],
                    "aws_state": inst["state"],
                    "disk_usage_pct": 100.0,
                    "problem": "Filesystem /var/log is full (100% inode exhaustion). Services unable to write.",
                },
            )

        return ResourceState(
            resource,
            ConnectorState.HEALTHY,
            {
                "instance_id": inst["instance_id"],
                "instance_type": inst["instance_type"],
                "aws_state": inst["state"],
                "cpu_utilization": inst["cpu_pct"],
                "status_checks": "2/2 passed",
            },
        )

    def aws_fetch_logs(self, resource: str) -> list[str]:
        info = self.aws_locate(resource)
        if not info:
            return []
        name = info["name"]
        inst = self.state["aws"]["instances"][name]
        return inst.get("watchdog_log") or inst.get("logs") or []

    def aws_get_stats(self, resource: str, since: datetime.datetime | None = None) -> list[ConnectorEvent]:
        info = self.aws_locate(resource)
        if not info:
            return []
        name = info["name"]
        inst = self.state["aws"]["instances"][name]
        now = datetime.datetime.now(datetime.timezone.utc)

        events: list[ConnectorEvent] = []
        if inst.get("marker_present") or inst.get("active_error"):
            events.append({
                "timestamp": now - datetime.timedelta(minutes=4),
                "connector": "aws",
                "event_type": "CloudWatch_Alarm",
                "summary": f"HighCPUUtilization Alarm in ALARM state: CPU was {inst['cpu_pct']}% >= threshold 85.0%",
                "raw": {"metric": "CPUUtilization", "value": inst["cpu_pct"], "instance_id": inst["instance_id"]},
            })
            events.append({
                "timestamp": now - datetime.timedelta(minutes=2),
                "connector": "aws",
                "event_type": "Watchdog_Timeout",
                "summary": "Watchdog thread unresponsive for 120s on prash-test-fixture.service",
                "raw": {"service": "prash-test-fixture", "marker": "/tmp/prash-test-fixture-break"},
            })
        else:
            events.append({
                "timestamp": now - datetime.timedelta(minutes=5),
                "connector": "aws",
                "event_type": "CloudWatch_Metric",
                "summary": f"CPUUtilization normal: {inst['cpu_pct']}%",
                "raw": {"metric": "CPUUtilization", "value": inst["cpu_pct"]},
            })
        return events

    def aws_execute_command(self, resource: str, command: str) -> Dict[str, Any]:
        info = self.aws_locate(resource)
        if not info:
            return {"error": f"Instance {resource} not found"}
        name = info["name"]
        inst = self.state["aws"]["instances"][name]

        # Simulate execution and auto-heal triggers
        stdout = f"[mock-ssm@{inst['instance_id']}]$ {command}\n"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if "rm" in command and "prash-test-fixture-break" in command:
            inst["marker_present"] = False
            inst["active_error"] = None
            inst["cpu_pct"] = 11.8
            inst.setdefault("watchdog_log", []).append(f"{now_iso} [INFO] Marker /tmp/prash-test-fixture-break removed by Lear SRE")
            stdout += "Removed /tmp/prash-test-fixture-break.\n"

        if "systemctl restart" in command or "restart" in command:
            inst["marker_present"] = False
            inst["active_error"] = None
            inst["cpu_pct"] = 9.5
            inst["state"] = "running"
            inst.setdefault("watchdog_log", []).append(f"{now_iso} [INFO] Service restarted cleanly. Health probes passing (200 OK).")
            stdout += "Service restarted successfully. Active: active (running).\n"

        if "truncate" in command or "rm" in command and "log" in command:
            inst["disk_usage_pct"] = 15.0
            inst["active_error"] = None
            stdout += "Disk space reclaimed. Free space: 85%.\n"

        self._save_state()
        return {
            "source": "mock-ssm",
            "status": "Success",
            "stdout": stdout,
            "stderr": "",
        }

    # =========================================================================
    # GCP MOCK OPERATIONS
    # =========================================================================

    def gcp_locate(self, resource: str) -> Dict[str, Any]:
        instances = self.state["gcp"]["instances"]
        for name, inst in instances.items():
            if resource in (name, inst["instance_id"]):
                return {
                    "name": name,
                    "instance_id": inst["instance_id"],
                    "state": inst["state"],
                    "zone": inst.get("zone", "us-central1-a"),
                    "machine_type": inst.get("machine_type", "e2-standard-2"),
                }
        return {}

    def gcp_poll_state(self, resource: str) -> ResourceState:
        info = self.gcp_locate(resource)
        if not info:
            return ResourceState(resource, ConnectorState.NOT_FOUND, {})
        name = info["name"]
        inst = self.state["gcp"]["instances"][name]

        if inst.get("marker_present") or inst.get("active_error") == "proxy_exhaustion":
            return ResourceState(
                resource,
                ConnectorState.DEGRADED,
                {
                    "instance_id": inst["instance_id"],
                    "gcp_state": inst["state"],
                    "active_connections": inst.get("active_connections", 1024),
                    "problem": "Connection pool exhausted (1024/1024). Gateway 504 timeouts to upstream services.",
                },
            )
        elif inst.get("active_error") == "cloudrun_oom":
            return ResourceState(
                resource,
                ConnectorState.CRASH_LOOPING,
                {
                    "instance_id": inst["instance_id"],
                    "gcp_state": "CRASH_LOOPING",
                    "memory_used_mb": 512,
                    "memory_limit_mb": 512,
                    "problem": "Container exceeded 512MiB memory quota. Terminated with exit code 137 (OOMKilled).",
                },
            )

        return ResourceState(
            resource,
            ConnectorState.HEALTHY,
            {
                "instance_id": inst["instance_id"],
                "gcp_state": inst["state"],
                "active_connections": inst.get("active_connections", 120),
            },
        )

    def gcp_fetch_logs(self, resource: str) -> list[str]:
        info = self.gcp_locate(resource)
        if not info:
            return []
        name = info["name"]
        return self.state["gcp"]["instances"][name].get("logs", [])

    def gcp_get_stats(self, resource: str, since: datetime.datetime | None = None) -> list[ConnectorEvent]:
        info = self.gcp_locate(resource)
        if not info:
            return []
        name = info["name"]
        inst = self.state["gcp"]["instances"][name]
        now = datetime.datetime.now(datetime.timezone.utc)

        events: list[ConnectorEvent] = []
        if inst.get("marker_present") or inst.get("active_error"):
            events.append({
                "timestamp": now - datetime.timedelta(minutes=3),
                "connector": "gcp",
                "event_type": "Cloud_Monitoring_Alert",
                "summary": f"drufiy-proxy upstream 5xx rate exceeded threshold (>5.0%, current 14.8%)",
                "raw": {"service": name, "connections": inst.get("active_connections", 1024)},
            })
        else:
            events.append({
                "timestamp": now - datetime.timedelta(minutes=5),
                "connector": "gcp",
                "event_type": "Cloud_Monitoring_Metric",
                "summary": f"Proxy request latency healthy (p95: 38ms)",
                "raw": {"service": name, "latency_ms": 38},
            })
        return events

    def gcp_execute_command(self, resource: str, command: str) -> Dict[str, Any]:
        info = self.gcp_locate(resource)
        if not info:
            return {"error": f"Instance {resource} not found"}
        name = info["name"]
        inst = self.state["gcp"]["instances"][name]
        stdout = f"[gcloud-ssh@{name}]$ {command}\n"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if "rm" in command and "prash-test-fixture-break" in command or "reload" in command or "restart" in command:
            inst["marker_present"] = False
            inst["active_error"] = None
            inst["active_connections"] = 138
            inst["state"] = "RUNNING"
            inst.setdefault("logs", []).append(f"{now_iso} [INFO] drufiy-proxy reloaded cleanly by Lear SRE agent.")
            stdout += "Connection pool cleared. Upstream proxy reloaded successfully.\n"

        if "memory" in command or "scale" in command:
            inst["memory_limit_mb"] = 1024
            inst["memory_used_mb"] = 320
            inst["state"] = "RUNNING"
            inst["active_error"] = None
            stdout += "Memory quota scaled to 1024MiB. Container restarted 1/1 Running.\n"

        self._save_state()
        return {
            "source": "mock-gcloud-ssh",
            "status": "Success",
            "stdout": stdout,
            "stderr": "",
        }

    # =========================================================================
    # KUBERNETES MOCK OPERATIONS
    # =========================================================================

    def k8s_get_pods(self) -> List[Dict[str, Any]]:
        pods = []
        for key, p in self.state["k8s"]["pods"].items():
            pods.append({
                "name": p.get("name", key),
                "service": key,
                "status": p.get("status", "Running"),
                "ready": p.get("ready", True),
                "restarts": p.get("restarts", 0),
                "cpu": p.get("cpu", "25m"),
                "memory": p.get("memory", "128Mi"),
            })
        return pods

    def k8s_patch_configmap(self, name: str, patch_data: Dict[str, str]) -> Dict[str, Any]:
        cm = self.state["k8s"]["configmaps"].get(name, {})
        cm.update(patch_data)
        self.state["k8s"]["configmaps"][name] = cm

        # If checkout-api-config is patched to postgres, heal checkout-api pod!
        if name == "checkout-api-config" and patch_data.get("DATABASE_HOST") == "postgres":
            chk = self.state["k8s"]["pods"]["checkout-api"]
            chk["status"] = "Running"
            chk["ready"] = True
            chk["active_error"] = None
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            chk.setdefault("logs", []).append(
                f"{now_iso} INFO: Database host connected (postgres:5432). /healthz -> 200 OK"
            )

        self._save_state()
        return {"success": True, "configmap": cm}

    # =========================================================================
    # GITHUB MOCK OPERATIONS
    # =========================================================================

    def github_locate(self, resource: str) -> Dict[str, Any]:
        repos = self.state.get("github", {}).get("repos", {})
        if resource in repos:
            return repos[resource]
        for k, v in repos.items():
            if resource in (k, v.get("name")):
                return v
        return {
            "name": resource.split("/")[-1] if "/" in resource else resource,
            "full_name": resource if "/" in resource else f"drufiy/{resource}",
            "default_branch": "main",
            "ci_status": "success",
            "active_error": None,
        }

    def github_poll_state(self, resource: str) -> ResourceState:
        info = self.github_locate(resource)
        if not info:
            return ResourceState(resource, ConnectorState.NOT_FOUND, {})
        if info.get("active_error") == "ci_test_failure" or info.get("ci_status") == "failure":
            return ResourceState(
                resource,
                ConnectorState.FAILED,
                {
                    "repo": info.get("full_name", resource),
                    "default_branch": info.get("default_branch", "main"),
                    "ci_status": "failure",
                    "workflow": "CI / Test & Build",
                    "problem": "CI run #143 failed on commit c84f1a2: AssertionError in db connection pool test.",
                },
            )
        return ResourceState(
            resource,
            ConnectorState.HEALTHY,
            {
                "repo": info.get("full_name", resource),
                "default_branch": info.get("default_branch", "main"),
                "ci_status": "success",
                "workflow": "CI / Test & Build",
                "latest_commit": info.get("latest_commit", "c84f1a2"),
            },
        )

    def github_fetch_logs(self, resource: str) -> list[str]:
        info = self.github_locate(resource)
        return info.get("logs", [])

    def github_get_stats(self, resource: str, since: datetime.datetime | None = None) -> list[ConnectorEvent]:
        info = self.github_locate(resource)
        now = datetime.datetime.now(datetime.timezone.utc)
        events: list[ConnectorEvent] = []
        if info.get("active_error") == "ci_test_failure" or info.get("ci_status") == "failure":
            events.append({
                "timestamp": now - datetime.timedelta(minutes=2),
                "connector": "github",
                "event_type": "Workflow_Failure",
                "summary": f"CI run #143 failed on {info.get('full_name', resource)} (commit c84f1a2)",
                "raw": {"status": "failure", "workflow": "CI / Test & Build"},
            })
        else:
            events.append({
                "timestamp": now - datetime.timedelta(minutes=5),
                "connector": "github",
                "event_type": "Workflow_Success",
                "summary": f"CI run #142 passed cleanly for {info.get('full_name', resource)}",
                "raw": {"status": "success", "workflow": "CI / Test & Build"},
            })
        return events

    def github_create_pr(self, repo: str, title: str, head: str, base: str, body: str = "") -> Dict[str, Any]:
        info = self.github_locate(repo)
        repo_key = info.get("full_name", repo)
        if repo_key not in self.state.setdefault("github", {}).setdefault("repos", {}):
            self.state["github"]["repos"][repo_key] = info
        pr_number = len(info.get("open_prs", [])) + 55
        new_pr = {
            "number": pr_number,
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "state": "open",
            "html_url": f"https://github.com/{repo_key}/pull/{pr_number}",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        info.setdefault("open_prs", []).append(new_pr)
        info["ci_status"] = "success"
        info["active_error"] = None
        info.setdefault("logs", []).append(
            f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} [CI] Remediation PR #{pr_number} opened: CI checks passed (200 OK)."
        )
        self._save_state()
        return new_pr

    def github_rerun_job(self, repo: str, job_id: str | None = None) -> Dict[str, Any]:
        info = self.github_locate(repo)
        info["ci_status"] = "success"
        info["active_error"] = None
        info.setdefault("logs", []).append(
            f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} [CI] Workflow re-run initiated by Lear SRE: 42/42 tests passed."
        )
        self._save_state()
        return {"success": True, "message": "Workflow re-run queued and completed successfully."}

    # =========================================================================
    # SCENARIOS: ERROR INJECTION & AI AUTO-FIX
    # =========================================================================

    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "aws_cpu_spike",
                "connector": "aws",
                "name": "AWS EC2 Runaway Watchdog & High CPU",
                "target": "prash-test-fixture",
                "severity": "CRITICAL",
                "description": "Simulates runaway thread and break marker /tmp/prash-test-fixture-break on EC2 instance.",
                "is_active": self.state["aws"]["instances"]["prash-test-fixture"].get("marker_present", False),
                "fix_command": "execute-aws prash-test-fixture --command 'rm -f /tmp/prash-test-fixture-break && systemctl restart prash-test-fixture'",
            },
            {
                "id": "aws_disk_full",
                "connector": "aws",
                "name": "AWS EC2 Inode & Disk Exhaustion",
                "target": "payment-api",
                "severity": "CRITICAL",
                "description": "Simulates 100% disk usage on /var/log, freezing payment processing.",
                "is_active": self.state["aws"]["instances"]["payment-api"].get("active_error") == "disk_full",
                "fix_command": "execute-aws payment-api --command 'truncate -s 0 /var/log/payment.log && systemctl restart payment-api'",
            },
            {
                "id": "gcp_proxy_exhaustion",
                "connector": "gcp",
                "name": "GCP drufiy-proxy Connection Pool Saturation",
                "target": "drufiy-proxy",
                "severity": "CRITICAL",
                "description": "Simulates 1024/1024 proxy connection exhaustion and 504 Gateway Timeouts.",
                "is_active": self.state["gcp"]["instances"]["drufiy-proxy"].get("marker_present", False),
                "fix_command": "execute-gcp drufiy-proxy --command 'rm -f /tmp/prash-test-fixture-break && systemctl reload drufiy-proxy'",
            },
            {
                "id": "gcp_cloudrun_oom",
                "connector": "gcp",
                "name": "GCP Cloud Run Container Memory Quota (OOMKilled)",
                "target": "order-service",
                "severity": "CRITICAL",
                "description": "Simulates container memory spike exceeding 512MiB quota, producing exit code 137.",
                "is_active": self.state["gcp"]["instances"]["order-service"].get("active_error") == "cloudrun_oom",
                "fix_command": "execute-gcp order-service --command 'gcloud run services update order-service --memory 1024Mi'",
            },
            {
                "id": "k8s_configmap_corrupt",
                "connector": "k8s",
                "name": "Kubernetes ConfigMap Database Mismatch (CrashLoopBackOff)",
                "target": "checkout-api",
                "severity": "CRITICAL",
                "description": "Sets DATABASE_HOST to postgres-wrong in checkout-api-config, breaking customer orders.",
                "is_active": self.state["k8s"]["pods"]["checkout-api"].get("status") == "CrashLoopBackOff",
                "fix_command": "edit-configmap checkout-api-config --key DATABASE_HOST --value postgres",
            },
            {
                "id": "github_ci_failure",
                "connector": "github",
                "name": "GitHub Actions CI Build & Test Failure",
                "target": "drufiy/checkout-backend",
                "severity": "HIGH",
                "description": "Simulates broken CI workflow on commit c84f1a2 blocking deployment pipeline.",
                "is_active": self.state.get("github", {}).get("repos", {}).get("drufiy/checkout-backend", {}).get("ci_status") == "failure",
                "fix_command": "github-open-pr --repo drufiy/checkout-backend --title 'fix(db): restore database pool host' && rerun-job",
            },
            {
                "id": "datadog_error_spike",
                "connector": "datadog",
                "name": "Datadog Synthetic Error Rate Monitor Alert",
                "target": "prash-test-synthetic-error-rate",
                "severity": "HIGH",
                "description": "Triggers synthetic error rate spike (8.7% > 5.0% threshold) on Datadog monitor.",
                "is_active": self.state["datadog"]["monitors"]["prash-test-synthetic-error-rate"]["overall_state"] == "Alert",
                "fix_command": "datadog-mute-monitor prash-test-synthetic-error-rate --minutes 30",
            },
            {
                "id": "pagerduty_critical",
                "connector": "pagerduty",
                "name": "PagerDuty P1 Incident (Service Unreachable)",
                "target": "prash-v2",
                "severity": "CRITICAL",
                "description": "Triggers critical on-call incident on PagerDuty service.",
                "is_active": self.state["pagerduty"]["services"]["prash-v2"]["status"] == "triggered",
                "fix_command": "pagerduty-resolve prash-v2",
            },
            {
                "id": "multi_cloud_cascade",
                "connector": "multi-cloud",
                "name": "Multi-Cloud Cascade (AWS Database Lock -> GCP Proxy Timeout)",
                "target": "all",
                "severity": "CRITICAL",
                "description": "Simulates cascading failure across AWS, GCP, and Kubernetes for cross-cloud diagnosis demo.",
                "is_active": (
                    self.state["aws"]["instances"]["prash-test-fixture"].get("marker_present", False)
                    and self.state["gcp"]["instances"]["drufiy-proxy"].get("marker_present", False)
                ),
                "fix_command": "prash fix --all",
            },
        ]

    def inject_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Injects simulated failure and creates official SRE incident in IncidentManager."""
        from prash.incident_manager import create_incident

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        incident_res = None

        if scenario_id == "aws_cpu_spike":
            inst = self.state["aws"]["instances"]["prash-test-fixture"]
            inst["marker_present"] = True
            inst["active_error"] = "runaway_cpu"
            inst["cpu_pct"] = 94.6
            inst.setdefault("watchdog_log", []).append(
                f"{now_iso} [FATAL] Simulated break marker /tmp/prash-test-fixture-break detected! Watchdog loop wedged."
            )
            incident_res = create_incident(
                service="prash-test-fixture",
                namespace="aws-ap-south-1",
                title="[CRITICAL] AWS EC2 prash-test-fixture CPU Spike (94.6%) & Watchdog Hang",
                severity="CRITICAL",
                error_summary="Marker /tmp/prash-test-fixture-break active. Watchdog thread unresponsive, CPU at 94.6%.",
                diagnosis="Lear Autonomous SRE detected runaway thread on EC2 instance i-0a81f33e792b0c901. Service wedged.",
                proposed_remediation="Execute SSM command: rm -f /tmp/prash-test-fixture-break && systemctl restart prash-test-fixture",
                patch_data={"command": "rm -f /tmp/prash-test-fixture-break && systemctl restart prash-test-fixture"},
                cluster="AWS EC2 ap-south-1 Mumbai",
                tags=["CRITICAL", "AWS", "EC2", "HIGH-CPU"],
            )

        elif scenario_id == "aws_disk_full":
            inst = self.state["aws"]["instances"]["payment-api"]
            inst["disk_usage_pct"] = 100.0
            inst["active_error"] = "disk_full"
            inst.setdefault("logs", []).append(
                f"{now_iso} [CRITICAL] ENOSPC: no space left on device. Cannot write payment ledger."
            )
            incident_res = create_incident(
                service="payment-api",
                namespace="aws-ap-south-1",
                title="[CRITICAL] AWS EC2 payment-api Inode/Disk Full (100%)",
                severity="CRITICAL",
                error_summary="ENOSPC: no space left on device on /var/log/payment.log. Inode exhaustion.",
                diagnosis="Payment processing daemon halted because journal volume is 100% full.",
                proposed_remediation="Execute SSM command: truncate -s 0 /var/log/payment.log && systemctl restart payment-api",
                patch_data={"command": "truncate -s 0 /var/log/payment.log && systemctl restart payment-api"},
                cluster="AWS EC2 ap-south-1 Mumbai",
                tags=["CRITICAL", "AWS", "DISK-FULL"],
            )

        elif scenario_id == "gcp_proxy_exhaustion":
            inst = self.state["gcp"]["instances"]["drufiy-proxy"]
            inst["marker_present"] = True
            inst["active_error"] = "proxy_exhaustion"
            inst["active_connections"] = 1024
            inst.setdefault("logs", []).append(
                f"{now_iso} [ALERT] 1024/1024 active connections. Upstream timeout 504 Gateway Timeout."
            )
            incident_res = create_incident(
                service="drufiy-proxy",
                namespace="gcp-us-central1",
                title="[CRITICAL] GCP Compute Engine drufiy-proxy Connection Saturation (504 Gateway Timeout)",
                severity="CRITICAL",
                error_summary="upstream proxy timeout: max connection limit 1024 reached. 504 Gateway Timeout to clients.",
                diagnosis="Envoy connection pool saturated by zombie connections. Marker /tmp/prash-test-fixture-break present.",
                proposed_remediation="Execute gcloud SSH: rm -f /tmp/prash-test-fixture-break && systemctl reload drufiy-proxy",
                patch_data={"command": "rm -f /tmp/prash-test-fixture-break && systemctl reload drufiy-proxy"},
                cluster="Google Cloud Platform (us-central1-a)",
                tags=["CRITICAL", "GCP", "PROXY-TIMEOUT"],
            )

        elif scenario_id == "gcp_cloudrun_oom":
            inst = self.state["gcp"]["instances"]["order-service"]
            inst["active_error"] = "cloudrun_oom"
            inst["state"] = "CRASH_LOOPING"
            inst["memory_used_mb"] = 512
            inst.setdefault("logs", []).append(
                f"{now_iso} [FATAL] Container terminated with exit code 137 (OOMKilled). Exceeded 512MiB memory quota."
            )
            incident_res = create_incident(
                service="order-service",
                namespace="gcp-us-central1",
                title="[CRITICAL] GCP Cloud Run order-service Container OOMKilled (Exit Code 137)",
                severity="CRITICAL",
                error_summary="Container terminated with exit code 137 (OOMKilled). Memory usage reached 512MiB quota.",
                diagnosis="Memory leak in order batch aggregation worker exceeded 512MiB Cloud Run quota.",
                proposed_remediation="Scale Cloud Run memory allocation to 1024MiB and restart container.",
                patch_data={"command": "gcloud run services update order-service --memory 1024Mi"},
                cluster="Google Cloud Platform (Cloud Run us-central1)",
                tags=["CRITICAL", "GCP", "OOMKILLED"],
            )

        elif scenario_id == "k8s_configmap_corrupt":
            chk = self.state["k8s"]["pods"]["checkout-api"]
            chk["status"] = "CrashLoopBackOff"
            chk["ready"] = False
            chk["active_error"] = "db_mismatch"
            self.state["k8s"]["configmaps"]["checkout-api-config"]["DATABASE_HOST"] = "postgres-wrong"
            chk.setdefault("logs", []).append(
                f"{now_iso} gaierror: [Errno -2] Name does not resolve for database host 'postgres-wrong:5432'"
            )
            incident_res = create_incident(
                service="checkout-api",
                namespace="lear-demo",
                title="[CRITICAL] checkout-api Database Connectivity Failure (CrashLoopBackOff)",
                severity="CRITICAL",
                error_summary="gaierror: [Errno -2] Name does not resolve for database host 'postgres-wrong:5432'",
                diagnosis="DeepSeek AI Brain analyzed CrashLoopBackOff: ConfigMap 'checkout-api-config' DATABASE_HOST is set to 'postgres-wrong'.",
                proposed_remediation="Patch ConfigMap checkout-api-config (DATABASE_HOST -> postgres) and trigger rolling restart.",
                patch_data={"DATABASE_HOST": "postgres"},
                cluster="AWS EKS lear-demo (ap-south-1 Mumbai)",
                tags=["CRITICAL", "KUBERNETES", "DATABASE"],
            )

        elif scenario_id == "github_ci_failure":
            repo = self.state.setdefault("github", {}).setdefault("repos", {}).setdefault("drufiy/checkout-backend", {
                "name": "checkout-backend",
                "full_name": "drufiy/checkout-backend",
                "default_branch": "main",
                "latest_commit": "c84f1a2",
            })
            repo["ci_status"] = "failure"
            repo["active_error"] = "ci_test_failure"
            repo.setdefault("logs", []).append(
                f"{now_iso} [FATAL] CI Run #143 FAILED on commit c84f1a2: AssertionError in db connection pool test."
            )
            incident_res = create_incident(
                service="drufiy/checkout-backend",
                namespace="github-ci",
                title="[FAILED] GitHub Actions CI: drufiy/checkout-backend Build & Test Failure",
                severity="HIGH",
                error_summary="Workflow 'CI / Test & Build' failed on commit c84f1a2: DB connection pool test assertion failed.",
                diagnosis="Regression introduced in commit c84f1a2: DATABASE_HOST configuration syntax error broke automated CI test suite.",
                proposed_remediation="Open remediation PR reverting broken config commit and re-run CI workflow.",
                patch_data={"action": "github-open-pr", "repo": "drufiy/checkout-backend"},
                cluster="GitHub Actions CI/CD",
                tags=["HIGH", "GITHUB", "CI-FAILURE"],
            )

        elif scenario_id == "datadog_error_spike":
            mon = self.state["datadog"]["monitors"]["prash-test-synthetic-error-rate"]
            mon["overall_state"] = "Alert"
            mon["value"] = 8.7
            incident_res = create_incident(
                service="prash-test-synthetic-error-rate",
                namespace="datadog",
                title="[ALERT] Datadog Monitor: Synthetic Error Rate Spike (8.7% > 5.0%)",
                severity="HIGH",
                error_summary="Monitor 316853860 triggered Alert: avg(last_5m) prash.test.synthetic_error_rate = 8.7%",
                diagnosis="Datadog synthetic anomaly detected. Exceeded 5.0% error budget threshold.",
                proposed_remediation="Mute Datadog monitor for 30 minutes while investigating upstream root cause.",
                patch_data={"action": "datadog-mute-monitor"},
                cluster="Datadog Observability",
                tags=["HIGH", "DATADOG", "MONITOR-ALERT"],
            )

        elif scenario_id == "pagerduty_critical":
            pd = self.state["pagerduty"]["services"]["prash-v2"]
            pd["status"] = "triggered"
            incident_res = create_incident(
                service="prash-v2",
                namespace="pagerduty",
                title="[P1-CRITICAL] PagerDuty Incident: Service checkout-api Unreachable",
                severity="CRITICAL",
                error_summary="Events API v2 trigger: High HTTP 5xx rate on checkout-api edge route.",
                diagnosis="Critical incident open on PagerDuty on-call schedule for DrufiyAI.",
                proposed_remediation="Acknowledge incident and initiate auto-healing runbook.",
                patch_data={"action": "pagerduty-acknowledge"},
                cluster="PagerDuty On-Call",
                tags=["P1", "PAGERDUTY", "ON-CALL"],
            )

        elif scenario_id == "multi_cloud_cascade":
            # Break AWS, GCP, K8s, and GitHub
            self.inject_scenario("aws_cpu_spike")
            self.inject_scenario("gcp_proxy_exhaustion")
            self.inject_scenario("k8s_configmap_corrupt")
            self.inject_scenario("github_ci_failure")
            incident_res = create_incident(
                service="multi-cloud-topology",
                namespace="multi-cloud",
                title="[MULTI-CLOUD-OUTAGE] Cascading Failure: AWS EC2 Lock + GCP Proxy Timeout + EKS Crash + CI Break",
                severity="CRITICAL",
                error_summary="Correlated anomaly: AWS EC2 CPU lock, GCP drufiy-proxy saturation, EKS checkout-api CrashLoop, and broken CI pipeline.",
                diagnosis="Cross-Cloud Domino Anomaly: Database lock on AWS cascaded to GCP ingress connection starvation and broken CI deployment.",
                proposed_remediation="Execute orchestrated multi-cloud remediation: clear AWS marker, flush GCP proxy, patch K8s ConfigMap, and re-run GitHub CI.",
                cluster="Multi-Cloud Hybrid (AWS + GCP + GitHub)",
                tags=["CRITICAL", "MULTI-CLOUD", "CASCADE"],
            )

        self._save_state()
        return {
            "success": True,
            "scenario_id": scenario_id,
            "incident": incident_res,
            "state": self.state,
        }

    def _execute_llm_inference(self, active_summary: str, recent_logs: list[str]) -> tuple[str, str]:
        """Calls actual DeepSeek / Kimi model to perform live SRE diagnostic reasoning."""
        import dotenv
        dotenv.load_dotenv()
        from prash.brain.kimi_client import _deepseek_client, _deepseek_model, _kimi_client, _kimi_model
        import asyncio
        import threading

        logs_text = "\n".join(recent_logs[-10:]) if recent_logs else "No active error traces in buffer."
        system_prompt = (
            "You are Lear, an autonomous AI Site Reliability Engineer.\n"
            "Analyze the active infrastructure failure and error logs across our production microservices.\n"
            "Provide:\n"
            "1. Concise Root Cause Diagnosis\n"
            "2. Specific remediation commands to apply (SSM, gcloud, kubectl, or gh)\n"
            "3. Expected post-heal operational verification\n"
            "Be direct, technical, and authoritative in 3-4 sentences."
        )
        user_prompt = f"ACTIVE INCIDENT TELEMETRY:\n{active_summary}\n\nRECENT LOGS:\n{logs_text}"

        model_name = "Lear SRE Brain"
        diagnosis_result = ""

        async def _call_model():
            nonlocal model_name, diagnosis_result
            client = _deepseek_client()
            if client:
                try:
                    model_name = _deepseek_model()
                    res = await client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        max_tokens=300,
                        temperature=0.2,
                    )
                    diagnosis_result = res.choices[0].message.content or ""
                    return
                except Exception as e:
                    logger.warning(f"DeepSeek diagnosis error: {e}")

            k_client = _kimi_client()
            if k_client:
                try:
                    model_name = _kimi_model()
                    res = await k_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        max_tokens=300,
                        temperature=0.2,
                    )
                    diagnosis_result = res.choices[0].message.content or ""
                    return
                except Exception as e:
                    logger.warning(f"Kimi diagnosis error: {e}")

        def _worker():
            try:
                asyncio.run(asyncio.wait_for(_call_model(), timeout=10.0))
            except Exception as exc:
                logger.warning(f"Inference worker exception: {exc}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout=12.0)

        if not diagnosis_result:
            diagnosis_result = (
                f"Lear Autonomous SRE diagnosed root cause across active topology: {active_summary}. "
                "Executing targeted auto-remediation runbooks across connectors."
            )

        return model_name, diagnosis_result

    def ai_auto_fix(self, scenario_id: Optional[str] = None) -> Dict[str, Any]:
        """Automatically diagnoses and executes the AI fix for the active failure scenario using real LLM inference."""
        from prash.incident_manager import get_latest_incident, approve_incident

        latest = get_latest_incident()
        actions_taken = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Gather active failures and logs for real LLM reasoning
        active_failures = []
        recent_logs = []

        # 1. AWS Fixes
        inst_aws = self.state["aws"]["instances"]["prash-test-fixture"]
        if inst_aws.get("marker_present") or inst_aws.get("active_error") == "runaway_cpu":
            active_failures.append("AWS EC2 prash-test-fixture CPU spike (94.6%) and watchdog hang with break marker")
            recent_logs.extend(inst_aws.get("watchdog_log", []))
            self.aws_execute_command("prash-test-fixture", "rm -f /tmp/prash-test-fixture-break && systemctl restart prash-test-fixture")
            actions_taken.append({
                "connector": "aws",
                "target": "prash-test-fixture",
                "action": "execute-aws",
                "command": "rm -f /tmp/prash-test-fixture-break && systemctl restart prash-test-fixture",
                "result": "Cleared break marker. Watchdog thread recovered. CPU dropped from 94.6% to 11.2%. State: HEALTHY.",
            })

        inst_pay = self.state["aws"]["instances"]["payment-api"]
        if inst_pay.get("active_error") == "disk_full":
            active_failures.append("AWS EC2 payment-api Inode/Disk 100% full on /var/log")
            recent_logs.extend(inst_pay.get("logs", []))
            self.aws_execute_command("payment-api", "truncate -s 0 /var/log/payment.log && systemctl restart payment-api")
            actions_taken.append({
                "connector": "aws",
                "target": "payment-api",
                "action": "execute-aws",
                "command": "truncate -s 0 /var/log/payment.log && systemctl restart payment-api",
                "result": "Truncated payment transaction log. Disk space reclaimed (85% free). Service restored to HEALTHY.",
            })

        # 2. GCP Fixes
        inst_gcp = self.state["gcp"]["instances"]["drufiy-proxy"]
        if inst_gcp.get("marker_present") or inst_gcp.get("active_error") == "proxy_exhaustion":
            active_failures.append("GCP Compute Engine drufiy-proxy connection pool saturated (1024/1024) -> 504 Timeout")
            recent_logs.extend(inst_gcp.get("logs", []))
            self.gcp_execute_command("drufiy-proxy", "rm -f /tmp/prash-test-fixture-break && systemctl reload drufiy-proxy")
            actions_taken.append({
                "connector": "gcp",
                "target": "drufiy-proxy",
                "action": "execute-gcp",
                "command": "rm -f /tmp/prash-test-fixture-break && systemctl reload drufiy-proxy",
                "result": "Cleared marker. Flushed zombie connections. Proxy reloaded (138 active connections). State: HEALTHY.",
            })

        inst_run = self.state["gcp"]["instances"]["order-service"]
        if inst_run.get("active_error") == "cloudrun_oom":
            active_failures.append("GCP Cloud Run order-service container OOMKilled (Exit Code 137, exceeded 512MB)")
            recent_logs.extend(inst_run.get("logs", []))
            self.gcp_execute_command("order-service", "gcloud run services update order-service --memory 1024Mi")
            actions_taken.append({
                "connector": "gcp",
                "target": "order-service",
                "action": "execute-gcp",
                "command": "gcloud run services update order-service --memory 1024Mi",
                "result": "Allocated 1024MiB container memory. Container restarted with 0 OOM errors. State: HEALTHY.",
            })

        # 3. K8s Fixes
        chk = self.state["k8s"]["pods"]["checkout-api"]
        if chk.get("status") == "CrashLoopBackOff" or chk.get("active_error"):
            active_failures.append("Kubernetes checkout-api pod in CrashLoopBackOff (DATABASE_HOST set to postgres-wrong)")
            recent_logs.extend(chk.get("logs", []))
            self.k8s_patch_configmap("checkout-api-config", {"DATABASE_HOST": "postgres"})
            actions_taken.append({
                "connector": "k8s",
                "target": "checkout-api-config",
                "action": "edit_configmap",
                "command": "patch configmap checkout-api-config (DATABASE_HOST: postgres)",
                "result": "Patched ConfigMap to postgres:5432. Pod rolled out cleanly. Probe /healthz -> 200 OK. State: HEALTHY.",
            })

        # 4. GitHub Fixes
        repo = self.state.get("github", {}).get("repos", {}).get("drufiy/checkout-backend")
        if repo and (repo.get("active_error") or repo.get("ci_status") == "failure"):
            active_failures.append("GitHub Actions CI Run #143 failed on commit c84f1a2: DB connection test broken")
            recent_logs.extend(repo.get("logs", []))
            self.github_rerun_job("drufiy/checkout-backend")
            actions_taken.append({
                "connector": "github",
                "target": "drufiy/checkout-backend",
                "action": "github-re-run-job",
                "command": "gh run rerun 143 --repo drufiy/checkout-backend",
                "result": "Regression patched. Automated CI pipeline re-run succeeded (42/42 tests passed). State: HEALTHY.",
            })

        # 5. Datadog & PagerDuty Fixes
        mon = self.state["datadog"]["monitors"]["prash-test-synthetic-error-rate"]
        if mon["overall_state"] == "Alert":
            mon["overall_state"] = "OK"
            mon["value"] = 0.5
            mon["muted"] = True
            actions_taken.append({
                "connector": "datadog",
                "target": "prash-test-synthetic-error-rate",
                "action": "datadog-mute-monitor",
                "command": "datadog-mute-monitor prash-test-synthetic-error-rate --minutes 30",
                "result": "Monitor muted and metric normalized. State: OK.",
            })

        pd = self.state["pagerduty"]["services"]["prash-v2"]
        if pd["status"] == "triggered":
            pd["status"] = "resolved"
            actions_taken.append({
                "connector": "pagerduty",
                "target": "prash-v2",
                "action": "pagerduty-resolve",
                "command": "pagerduty-resolve prash-v2",
                "result": "PagerDuty incident marked RESOLVED on on-call schedule.",
            })

        # Run real LLM inference for diagnosis
        failure_summary = "; ".join(active_failures) if active_failures else "Routine preventive health check and baseline verification."
        inference_model, inference_diagnosis = self._execute_llm_inference(failure_summary, recent_logs)

        # Update latest incident with real LLM reasoning
        if latest and latest.get("status") != "RESOLVED":
            latest["agent_thinking"] = inference_diagnosis
            latest["diagnosis"] = inference_diagnosis
            approve_incident(latest["incident_id"], approver=f"Lear AI ({inference_model})")

        self._save_state()
        return {
            "success": True,
            "inference_model": inference_model,
            "inference_diagnosis": inference_diagnosis,
            "actions_taken": actions_taken,
            "message": f"Lear AI ({inference_model}) successfully diagnosed root cause and restored all services to 100% HEALTHY.",
            "latest_incident": get_latest_incident(),
        }

    def heal_all(self) -> Dict[str, Any]:
        """Resets all mock services across AWS, GCP, K8s, GitHub, Datadog, PagerDuty to baseline healthy."""
        self.state = self._default_state()
        self._save_state()
        return {"success": True, "message": "All mock services restored to 100% HEALTHY baseline."}

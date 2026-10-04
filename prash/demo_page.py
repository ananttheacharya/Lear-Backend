"""Lear Interactive Demo Control Center & Storefront.

Serves an executive-grade dashboard allowing presenters to:
  1. Demonstrate the live customer storefront experience and impact of outages.
  2. Simulate real-world failures across AWS, GCP, Kubernetes, Datadog, and PagerDuty.
  3. Witness real-time AI diagnosis and autonomous multi-cloud remediation (SSM, gcloud, kubectl, API resolution).
  4. View dispatched executive alerts and incident war rooms.
"""
from __future__ import annotations

DEMO_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lear | Autonomous SRE Multi-Cloud Demo Control Center</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #07090E;
      --surface: #0D111A;
      --surface-border: #1B2333;
      --surface-hover: #141A28;
      --primary: #10B981;
      --primary-glow: rgba(16, 185, 129, 0.25);
      --danger: #F43F5E;
      --danger-glow: rgba(244, 63, 94, 0.25);
      --warning: #F59E0B;
      --cyan: #06B6D4;
      --purple: #8B5CF6;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background-color: var(--bg);
      color: var(--text-main);
      font-family: 'Inter', -apple-system, sans-serif;
      overflow-x: hidden;
      min-height: 100vh;
    }
    header {
      background: rgba(13, 17, 26, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--surface-border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .logo-group {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .logo {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: 1px;
      color: #FFF;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .logo span {
      color: var(--primary);
    }
    .status-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--primary);
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--primary);
      box-shadow: 0 0 10px var(--primary);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.3); }
      100% { opacity: 1; transform: scale(1); }
    }
    .cluster-info {
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .cluster-tag {
      background: rgba(255,255,255,0.04);
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--surface-border);
    }
    .cluster-tag strong {
      color: #FFF;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-secondary {
      background: #1E293B;
      border: 1px solid var(--surface-border);
      color: #E2E8F0;
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-secondary:hover {
      background: #334155;
      border-color: #475569;
    }

    /* Sub-nav connector tabs */
    .connector-tabs-bar {
      background: #0B0E16;
      border-bottom: 1px solid var(--surface-border);
      padding: 8px 28px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tab-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .tab-btn:hover {
      color: #FFF;
      background: rgba(255, 255, 255, 0.05);
    }
    .tab-btn.active {
      color: #FFF;
      background: #1B2333;
      border-color: #2D3A54;
    }

    .main-grid {
      display: grid;
      grid-template-columns: 1fr 1.1fr;
      gap: 24px;
      padding: 24px;
      max-width: 1700px;
      margin: 0 auto;
    }

    .pane {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    .pane-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(20, 26, 40, 0.4);
    }
    .pane-title {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .pane-subtitle {
      font-size: 12px;
      color: var(--text-muted);
    }
    .pane-body {
      padding: 20px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* Radar / Multi-Cloud Service Cards */
    .service-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }
    .service-card {
      background: #111724;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: all 0.2s;
    }
    .service-card:hover {
      border-color: #2D3A54;
      background: #141C2C;
    }
    .service-card.error {
      border-color: rgba(244, 63, 94, 0.6);
      background: rgba(244, 63, 94, 0.08);
    }
    .service-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .service-card-title {
      font-size: 13px;
      font-weight: 700;
      color: #E2E8F0;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .service-badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(16, 185, 129, 0.2);
      color: #34D399;
    }
    .service-card.error .service-badge {
      background: rgba(244, 63, 94, 0.2);
      color: #FB7185;
    }
    .service-detail {
      font-size: 11px;
      color: var(--text-dim);
      font-family: 'JetBrains Mono', monospace;
      display: flex;
      justify-content: space-between;
    }
    .service-meta {
      font-size: 11px;
      color: var(--text-muted);
    }

    /* Storefront & Customer Traffic */
    .store-banner {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%);
      border: 1px solid rgba(16, 185, 129, 0.2);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .store-banner.error {
      background: linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
      border-color: rgba(244, 63, 94, 0.4);
    }
    .store-banner h4 {
      font-size: 14px;
      font-weight: 700;
    }
    .store-banner p {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .product-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }
    .product-card {
      background: #111724;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .product-icon {
      font-size: 24px;
      margin-bottom: 6px;
    }
    .product-name {
      font-size: 12px;
      font-weight: 600;
      color: #E2E8F0;
    }
    .product-price {
      font-size: 14px;
      font-weight: 700;
      color: var(--primary);
      margin: 6px 0;
    }
    .btn-add-cart {
      background: rgba(16, 185, 129, 0.15);
      color: #34D399;
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
    }
    .checkout-box {
      background: #111724;
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .checkout-summary {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px dashed var(--surface-border);
      padding-bottom: 10px;
    }
    .btn-checkout {
      background: linear-gradient(135deg, #10B981 0%, #059669 100%);
      color: #FFF;
      border: none;
      padding: 12px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 15px var(--primary-glow);
      transition: all 0.2s;
    }
    .btn-checkout:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px var(--primary-glow);
    }
    .btn-checkout:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .order-status-feed {
      background: #090C13;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      min-height: 100px;
      max-height: 140px;
      overflow-y: auto;
    }
    .feed-line {
      margin-bottom: 6px;
      display: flex;
      gap: 8px;
    }
    .feed-line.ok { color: #34D399; }
    .feed-line.err { color: #F43F5E; }
    .feed-line.warn { color: #FBBF24; }
    .feed-line.info { color: #94A3B8; }

    /* Failure Scenario Launcher Grid */
    .scenarios-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }
    .scenario-card {
      background: #111724;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 8px;
    }
    .scenario-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .scenario-tag {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .tag-aws { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
    .tag-gcp { background: rgba(56, 189, 248, 0.2); color: #38BDF8; }
    .tag-k8s { background: rgba(139, 92, 246, 0.2); color: #A78BFA; }
    .tag-obs { background: rgba(244, 63, 94, 0.2); color: #FB7185; }
    .tag-cascade { background: rgba(236, 72, 153, 0.2); color: #F472B6; }

    .scenario-title {
      font-size: 13px;
      font-weight: 700;
      color: #E2E8F0;
    }
    .scenario-desc {
      font-size: 11px;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .scenario-plan {
      font-size: 11px;
      color: var(--primary);
      background: rgba(16, 185, 129, 0.08);
      padding: 6px 8px;
      border-radius: 6px;
      border-left: 2px solid var(--primary);
      font-family: 'JetBrains Mono', monospace;
    }
    .btn-inject {
      background: rgba(244, 63, 94, 0.15);
      border: 1px solid rgba(244, 63, 94, 0.4);
      color: #FB7185;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-inject:hover {
      background: rgba(244, 63, 94, 0.25);
    }

    /* Primary Auto-Remediation Bar */
    .remediation-bar {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(139, 92, 246, 0.1) 100%);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .btn-ai-fix {
      background: linear-gradient(135deg, #10B981 0%, #059669 100%);
      color: #FFF;
      border: none;
      padding: 14px 24px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 4px 20px var(--primary-glow);
      transition: all 0.2s;
      white-space: nowrap;
    }
    .btn-ai-fix:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 25px var(--primary-glow);
    }

    .control-actions {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }
    .btn-action {
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-action-warroom {
      background: #2563EB;
      color: #FFF;
      border: 1px solid #3B82F6;
    }
    .btn-action-traffic {
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.4);
      color: #38BDF8;
    }
    .btn-action-reset {
      background: #1E293B;
      border: 1px solid var(--surface-border);
      color: #E2E8F0;
    }

    .terminal-box {
      background: #07090F;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #CBD5E1;
      height: 220px;
      overflow-y: auto;
      line-height: 1.6;
    }
    .term-tag {
      font-weight: 700;
    }
    .tag-brain { color: #818CF8; }
    .tag-aws-term { color: #F59E0B; }
    .tag-gcp-term { color: #38BDF8; }
    .tag-k8s-term { color: #A78BFA; }
    .tag-dd-term { color: #F472B6; }
    .tag-fix-term { color: #34D399; }
    .tag-err-term { color: #F43F5E; }

    /* Modal Styles */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 24px;
    }
    .modal-overlay.active { display: flex; }
    .modal-content {
      background: #0E131F;
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      width: 100%;
      max-width: 800px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }
    .modal-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #131A2B;
    }
    .modal-body {
      padding: 0;
      flex: 1;
      overflow-y: auto;
      background: #080B11;
    }
    .email-frame {
      width: 100%;
      height: 520px;
      border: none;
    }
    .modal-footer {
      padding: 14px 24px;
      border-top: 1px solid var(--surface-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #101624;
    }

    /* Toast */
    .toast-alert {
      position: fixed;
      top: 76px;
      right: 28px;
      background: #131A2B;
      border: 1px solid var(--danger);
      box-shadow: 0 10px 30px rgba(244, 63, 94, 0.3);
      border-radius: 10px;
      padding: 16px 20px;
      display: none;
      align-items: center;
      gap: 14px;
      z-index: 90;
      animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      max-width: 440px;
    }
    .toast-alert.active { display: flex; }
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  </style>
</head>
<body>
  <header>
    <div class="logo-group">
      <div class="logo">LEAR<span>.AI</span></div>
      <div class="status-badge" id="sreBadge">
        <div class="pulse-dot"></div>
        AUTONOMOUS SRE ACTIVE
      </div>
    </div>
    <div class="cluster-info">
      <span class="cluster-tag">☁️ <strong>AWS EC2 & ECS</strong> (Mock Active)</span>
      <span class="cluster-tag">⚡ <strong>GCP Compute & Cloud Run</strong> (Mock Active)</span>
      <span class="cluster-tag">☸️ <strong>Kubernetes</strong> (lear-demo)</span>
      <span class="cluster-tag">🐙 <strong>GitHub CI/CD</strong> (drufiy/checkout-backend)</span>
      <span class="cluster-tag">📊 <strong>Datadog & PagerDuty</strong></span>
    </div>
    <div class="header-actions">
      <a href="/store" target="_blank" class="btn-secondary" style="text-decoration: none; color: #FFF; background: linear-gradient(135deg, #10B981 0%, #059669 100%); border: none;">🛍️ Live Customer Storefront</a>
      <button class="btn-secondary" onclick="openEmailModal()">✉️ Incident Alert Email</button>
      <button class="btn-secondary" onclick="resetAllServices()">🔄 Reset Baseline</button>
    </div>
  </header>

  <!-- Filter tabs -->
  <div class="connector-tabs-bar">
    <button class="tab-btn active" onclick="filterConnectorTab('all')">🌐 All Cloud Connectors</button>
    <button class="tab-btn" onclick="filterConnectorTab('aws')">☁️ AWS (EC2/SSM)</button>
    <button class="tab-btn" onclick="filterConnectorTab('gcp')">⚡ Google Cloud (GCE/Cloud Run)</button>
    <button class="tab-btn" onclick="filterConnectorTab('k8s')">☸️ Kubernetes (Pods/ConfigMaps)</button>
    <button class="tab-btn" onclick="filterConnectorTab('github')">🐙 GitHub (Actions/CI)</button>
    <button class="tab-btn" onclick="filterConnectorTab('obs')">📊 Observability (Datadog/PagerDuty)</button>
  </div>

  <div class="toast-alert" id="incidentToast">
    <div style="font-size: 24px;">🚨</div>
    <div>
      <div style="font-size: 14px; font-weight: 700; color: #F8FAFC;" id="toastTitle">CRITICAL OUTAGE DETECTED</div>
      <div style="font-size: 12px; color: #CBD5E1; margin-top: 2px;" id="toastDesc">Service degradation detected. AI auto-remediation available.</div>
    </div>
    <button class="btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="triggerAutoFix()">Fix Now</button>
  </div>

  <div class="main-grid">
    <!-- LEFT PANE: Fleet Topology & Live Workload -->
    <div class="pane">
      <div class="pane-header">
        <div>
          <div class="pane-title">🌐 Multi-Cloud Service Topology & Customer Storefront</div>
          <div class="pane-subtitle">Live health status across AWS, GCP, K8s, and real-time checkout pipeline</div>
        </div>
        <span class="status-badge" id="fleetStatusBadge">100% HEALTHY</span>
      </div>
      <div class="pane-body">
        <!-- Service Radar Grid -->
        <div>
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 8px;">
            MICROSERVICES & CONNECTOR RADAR
          </div>
          <div class="service-grid" id="serviceGrid">
            <!-- AWS Cards -->
            <div class="service-card" id="cardAwsFixture" data-connector="aws">
              <div class="service-card-header">
                <span class="service-card-title">☁️ prash-test-fixture</span>
                <span class="service-badge" id="badgeAwsFixture">Running</span>
              </div>
              <div class="service-detail">
                <span>CPU: <strong id="valAwsCpu">12.4%</strong></span>
                <span>Type: t3.micro</span>
              </div>
              <div class="service-meta">AWS EC2 (ap-south-1a) • Watchdog OK</div>
            </div>

            <div class="service-card" id="cardAwsPayment" data-connector="aws">
              <div class="service-card-header">
                <span class="service-card-title">☁️ payment-api</span>
                <span class="service-badge" id="badgeAwsPayment">Running</span>
              </div>
              <div class="service-detail">
                <span>Disk: <strong id="valAwsDisk">34%</strong></span>
                <span>Port: 5000</span>
              </div>
              <div class="service-meta">AWS EC2 (ap-south-1) • Settlement Engine</div>
            </div>

            <!-- GCP Cards -->
            <div class="service-card" id="cardGcpProxy" data-connector="gcp">
              <div class="service-card-header">
                <span class="service-card-title">⚡ drufiy-proxy</span>
                <span class="service-badge" id="badgeGcpProxy">RUNNING</span>
              </div>
              <div class="service-detail">
                <span>Conns: <strong id="valGcpConns">142/1024</strong></span>
                <span>Zone: us-c1-a</span>
              </div>
              <div class="service-meta">GCP Compute Engine • Envoy Ingress</div>
            </div>

            <div class="service-card" id="cardGcpOrder" data-connector="gcp">
              <div class="service-card-header">
                <span class="service-card-title">⚡ order-service</span>
                <span class="service-badge" id="badgeGcpOrder">RUNNING</span>
              </div>
              <div class="service-detail">
                <span>RAM: <strong id="valGcpRam">218MB / 512MB</strong></span>
                <span>Rev: v4</span>
              </div>
              <div class="service-meta">GCP Cloud Run • Async Processor</div>
            </div>

            <!-- K8s Cards -->
            <div class="service-card" id="cardK8sCheckout" data-connector="k8s">
              <div class="service-card-header">
                <span class="service-card-title">☸️ checkout-api</span>
                <span class="service-badge" id="badgeK8sCheckout">Running</span>
              </div>
              <div class="service-detail">
                <span>Host: <strong id="valK8sHost">postgres</strong></span>
                <span>Restarts: 0</span>
              </div>
              <div class="service-meta">K8s Pod • FastAPI Core Backend</div>
            </div>

            <div class="service-card" id="cardK8sFrontend" data-connector="k8s">
              <div class="service-card-header">
                <span class="service-card-title">☸️ frontend-web</span>
                <span class="service-badge" id="badgeK8sFrontend">Running</span>
              </div>
              <div class="service-detail">
                <span>Ingress: ELB :80</span>
                <span>Ready: 1/1</span>
              </div>
              <div class="service-meta">K8s Pod • Nginx Web Gateway</div>
            </div>

            <!-- Observability Cards -->
            <div class="service-card" id="cardDatadog" data-connector="obs">
              <div class="service-card-header">
                <span class="service-card-title">📊 datadog-monitor</span>
                <span class="service-badge" id="badgeDatadog">OK</span>
              </div>
              <div class="service-detail">
                <span>Rate: <strong id="valDdRate">0.4%</strong></span>
                <span>Limit: 5.0%</span>
              </div>
              <div class="service-meta">Synthetic Monitor #316853860</div>
            </div>

            <div class="service-card" id="cardPagerDuty" data-connector="obs">
              <div class="service-card-header">
                <span class="service-card-title">📟 pagerduty-oncall</span>
                <span class="service-badge" id="badgePagerDuty">Resolved</span>
              </div>
              <div class="service-detail">
                <span>Service: prash-v2</span>
                <span>Escalation: P1</span>
              </div>
              <div class="service-meta">On-Call Notification Engine</div>
            </div>

            <div class="service-card" id="cardK8sPostgres" data-connector="k8s">
              <div class="service-card-header">
                <span class="service-card-title">🐘 postgres-primary</span>
                <span class="service-badge" id="badgeK8sPostgres">Running</span>
              </div>
              <div class="service-detail">
                <span>Port: 5432</span>
                <span>Health: 200 OK</span>
              </div>
              <div class="service-meta">K8s StatefulSet • Orders DB</div>
            </div>

            <!-- GitHub Card -->
            <div class="service-card" id="cardGithub" data-connector="github">
              <div class="service-card-header">
                <span class="service-card-title">🐙 drufiy/checkout-backend</span>
                <span class="service-badge" id="badgeGithub">Passing</span>
              </div>
              <div class="service-detail">
                <span>Branch: <strong id="valGithubBranch">main</strong></span>
                <span>Commit: <strong id="valGithubCommit">c84f1a2</strong></span>
              </div>
              <div class="service-meta">GitHub Actions CI • Workflow #143</div>
            </div>
          </div>
        </div>

        <!-- Storefront Demo Section -->
        <div class="store-banner" id="storeBanner">
          <div>
            <h4 id="bannerTitle">🟢 Customer Checkout Pipeline Online</h4>
            <p id="bannerDesc">ELB -> Envoy Proxy -> checkout-api -> Postgres DB active & healthy</p>
          </div>
          <div style="font-size: 13px; font-weight: 700; color: var(--primary);" id="bannerLatency">18ms</div>
        </div>

        <div class="product-list">
          <div class="product-card">
            <div class="product-icon">🛡️</div>
            <div class="product-name">AI SRE Sentinel Key</div>
            <div class="product-price">$49.99</div>
            <button class="btn-add-cart" onclick="selectItem('AI SRE Sentinel Key', 49.99)">Selected</button>
          </div>
          <div class="product-card">
            <div class="product-icon">⚡</div>
            <div class="product-name">Multi-Cloud Edge Appliance</div>
            <div class="product-price">$199.00</div>
            <button class="btn-add-cart" onclick="selectItem('Multi-Cloud Edge Appliance', 199.00)">Select</button>
          </div>
          <div class="product-card">
            <div class="product-icon">📦</div>
            <div class="product-name">Autonomous Cluster Unit</div>
            <div class="product-price">$499.00</div>
            <button class="btn-add-cart" onclick="selectItem('Autonomous Cluster Unit', 499.00)">Select</button>
          </div>
        </div>

        <div class="checkout-box">
          <div class="checkout-summary">
            <div>
              <div style="font-size: 11px; color: var(--text-muted);">Cart Item</div>
              <strong id="cartItemName" style="font-size: 13px;">AI SRE Sentinel Key</strong>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 11px; color: var(--text-muted);">Total Price</div>
              <div style="font-size: 18px; font-weight: 800; color: #FFF;" id="cartItemPrice">$49.99</div>
            </div>
          </div>
          <button class="btn-checkout" id="checkoutBtn" onclick="performCustomerCheckout()">
            💳 Place Order & Run E2E Checkout Flow
          </button>
        </div>

        <div>
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px;">
            CUSTOMER ORDER AUDIT STREAM
          </div>
          <div class="order-status-feed" id="orderFeed">
            <div class="feed-line info">[INIT] Storefront loaded. Connected to multi-cloud proxy pipeline.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT PANE: Failure Simulator & AI SRE Brain -->
    <div class="pane">
      <div class="pane-header">
        <div>
          <div class="pane-title">⚡ Autonomous Multi-Cloud SRE Control Engine</div>
          <div class="pane-subtitle">Simulate outages on AWS, GCP, K8s & witness Lear AI auto-fix live</div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted);">
          <span>AI Healing:</span>
          <strong style="color: var(--primary);">AUTONOMOUS</strong>
        </div>
      </div>
      <div class="pane-body">
        <!-- Hero AI Remediation Trigger Bar -->
        <div class="remediation-bar">
          <div>
            <div style="font-size: 14px; font-weight: 800; color: #FFF;">Autonomous AI Multi-Cloud Healing</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
              Lear AI analyzes logs, executes targeted SSM/gcloud/kubectl fixes, and resolves alarms.
            </div>
          </div>
          <button class="btn-ai-fix" id="btnHeroFix" onclick="triggerAutoFix()">
            🧠 Trigger Lear AI Auto-Fix
          </button>
        </div>

        <!-- Failure Simulator Cards -->
        <div>
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 8px;">
            SIMULATE OUTAGES FOR LIVE DEMO
          </div>
          <div class="scenarios-grid">
            <!-- AWS Scenario 1 -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-aws">AWS EC2</span>
                <button class="btn-inject" onclick="injectScenario('aws_cpu_spike')">💥 Inject CPU Spike</button>
              </div>
              <div class="scenario-title">Runaway Watchdog Hang</div>
              <div class="scenario-desc">Simulates runaway thread and break marker on EC2 instance. CPU spikes to 99%.</div>
              <div class="scenario-plan">AI Plan: SSM RunCommand rm marker & restart service</div>
            </div>

            <!-- AWS Scenario 2 -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-aws">AWS EBS</span>
                <button class="btn-inject" onclick="injectScenario('aws_disk_full')">💥 Inject Disk Full</button>
              </div>
              <div class="scenario-title">Filesystem Inode Full</div>
              <div class="scenario-desc">/var/log reaches 100% capacity on payment-api, blocking transaction commits.</div>
              <div class="scenario-plan">AI Plan: Purge rotated logs & restart journald</div>
            </div>

            <!-- GCP Scenario 1 -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-gcp">GCP Compute</span>
                <button class="btn-inject" onclick="injectScenario('gcp_proxy_exhaustion')">💥 Inject Proxy Leak</button>
              </div>
              <div class="scenario-title">Connection Pool Exhaustion</div>
              <div class="scenario-desc">drufiy-proxy hits 1024/1024 sockets. External HTTP calls drop into 502 Bad Gateway.</div>
              <div class="scenario-plan">AI Plan: gcloud compute ssh reload envoy proxy</div>
            </div>

            <!-- GCP Scenario 2 -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-gcp">GCP Cloud Run</span>
                <button class="btn-inject" onclick="injectScenario('gcp_cloudrun_oom')">💥 Inject OOM Crash</button>
              </div>
              <div class="scenario-title">Container Memory OOM</div>
              <div class="scenario-desc">order-service worker leaks RAM, container terminates with SIGKILL 137.</div>
              <div class="scenario-plan">AI Plan: gcloud run services update --memory 1024Mi</div>
            </div>

            <!-- K8s Scenario -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-k8s">Kubernetes</span>
                <button class="btn-inject" onclick="injectScenario('k8s_configmap_corrupt')">💥 Corrupt ConfigMap</button>
              </div>
              <div class="scenario-title">ConfigMap DB Host Mismatch</div>
              <div class="scenario-desc">checkout-api-config set to 'postgres-wrong'. Pods enter CrashLoopBackOff.</div>
              <div class="scenario-plan">AI Plan: kubectl patch configmap & rollout restart</div>
            </div>

            <!-- GitHub Scenario -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag" style="background: rgba(139, 92, 246, 0.2); color: #C084FC;">GitHub CI</span>
                <button class="btn-inject" onclick="injectScenario('github_ci_failure')">💥 Break CI Workflow</button>
              </div>
              <div class="scenario-title">CI Pipeline Broken Build</div>
              <div class="scenario-desc">Checkout backend unit tests fail on commit c84f1a2, blocking hotfix release deployment.</div>
              <div class="scenario-plan">AI Plan: Analyze pytest trace & auto-create hotfix PR</div>
            </div>

            <!-- Cascade Scenario -->
            <div class="scenario-card">
              <div class="scenario-header">
                <span class="scenario-tag tag-cascade">Multi-Cloud</span>
                <button class="btn-inject" style="background: rgba(236,72,153,0.2); color:#F472B6;" onclick="injectScenario('multi_cloud_cascade')">🌪️ Full Cascade</button>
              </div>
              <div class="scenario-title">Cross-Cloud Domino Failure</div>
              <div class="scenario-desc">Simultaneous break across AWS, GCP, K8s, and Datadog monitoring alert storm.</div>
              <div class="scenario-plan">AI Plan: Orchestrate multi-connector recovery sequence</div>
            </div>
          </div>
        </div>

        <!-- Quick actions -->
        <div class="control-actions">
          <button class="btn-action btn-action-warroom" onclick="openLatestWarRoom()">
            💬 Open Incident War Room
          </button>
          <button class="btn-action btn-action-traffic" id="btnTraffic" onclick="toggleTraffic()">
            🚀 Start Background Traffic
          </button>
          <button class="btn-action btn-action-reset" onclick="resetAllServices()">
            🔄 Reset Fleet to 100%
          </button>
        </div>

        <!-- Terminal log -->
        <div>
          <div style="font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 8px;">
            LEAR AUTONOMOUS REASONING & SRE EXECUTION LOG
          </div>
          <div class="terminal-box" id="termLog">
            <div><span class="term-tag tag-brain">[BRAIN]</span> DeepSeek / Kimi AI reasoning engine connected and warm.</div>
            <div><span class="term-tag tag-aws-term">[AWS]</span> Monitoring 2 EC2 instances (prash-test-fixture, payment-api).</div>
            <div><span class="term-tag tag-gcp-term">[GCP]</span> Monitoring drufiy-proxy (GCE) and order-service (Cloud Run).</div>
            <div><span class="term-tag tag-k8s-term">[K8S]</span> Watching namespace 'lear-demo' pod lifecycle and ConfigMaps.</div>
            <div><span class="term-tag tag-dd-term">[DATADOG]</span> Metric monitor 'prash.test.synthetic_error_rate' synchronized.</div>
            <div><span class="term-tag tag-fix-term">[READY]</span> Autonomous multi-cloud remediation circuit armed.</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- EMAIL MODAL -->
  <div class="modal-overlay" id="emailModal">
    <div class="modal-content">
      <div class="modal-header">
        <div style="font-weight: 700; font-size: 16px; color: #FFF;">
          ✉️ Dispatched Executive Incident Alert Email
        </div>
        <button class="btn-secondary" onclick="closeEmailModal()">✕ Close</button>
      </div>
      <div class="modal-body">
        <iframe class="email-frame" id="emailIframe" src="/api/demo/emails/latest"></iframe>
      </div>
      <div class="modal-footer">
        <div style="font-size: 12px; color: var(--text-muted);">
          Dispatched to: <strong>oncall-sre@lear-demo.com</strong>
        </div>
        <button class="btn-secondary" onclick="sendRealEmail()">🚀 Forward To My Email</button>
      </div>
    </div>
  </div>

  <script>
    let currentItem = { name: "AI SRE Sentinel Key", price: 49.99 };
    let trafficInterval = null;
    let isBroken = false;
    let activeIncidentId = null;

    function selectItem(name, price) {
      currentItem = { name, price };
      document.getElementById('cartItemName').innerText = name;
      document.getElementById('cartItemPrice').innerText = '$' + price.toFixed(2);
    }

    function logTerminal(tagClass, tagText, msg) {
      const term = document.getElementById('termLog');
      const div = document.createElement('div');
      const time = new Date().toLocaleTimeString();
      div.innerHTML = `<span style="color: #64748B;">[${time}]</span> <span class="term-tag ${tagClass}">[${tagText}]</span> ${msg}`;
      term.appendChild(div);
      term.scrollTop = term.scrollHeight;
    }

    function logOrder(type, msg) {
      const feed = document.getElementById('orderFeed');
      const div = document.createElement('div');
      div.className = `feed-line ${type}`;
      const time = new Date().toLocaleTimeString();
      div.innerText = `[${time}] ${msg}`;
      feed.prepend(div);
    }

    function filterConnectorTab(type) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');

      document.querySelectorAll('.service-card').forEach(card => {
        if (type === 'all' || card.getAttribute('data-connector') === type) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    async function performCustomerCheckout() {
      const btn = document.getElementById('checkoutBtn');
      btn.disabled = true;
      btn.innerText = 'Processing Payment via Proxy...';
      const t0 = performance.now();

      try {
        const resp = await fetch('/api/demo/customer-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item: currentItem.name,
            price: currentItem.price
          })
        });
        const elapsed = Math.round(performance.now() - t0);
        const data = await resp.json();

        if (resp.ok && data.status === 'COMPLETED') {
          logOrder('ok', `SUCCESS: Order #${data.order_id} placed for $${currentItem.price} (${elapsed}ms)`);
          document.getElementById('bannerLatency').innerText = `${elapsed}ms`;
        } else {
          logOrder('err', `FAILED: ${data.error || 'HTTP 502/504 Bad Gateway'} (${elapsed}ms)`);
          triggerOutageUI(data.error);
        }
      } catch (err) {
        logOrder('err', `FAILED: Gateway Timeout (${err.message})`);
        triggerOutageUI(err.message);
      } finally {
        btn.disabled = false;
        btn.innerText = '💳 Place Order & Run E2E Checkout Flow';
      }
    }

    function triggerOutageUI(customMsg) {
      isBroken = true;
      document.getElementById('fleetStatusBadge').innerText = 'OUTAGE ACTIVE';
      document.getElementById('fleetStatusBadge').style.borderColor = 'var(--danger)';
      document.getElementById('fleetStatusBadge').style.color = 'var(--danger)';
      document.getElementById('storeBanner').classList.add('error');
      document.getElementById('bannerTitle').innerText = '🔴 CHECKOUT FLOW DEGRADED';
      document.getElementById('bannerDesc').innerText = customMsg || 'Microservice failure detected in pipeline. Orders failing!';
      document.getElementById('bannerLatency').innerText = 'ERR 502';
      document.getElementById('bannerLatency').style.color = 'var(--danger)';
      document.getElementById('incidentToast').classList.add('active');
    }

    function restoreHealthyUI() {
      isBroken = false;
      document.getElementById('fleetStatusBadge').innerText = '100% HEALTHY';
      document.getElementById('fleetStatusBadge').style.borderColor = 'rgba(16, 185, 129, 0.3)';
      document.getElementById('fleetStatusBadge').style.color = 'var(--primary)';
      document.getElementById('storeBanner').classList.remove('error');
      document.getElementById('bannerTitle').innerText = '🟢 Customer Checkout Pipeline Online';
      document.getElementById('bannerDesc').innerText = 'ELB -> Envoy Proxy -> checkout-api -> Postgres DB active & healthy';
      document.getElementById('bannerLatency').innerText = '18ms';
      document.getElementById('bannerLatency').style.color = 'var(--primary)';
      document.getElementById('incidentToast').classList.remove('active');

      // Reset card errors
      document.querySelectorAll('.service-card').forEach(c => c.classList.remove('error'));
      document.getElementById('badgeAwsFixture').innerText = 'Running';
      document.getElementById('valAwsCpu').innerText = '12.4%';
      document.getElementById('badgeGcpProxy').innerText = 'RUNNING';
      document.getElementById('valGcpConns').innerText = '142/1024';
      document.getElementById('badgeK8sCheckout').innerText = 'Running';
      document.getElementById('valK8sHost').innerText = 'postgres';
      document.getElementById('badgeDatadog').innerText = 'OK';
      document.getElementById('valDdRate').innerText = '0.4%';
      document.getElementById('badgePagerDuty').innerText = 'Resolved';
      const ghCard = document.getElementById('cardGithub');
      if (ghCard) ghCard.classList.remove('error');
      const ghBadge = document.getElementById('badgeGithub');
      if (ghBadge) {
        ghBadge.innerText = 'Passing';
        ghBadge.style.background = 'rgba(16, 185, 129, 0.2)';
        ghBadge.style.color = '#34D399';
      }
    }

    async function injectScenario(scenarioId) {
      logTerminal('tag-err-term', 'INJECT', `Injecting failure scenario '${scenarioId}'...`);

      try {
        const res = await fetch('/api/demo/inject-scenario', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scenario_id: scenarioId })
        });
        const d = await res.json();
        if (d.incident_id) activeIncidentId = d.incident_id;

        if (scenarioId === 'aws_cpu_spike') {
          logTerminal('tag-aws-term', 'AWS-CW', 'CloudWatch Alarm HighCPUUtilization triggered: 99.4%');
          document.getElementById('cardAwsFixture').classList.add('error');
          document.getElementById('badgeAwsFixture').innerText = 'Degraded';
          document.getElementById('valAwsCpu').innerText = '99.4%';
          triggerOutageUI('AWS prash-test-fixture CPU spike to 99.4% (Runaway process)');
        } else if (scenarioId === 'aws_disk_full') {
          logTerminal('tag-aws-term', 'AWS-EBS', 'Filesystem /var/log inode capacity reached 100%');
          document.getElementById('cardAwsPayment').classList.add('error');
          document.getElementById('badgeAwsPayment').innerText = 'DiskFull';
          document.getElementById('valAwsDisk').innerText = '100%';
          triggerOutageUI('AWS payment-api disk full: transaction logs rejected');
        } else if (scenarioId === 'gcp_proxy_exhaustion') {
          logTerminal('tag-gcp-term', 'GCP-GCE', 'Envoy connection pool exhausted: 1024/1024 sockets');
          document.getElementById('cardGcpProxy').classList.add('error');
          document.getElementById('badgeGcpProxy').innerText = 'EXHAUSTED';
          document.getElementById('valGcpConns').innerText = '1024/1024';
          triggerOutageUI('GCP drufiy-proxy connection pool exhausted (502 Bad Gateway)');
        } else if (scenarioId === 'gcp_cloudrun_oom') {
          logTerminal('tag-gcp-term', 'GCP-RUN', 'Cloud Run container killed with SIGKILL (Exit code 137 OOM)');
          document.getElementById('cardGcpOrder').classList.add('error');
          document.getElementById('badgeGcpOrder').innerText = 'CRASH_OOM';
          document.getElementById('valGcpRam').innerText = '512MB / 512MB (OOM)';
          triggerOutageUI('GCP order-service killed by Out-Of-Memory');
        } else if (scenarioId === 'k8s_configmap_corrupt') {
          logTerminal('tag-k8s-term', 'K8S', 'ConfigMap checkout-api-config set to DATABASE_HOST=postgres-wrong');
          document.getElementById('cardK8sCheckout').classList.add('error');
          document.getElementById('badgeK8sCheckout').innerText = 'CrashLoop';
          document.getElementById('valK8sHost').innerText = 'postgres-wrong';
          triggerOutageUI('Kubernetes checkout-api CrashLoop: cannot reach postgres database');
        } else if (scenarioId === 'github_ci_failure') {
          logTerminal('tag-err-term', 'GITHUB', 'CI Workflow build failure: test_payment_gateway FAILED (Exit code 1)');
          const ghCard = document.getElementById('cardGithub');
          if (ghCard) ghCard.classList.add('error');
          const ghBadge = document.getElementById('badgeGithub');
          if (ghBadge) {
            ghBadge.innerText = 'FAILED';
            ghBadge.style.background = 'rgba(244, 63, 94, 0.2)';
            ghBadge.style.color = '#FB7185';
          }
          triggerOutageUI('GitHub CI pipeline failing: drufiy/checkout-backend build blocked');
        } else if (scenarioId === 'multi_cloud_cascade') {
          logTerminal('tag-err-term', 'CASCADE', 'Cascading multi-cloud failure across AWS, GCP, and Kubernetes!');
          document.getElementById('cardAwsFixture').classList.add('error');
          document.getElementById('badgeAwsFixture').innerText = 'Degraded';
          document.getElementById('cardGcpProxy').classList.add('error');
          document.getElementById('badgeGcpProxy').innerText = 'EXHAUSTED';
          document.getElementById('cardK8sCheckout').classList.add('error');
          document.getElementById('badgeK8sCheckout').innerText = 'CrashLoop';
          const ghCard = document.getElementById('cardGithub');
          if (ghCard) ghCard.classList.add('error');
          const ghBadge = document.getElementById('badgeGithub');
          if (ghBadge) {
            ghBadge.innerText = 'FAILED';
            ghBadge.style.background = 'rgba(244, 63, 94, 0.2)';
            ghBadge.style.color = '#FB7185';
          }
          document.getElementById('cardDatadog').classList.add('error');
          document.getElementById('badgeDatadog').innerText = 'ALARM';
          document.getElementById('valDdRate').innerText = '14.8%';
          document.getElementById('cardPagerDuty').classList.add('error');
          document.getElementById('badgePagerDuty').innerText = 'TRIGGERED';
          triggerOutageUI('Multi-cloud cascading failure across AWS, GCP, GitHub, and Kubernetes!');
        }

        logTerminal('tag-dd-term', 'DATADOG', 'Datadog monitor #316853860 triggered: Synthetic error rate > 5.0%');
        logTerminal('tag-dd-term', 'PAGERDUTY', 'PagerDuty Incident dispatched: PD-ALERT-98214 (Urgency: High)');
        logTerminal('tag-brain', 'WAR_ROOM', 'Created incident war room: ' + (activeIncidentId || 'active'));
      } catch (e) {
        logTerminal('tag-err-term', 'ERROR', 'Failure injection failed: ' + e.message);
      }
    }

    async function triggerAutoFix() {
      logTerminal('tag-brain', 'AI-SRE', 'Lear AI Copilot evaluating telemetry & root cause via LLM inference...');
      logTerminal('tag-brain', 'EPISODIC', 'Correlating telemetry with multi-cloud runbook catalog...');

      try {
        const res = await fetch('/api/demo/ai-fix', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        const d = await res.json();

        if (d.inference_model) {
          logTerminal('tag-brain', d.inference_model.toUpperCase(), `AI Diagnosis: ${d.inference_diagnosis || d.message}`);
        }

        const actions = d.actions_taken || d.actions || [];
        if (actions.length > 0) {
          actions.forEach(act => {
            const text = typeof act === 'string' ? act : `${act.command} (${act.result})`;
            const conn = (typeof act === 'object' && act.connector) ? act.connector.toUpperCase() : 'AI-FIX';
            if (conn.includes('AWS')) {
              logTerminal('tag-aws-term', 'AWS-SSM', text);
            } else if (conn.includes('GCP')) {
              logTerminal('tag-gcp-term', 'GCP-CMD', text);
            } else if (conn.includes('K8S')) {
              logTerminal('tag-k8s-term', 'K8S-PATCH', text);
            } else if (conn.includes('GITHUB')) {
              logTerminal('tag-dd-term', 'GITHUB-PR', text);
            } else {
              logTerminal('tag-fix-term', conn, text);
            }
          });
        }

        logTerminal('tag-fix-term', 'HEALTHY', 'All connectors and services verified 100% healthy.');
        logTerminal('tag-dd-term', 'DATADOG', 'Synthetic error rate returned to normal baseline (0.4%).');
        logTerminal('tag-dd-term', 'PAGERDUTY', 'PagerDuty incident resolved cleanly.');
        logTerminal('tag-fix-term', 'RESOLVED', 'Resolution broadcasted to War Room. Incident closed.');

        restoreHealthyUI();
        logOrder('ok', 'RECOVERED: Multi-cloud services fully restored by Lear AI! Ready for orders.');
      } catch (e) {
        logTerminal('tag-err-term', 'ERROR', 'AI Fix failed: ' + e.message);
      }
    }

    async function resetAllServices() {
      logTerminal('tag-fix-term', 'RESET', 'Restoring all AWS, GCP, and Kubernetes services to baseline...');
      try {
        await fetch('/api/demo/reset-all', { method: 'POST' });
        restoreHealthyUI();
        logTerminal('tag-fix-term', 'BASELINE', 'All connectors reset to default healthy state.');
      } catch (e) {
        logTerminal('tag-err-term', 'ERROR', 'Reset failed: ' + e.message);
      }
    }

    function openLatestWarRoom() {
      if (activeIncidentId) {
        window.open('/incident/' + activeIncidentId, '_blank');
      } else {
        fetch('/api/incident/latest')
          .then(r => r.json())
          .then(d => {
            if (d.incident && d.incident.incident_id) {
              window.open('/incident/' + d.incident.incident_id, '_blank');
            } else {
              window.open('/incident/INC-LATEST', '_blank');
            }
          })
          .catch(() => window.open('/incident/INC-LATEST', '_blank'));
      }
    }

    function toggleTraffic() {
      const btn = document.getElementById('btnTraffic');
      if (trafficInterval) {
        clearInterval(trafficInterval);
        trafficInterval = null;
        btn.innerText = '🚀 Start Background Traffic';
        btn.style.background = 'rgba(6, 182, 212, 0.15)';
        logTerminal('tag-k8s-term', 'TRAFFIC', 'Background traffic simulation paused.');
      } else {
        trafficInterval = setInterval(performCustomerCheckout, 1000);
        btn.innerText = '🛑 Stop Traffic';
        btn.style.background = 'rgba(244, 63, 94, 0.2)';
        logTerminal('tag-k8s-term', 'TRAFFIC', 'Continuous background traffic started.');
      }
    }

    function openEmailModal() {
      document.getElementById('emailIframe').src = '/api/demo/emails/latest?t=' + Date.now();
      document.getElementById('emailModal').classList.add('active');
    }

    function closeEmailModal() {
      document.getElementById('emailModal').classList.remove('active');
    }

    async function sendRealEmail() {
      const to = prompt("Enter destination email address:", "anant@example.com");
      if (to) {
        try {
          const res = await fetch('/api/demo/send-email', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email: to })
          });
          const d = await res.json();
          alert(d.message || "Email dispatched!");
        } catch (e) {
          alert("Could not send email: " + e.message);
        }
      }
    }

    // Periodic status poll
    setInterval(async () => {
      try {
        const res = await fetch('/api/demo/status');
        const d = await res.json();
        if (d.aws_instances && d.aws_instances['prash-test-fixture']) {
          const f = d.aws_instances['prash-test-fixture'];
          if (f.marker_present || f.active_error) {
            document.getElementById('cardAwsFixture').classList.add('error');
            document.getElementById('badgeAwsFixture').innerText = 'Degraded';
            document.getElementById('valAwsCpu').innerText = (f.cpu_pct || 99.4) + '%';
          }
        }
        if (d.gcp_instances && d.gcp_instances['drufiy-proxy']) {
          const p = d.gcp_instances['drufiy-proxy'];
          if (p.marker_present || p.active_error) {
            document.getElementById('cardGcpProxy').classList.add('error');
            document.getElementById('badgeGcpProxy').innerText = 'EXHAUSTED';
            document.getElementById('valGcpConns').innerText = '1024/1024';
          }
        }
        if (d.github_repos && d.github_repos['drufiy/checkout-backend']) {
          const r = d.github_repos['drufiy/checkout-backend'];
          const ghCard = document.getElementById('cardGithub');
          const ghBadge = document.getElementById('badgeGithub');
          if (r.ci_status === 'failure' || r.active_error) {
            if (ghCard) ghCard.classList.add('error');
            if (ghBadge) {
              ghBadge.innerText = 'FAILED';
              ghBadge.style.background = 'rgba(244, 63, 94, 0.2)';
              ghBadge.style.color = '#FB7185';
            }
          } else {
            if (ghCard && !isBroken) ghCard.classList.remove('error');
            if (ghBadge && !isBroken) {
              ghBadge.innerText = 'Passing';
              ghBadge.style.background = 'rgba(16, 185, 129, 0.2)';
              ghBadge.style.color = '#34D399';
            }
          }
        }
      } catch (e) {}
    }, 4000);
  </script>
</body>
</html>
"""

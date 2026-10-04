"""Clean, Realistic Customer Storefront for Lear Demo.

Designed with executive-grade typography, real enterprise hardware product imagery,
interactive cart and checkout pipeline, and a simulated customer traffic stream
that reacts in real time to injected outages and autonomous AI healing.
"""

def generate_customer_store_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lear Edge Systems | Enterprise Hardware & Telemetry Store</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090D16;
      --surface: #0F172A;
      --surface-elevated: #1E293B;
      --surface-border: #1E293B;
      --surface-hover: #192339;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --primary: #10B981;
      --primary-hover: #059669;
      --primary-glow: rgba(16, 185, 129, 0.25);
      --accent: #3B82F6;
      --accent-glow: rgba(59, 130, 246, 0.25);
      --danger: #EF4444;
      --danger-glow: rgba(239, 68, 68, 0.25);
      --warning: #F59E0B;
      --purple: #8B5CF6;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }

    /* Header */
    header {
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--surface-border);
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .header-inner {
      max-width: 1400px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }
    .brand-logo {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #FFF;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .brand-logo span { color: var(--primary); }
    .brand-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      background: rgba(16, 185, 129, 0.12);
      color: var(--primary);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 3px 8px;
      border-radius: 6px;
    }

    .pipeline-status {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: var(--text-muted);
      background: rgba(30, 41, 59, 0.6);
      padding: 6px 14px;
      border-radius: 9999px;
      border: 1px solid var(--surface-border);
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--primary);
      box-shadow: 0 0 10px var(--primary);
      animation: pulse 2s infinite;
    }
    .pulse-dot.error {
      background: var(--danger);
      box-shadow: 0 0 12px var(--danger);
      animation: pulseErr 1s infinite;
    }
    @keyframes pulse {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.3); }
      100% { opacity: 1; transform: scale(1); }
    }
    @keyframes pulseErr {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(1.5); }
      100% { opacity: 1; transform: scale(1); }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-header {
      background: var(--surface-elevated);
      border: 1px solid var(--surface-border);
      color: #E2E8F0;
      font-size: 12px;
      font-weight: 600;
      padding: 8px 14px;
      border-radius: 8px;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-header:hover {
      background: #334155;
      color: #FFF;
      border-color: #475569;
    }
    .btn-cart {
      background: var(--primary);
      color: #042F2E;
      border: 1px solid rgba(16, 185, 129, 0.6);
      font-size: 13px;
      font-weight: 700;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s;
    }
    .btn-cart:hover {
      background: #34D399;
      transform: translateY(-1px);
    }
    .cart-count {
      background: #042F2E;
      color: var(--primary);
      padding: 2px 7px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 800;
    }

    /* Outage Alert Banner */
    .outage-banner {
      background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(239, 68, 68, 0.2) 100%);
      border-bottom: 1px solid rgba(239, 68, 68, 0.4);
      padding: 12px 24px;
      display: none;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      animation: slideDown 0.3s ease-out;
    }
    .outage-banner.active { display: flex; }
    @keyframes slideDown {
      from { transform: translateY(-100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .outage-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .outage-title {
      font-size: 13px;
      font-weight: 700;
      color: #FCA5A5;
    }
    .outage-desc {
      font-size: 12px;
      color: #CBD5E1;
      font-family: 'JetBrains Mono', monospace;
    }
    .btn-banner-heal {
      background: var(--danger);
      color: #FFF;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
      white-space: nowrap;
    }
    .btn-banner-heal:hover { background: #DC2626; }

    /* Hero Section */
    .hero {
      max-width: 1400px;
      margin: 0 auto;
      padding: 36px 24px 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .hero-top {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 20px;
    }
    .hero-badge {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--accent);
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 4px 10px;
      border-radius: 6px;
      display: inline-block;
      margin-bottom: 8px;
    }
    .hero h1 {
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.8px;
      color: #FFF;
      line-height: 1.2;
    }
    .hero p {
      font-size: 14px;
      color: var(--text-muted);
      max-width: 650px;
      margin-top: 6px;
      line-height: 1.5;
    }

    /* Metrics Strip */
    .metrics-strip {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 8px;
    }
    .metric-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      position: relative;
      overflow: hidden;
    }
    .metric-card::after {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: var(--accent);
      opacity: 0.4;
    }
    .metric-card.healthy::after { background: var(--primary); opacity: 0.8; }
    .metric-card.error::after { background: var(--danger); opacity: 0.9; }
    .metric-label {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-dim);
    }
    .metric-val {
      font-size: 22px;
      font-weight: 800;
      color: #FFF;
      font-family: 'JetBrains Mono', monospace;
    }
    .metric-meta {
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 4px;
    }

    /* Main Content Layout */
    .main-layout {
      max-width: 1400px;
      margin: 0 auto;
      padding: 0 24px 64px 24px;
      display: grid;
      grid-template-columns: 2.2fr 1fr;
      gap: 28px;
    }

    /* Catalog Controls */
    .catalog-controls {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }
    .category-tabs {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .cat-btn {
      background: transparent;
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .cat-btn:hover {
      background: rgba(255, 255, 255, 0.04);
      color: #FFF;
    }
    .cat-btn.active {
      background: var(--surface-elevated);
      color: #FFF;
      border-color: var(--accent);
    }
    .search-box {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 6px 12px;
      font-size: 13px;
      color: #FFF;
      width: 220px;
      outline: none;
      transition: border-color 0.15s;
    }
    .search-box:focus { border-color: var(--accent); }

    /* Product Grid */
    .product-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }
    .product-card {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }
    .product-card:hover {
      border-color: #334155;
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(0,0,0,0.3);
    }
    .product-image-container {
      width: 100%;
      height: 180px;
      background: #0B0F19;
      position: relative;
      overflow: hidden;
    }
    .product-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }
    .product-card:hover .product-image {
      transform: scale(1.05);
    }
    .product-category-tag {
      position: absolute;
      top: 10px;
      left: 10px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(4px);
      color: var(--accent);
    }
    .product-body {
      padding: 18px;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
    }
    .product-title {
      font-size: 16px;
      font-weight: 700;
      color: #FFF;
      line-height: 1.3;
    }
    .product-desc {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-top: 4px;
    }
    .product-specs {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .spec-pill {
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--surface-border);
      color: #CBD5E1;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .product-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    .price-tag {
      display: flex;
      flex-direction: column;
    }
    .price-val {
      font-size: 20px;
      font-weight: 800;
      color: #FFF;
      font-family: 'JetBrains Mono', monospace;
    }
    .price-unit {
      font-size: 11px;
      color: var(--text-dim);
    }
    .btn-buy-card {
      background: var(--surface-elevated);
      color: #FFF;
      border: 1px solid var(--surface-border);
      font-size: 12px;
      font-weight: 700;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .btn-buy-card:hover {
      background: var(--primary);
      color: #042F2E;
      border-color: var(--primary);
    }

    /* Right Sidebar: Cart & Live Order Audit Stream */
    .sidebar-pane {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .card-pane {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 12px;
      padding: 20px;
    }
    .pane-title {
      font-size: 14px;
      font-weight: 700;
      color: #FFF;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 14px;
    }
    .cart-item-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .cart-item-name {
      font-size: 13px;
      font-weight: 600;
      color: #E2E8F0;
    }
    .cart-item-qty {
      font-size: 11px;
      color: var(--text-dim);
    }
    .cart-item-price {
      font-size: 14px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: #FFF;
    }
    .cart-totals {
      margin-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
    }
    .total-row {
      display: flex;
      justify-content: space-between;
    }
    .total-row.grand {
      font-size: 16px;
      font-weight: 800;
      color: #FFF;
      padding-top: 10px;
      border-top: 1px solid var(--surface-border);
      margin-top: 6px;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Pipeline Microservices Visualizer */
    .pipeline-visualizer {
      background: #0B0E16;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-top: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }
    .pipeline-step {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 4px 0;
      color: #CBD5E1;
    }
    .pipeline-step .dot-step {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--primary);
    }
    .pipeline-step.broken .dot-step {
      background: var(--danger);
      animation: pulseErr 1s infinite;
    }
    .pipeline-step.broken {
      color: #F87171;
    }

    .btn-checkout-primary {
      width: 100%;
      margin-top: 18px;
      background: linear-gradient(135deg, #10B981 0%, #059669 100%);
      color: #042F2E;
      border: none;
      padding: 12px 18px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 15px var(--primary-glow);
      transition: all 0.2s;
    }
    .btn-checkout-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px var(--primary-glow);
      background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
    }
    .btn-checkout-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    /* Live Simulated Customer Activity Feed */
    .feed-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .feed-item {
      background: #0B0E16;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 12px;
      transition: all 0.2s;
      animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .feed-item.error {
      border-color: rgba(239, 68, 68, 0.5);
      background: rgba(239, 68, 68, 0.08);
    }
    .feed-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .feed-user {
      font-weight: 700;
      color: #FFF;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .feed-badge {
      font-size: 10px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(16, 185, 129, 0.15);
      color: #34D399;
    }
    .feed-item.error .feed-badge {
      background: rgba(239, 68, 68, 0.2);
      color: #F87171;
    }
    .feed-body {
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
    }
    .feed-err-msg {
      font-size: 11px;
      color: #F87171;
      font-family: 'JetBrains Mono', monospace;
      margin-top: 2px;
    }

    /* Modal */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.75);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }
    .modal-backdrop.active { display: flex; }
    .modal-card {
      background: #0F172A;
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      max-width: 520px;
      width: 100%;
      padding: 28px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      position: relative;
    }
    .modal-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      margin-bottom: 16px;
    }
    .modal-icon.success { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .modal-icon.error { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .modal-title { font-size: 18px; font-weight: 800; color: #FFF; margin-bottom: 6px; }
    .modal-desc { font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 18px; }
    .receipt-box {
      background: #0B0E16;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      line-height: 1.7;
      margin-bottom: 20px;
    }
    .btn-modal-action {
      width: 100%;
      padding: 11px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      border: none;
      transition: all 0.15s;
    }
  </style>
</head>
<body>
  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="brand">
        <a href="/store" class="brand-logo">LEAR<span>//</span>STORE</a>
        <span class="brand-badge">ENTERPRISE HARDWARE</span>
      </div>

      <div class="pipeline-status">
        <span class="pulse-dot" id="headerDot"></span>
        <span id="headerStatusText">All Microservices Operational (p99: 18ms)</span>
      </div>

      <div class="header-actions">
        <button class="btn-header" id="btnToggleSim" onclick="toggleSimulation()">
          <span id="simIcon">⏸</span> <span id="simText">Pause Traffic Sim</span>
        </button>
        <a href="/demo" target="_blank" class="btn-header">
          ⚡ Failure Injection Center
        </a>
        <button class="btn-cart" onclick="scrollToCheckout()">
          🛒 Cart <span class="cart-count" id="cartCountBadge">1</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Outage Alert Banner -->
  <div class="outage-banner" id="outageBanner">
    <div class="outage-info">
      <span style="font-size: 20px;">🚨</span>
      <div>
        <div class="outage-title" id="outageTitle">CRITICAL PRODUCTION ANOMALY DETECTED</div>
        <div class="outage-desc" id="outageDesc">Customer transactions failing across mock cloud topology.</div>
      </div>
    </div>
    <button class="btn-banner-heal" id="btnBannerHeal" onclick="triggerAutoFix()">
      🧠 Trigger Lear AI Auto-Fix
    </button>
  </div>

  <!-- Hero & KPIs -->
  <div class="hero">
    <div class="hero-top">
      <div>
        <span class="hero-badge">Enterprise Production E-Commerce</span>
        <h1>Autonomous Infrastructure Telemetry & Hardware</h1>
        <p>
          Simulating real enterprise shopping transactions hitting local mock microservices across AWS, GCP, and Kubernetes.
          Inject outages to test automated error handling and witness Lear AI diagnose and self-heal live.
        </p>
      </div>
      <div style="font-size: 12px; color: var(--text-dim); text-align: right; font-family: 'JetBrains Mono', monospace;">
        <div>LOCAL MOCK TOPOLOGY ACTIVE</div>
        <div style="color: var(--primary);">ZERO CLOUD BILLS • 100% REALISTIC</div>
      </div>
    </div>

    <!-- Live Metrics Strip -->
    <div class="metrics-strip">
      <div class="metric-card healthy" id="cardKpiOrders">
        <span class="metric-label">Completed Orders</span>
        <span class="metric-val" id="valTotalOrders">142</span>
        <span class="metric-meta">Processed live</span>
      </div>
      <div class="metric-card healthy" id="cardKpiRevenue">
        <span class="metric-label">Total Revenue</span>
        <span class="metric-val" id="valTotalRevenue">$14,280</span>
        <span class="metric-meta">USD Gross Settled</span>
      </div>
      <div class="metric-card healthy" id="cardKpiSuccess">
        <span class="metric-label">Pipeline Success Rate</span>
        <span class="metric-val" id="valSuccessRate">100.0%</span>
        <span class="metric-meta" id="valSuccessMeta">SLO: 99.95% target</span>
      </div>
      <div class="metric-card" id="cardKpiLatency">
        <span class="metric-label">p99 End-to-End Latency</span>
        <span class="metric-val" id="valLatency">18ms</span>
        <span class="metric-meta" id="valLatencyMeta">GCP Ingress ➔ AWS DB</span>
      </div>
    </div>
  </div>

  <!-- Main Store Layout -->
  <div class="main-layout">
    <!-- Left Column: Catalog -->
    <div>
      <div class="catalog-controls">
        <div class="category-tabs">
          <button class="cat-btn active" onclick="filterCategory('all', this)">All Hardware</button>
          <button class="cat-btn" onclick="filterCategory('compute', this)">Edge Compute</button>
          <button class="cat-btn" onclick="filterCategory('security', this)">Security Keys</button>
          <button class="cat-btn" onclick="filterCategory('networking', this)">Networking</button>
          <button class="cat-btn" onclick="filterCategory('storage', this)">NVMe Storage</button>
        </div>
        <input type="text" class="search-box" placeholder="🔍 Search hardware..." oninput="handleSearch(this.value)">
      </div>

      <div class="product-grid" id="productGrid">
        <!-- Products populated via JS -->
      </div>
    </div>

    <!-- Right Column: Cart & Live Customer Activity Stream -->
    <div class="sidebar-pane">
      <!-- Order Summary Card -->
      <div class="card-pane" id="checkoutSection">
        <div class="pane-title">
          <span>Order Checkout</span>
          <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">LIVE INGRESS</span>
        </div>

        <div id="cartItemsContainer">
          <div class="cart-item-row">
            <div>
              <div class="cart-item-name" id="cartItemName">Lear Tensor Node S4</div>
              <div class="cart-item-qty">Qty: 1 • Edge Compute Unit</div>
            </div>
            <div class="cart-item-price" id="cartItemPrice">$49.99</div>
          </div>
        </div>

        <div class="cart-totals">
          <div class="total-row">
            <span>Subtotal</span>
            <span id="cartSubtotal" style="font-family: 'JetBrains Mono', monospace;">$49.99</span>
          </div>
          <div class="total-row">
            <span>Estimated Sales Tax (8.25%)</span>
            <span id="cartTax" style="font-family: 'JetBrains Mono', monospace;">$4.12</span>
          </div>
          <div class="total-row">
            <span>Express Courier Shipping</span>
            <span id="cartShipping" style="font-family: 'JetBrains Mono', monospace;">$5.99</span>
          </div>
          <div class="total-row grand">
            <span>Total Amount</span>
            <span id="cartGrandTotal">$60.10</span>
          </div>
        </div>

        <!-- Pipeline Microservices Hop Visualizer -->
        <div class="pipeline-visualizer">
          <div style="font-size: 10px; font-weight: 700; color: var(--text-dim); margin-bottom: 6px; text-transform: uppercase;">
            Live E2E Hop Verification:
          </div>
          <div class="pipeline-step" id="stepDns"><span class="dot-step"></span> 1. Ingress Router (GCP drufiy-proxy)</div>
          <div class="pipeline-step" id="stepK8s"><span class="dot-step"></span> 2. Order Controller (K8s checkout-api)</div>
          <div class="pipeline-step" id="stepAws"><span class="dot-step"></span> 3. Payment Gateway (AWS payment-api)</div>
          <div class="pipeline-step" id="stepDb"><span class="dot-step"></span> 4. ACID Settlement (PostgreSQL 5432)</div>
        </div>

        <button class="btn-checkout-primary" id="btnPlaceOrder" onclick="executeCheckout()">
          💳 Place Order & Run E2E Transaction
        </button>

        <div style="margin-top: 10px; font-size: 11px; color: var(--text-dim); text-align: center;">
          PCI-DSS Compliant • Simulated End-to-End Pipeline
        </div>
      </div>

      <!-- Live Simulated Customer Activity Feed -->
      <div class="card-pane">
        <div class="pane-title">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span>Live Customer Activity Stream</span>
            <span class="brand-badge" style="font-size: 9px;">SIMULATED USERS</span>
          </div>
          <span style="font-size: 11px; color: var(--primary);" id="activeUsersCount">● 34 Online</span>
        </div>

        <div class="feed-container" id="orderFeed">
          <!-- Live order events stream here -->
          <div class="feed-item">
            <div class="feed-header">
              <span class="feed-user">👤 Sarah Chen · San Francisco, CA</span>
              <span class="feed-badge">200 OK</span>
            </div>
            <div class="feed-body">
              <span>Lear Tensor Node S4</span>
              <span style="font-weight:700; color:#FFF;">$49.99</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Order Result Modal -->
  <div class="modal-backdrop" id="resultModal">
    <div class="modal-card">
      <div class="modal-icon success" id="modalIcon">✓</div>
      <h3 class="modal-title" id="modalTitle">Order Authorized & Confirmed</h3>
      <p class="modal-desc" id="modalDesc">Transaction committed across local mock microservices with zero errors.</p>
      
      <div class="receipt-box" id="modalReceipt">
        <!-- Receipt details populated by JS -->
      </div>

      <div id="modalActions">
        <button class="btn-modal-action" style="background: var(--surface-elevated); color: #FFF;" onclick="closeModal()">
          Done
        </button>
      </div>
    </div>
  </div>

  <script>
    // Product Catalog Data with High-Res Enterprise Hardware Images
    const PRODUCTS = [
      {
        id: "prod_tensor_s4",
        name: "Lear Tensor Node S4",
        category: "compute",
        badge: "Edge AI Accelerator",
        price: 49.99,
        desc: "4-Core neural accelerator unit with hardware telemetry probe and zero-trust enclave.",
        specs: ["4 TOPS NPU", "PCIe Gen4", "TPM 2.0", "15W TDP"],
        image: "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&auto=format&fit=crop&q=80"
      },
      {
        id: "prod_sentinel_key",
        name: "Sentinel SRE Hardware Security Key",
        category: "security",
        badge: "FIDO2 / WebAuthn",
        price: 35.00,
        desc: "Cryptographic hardware sentinel enabling tamper-proof multi-cloud approval of autonomous changes.",
        specs: ["EAL6+ Enclave", "USB-C & NFC", "FIDO2 Level 3", "Ed25519"],
        image: "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=600&auto=format&fit=crop&q=80"
      },
      {
        id: "prod_edge_router",
        name: "Sentinel Multi-Cloud Edge Gateway Router",
        category: "networking",
        badge: "Enterprise Ingress",
        price: 199.00,
        desc: "Ultra-low latency edge gateway with real-time eBPF packet inspection and Envoy mesh sync.",
        specs: ["10Gbps SFP+", "eBPF Ingress", "Envoy v1.30", "Sub-1ms jitter"],
        image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80"
      },
      {
        id: "prod_nvme_cache",
        name: "Quantum NVMe Ephemeral Cache Unit",
        category: "storage",
        badge: "High-IOPS Buffer",
        price: 120.00,
        desc: "High-speed persistent memory buffer designed for local SRE agent episodic memory caching.",
        specs: ["2TB NVMe M.2", "1.2M IOPS", "AES-256", "7000 MB/s Read"],
        image: "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80"
      },
      {
        id: "prod_cluster_unit",
        name: "Autonomous Cluster Sentinel Unit 1U",
        category: "compute",
        badge: "Telemetry Engine",
        price: 499.00,
        desc: "Dedicated rack-mounted out-of-band IPMI & serial telemetry monitor with dual redundant power.",
        specs: ["1U Rackmount", "Dual 800W PSU", "Out-of-band IPMI", "64GB ECC"],
        image: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop&q=80"
      },
      {
        id: "prod_hsm_engine",
        name: "PCI-DSS HSM Cryptographic Payment Engine",
        category: "security",
        badge: "Compliance Module",
        price: 850.00,
        desc: "FIPS 140-3 Level 4 hardware security module for zero-leak transaction processing and tokenization.",
        specs: ["FIPS 140-3 L4", "15,000 TPS", "Zero-Knowledge", "PCI-DSS 4.0"],
        image: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80"
      }
    ];

    // Simulated Buyer Identities
    const SIMULATED_BUYERS = [
      { name: "Sarah Chen", location: "San Francisco, CA", email: "sarah.chen@stripe.com" },
      { name: "Marcus Vance", location: "New York, NY", email: "marcus@datadoghq.com" },
      { name: "Priya Patel", location: "Bengaluru, India", email: "priya.p@flipkart.com" },
      { name: "Kenji Takahashi", location: "Tokyo, Japan", email: "kenji@mercari.jp" },
      { name: "Elena Rossi", location: "Milan, Italy", email: "elena@spotify.com" },
      { name: "Liam O'Connor", location: "London, UK", email: "liam@revolut.com" },
      { name: "David Schneider", location: "Munich, Germany", email: "david@siemens.de" },
      { name: "Sofia Morales", location: "São Paulo, Brazil", email: "sofia@nubank.com.br" }
    ];

    let currentItem = PRODUCTS[0];
    let simulationActive = true;
    let totalOrdersCount = 142;
    let totalRevenue = 14280.00;
    let failedOrdersCount = 0;
    let simInterval = null;

    // Render Product Cards
    function renderProducts(items) {
      const grid = document.getElementById('productGrid');
      grid.innerHTML = items.map(p => `
        <div class="product-card" id="card_${p.id}">
          <div class="product-image-container">
            <span class="product-category-tag">${p.category}</span>
            <img src="${p.image}" alt="${p.name}" class="product-image" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80'">
          </div>
          <div class="product-body">
            <div>
              <div class="product-title">${p.name}</div>
              <div class="product-desc">${p.desc}</div>
              <div class="product-specs">
                ${p.specs.map(s => `<span class="spec-pill">${s}</span>`).join('')}
              </div>
            </div>
            <div class="product-footer">
              <div class="price-tag">
                <span class="price-val">$${p.price.toFixed(2)}</span>
                <span class="price-unit">/ unit</span>
              </div>
              <button class="btn-buy-card" onclick="selectProduct('${p.id}')">
                Buy Item
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }

    function selectProduct(prodId) {
      const p = PRODUCTS.find(item => item.id === prodId);
      if (!p) return;
      currentItem = p;
      document.getElementById('cartItemName').innerText = p.name;
      document.getElementById('cartItemPrice').innerText = '$' + p.price.toFixed(2);
      document.getElementById('cartSubtotal').innerText = '$' + p.price.toFixed(2);
      
      const tax = p.price * 0.0825;
      const total = p.price + tax + 5.99;
      document.getElementById('cartTax').innerText = '$' + tax.toFixed(2);
      document.getElementById('cartGrandTotal').innerText = '$' + total.toFixed(2);
      
      scrollToCheckout();
    }

    function scrollToCheckout() {
      document.getElementById('checkoutSection').scrollIntoView({ behavior: 'smooth' });
    }

    function filterCategory(cat, btn) {
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (cat === 'all') {
        renderProducts(PRODUCTS);
      } else {
        renderProducts(PRODUCTS.filter(p => p.category === cat));
      }
    }

    function handleSearch(query) {
      const q = query.toLowerCase().trim();
      if (!q) {
        renderProducts(PRODUCTS);
        return;
      }
      renderProducts(PRODUCTS.filter(p => 
        p.name.toLowerCase().includes(q) || 
        p.desc.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
      ));
    }

    // Execute Customer Checkout Flow
    async function executeCheckout() {
      const btn = document.getElementById('btnPlaceOrder');
      btn.disabled = true;
      btn.innerText = '⚡ Processing Multi-Cloud Checkout...';

      // Visual step animation
      resetPipelineSteps();
      document.getElementById('stepDns').style.color = '#38BDF8';

      try {
        const buyer = SIMULATED_BUYERS[Math.floor(Math.random() * SIMULATED_BUYERS.length)];
        const res = await fetch('/api/demo/customer-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item: currentItem.name,
            price: currentItem.price,
            customer: buyer
          })
        });

        const data = await res.json();
        if (res.ok && data.status === 'COMPLETED') {
          showModal(true, data);
          recordOrderInFeed(buyer, currentItem, true, data);
        } else {
          showModal(false, data);
          recordOrderInFeed(buyer, currentItem, false, data);
        }
      } catch (e) {
        showModal(false, { error: e.message, code: 502, service: 'edge-gateway' });
      } finally {
        btn.disabled = false;
        btn.innerText = '💳 Place Order & Run E2E Transaction';
      }
    }

    function resetPipelineSteps() {
      ['stepDns', 'stepK8s', 'stepAws', 'stepDb'].forEach(id => {
        const el = document.getElementById(id);
        el.className = 'pipeline-step';
        el.style.color = '#CBD5E1';
      });
    }

    function markPipelineFailure(failingHop) {
      resetPipelineSteps();
      const lower = (failingHop || '').toLowerCase();
      if (lower.includes('gcp') || lower.includes('ingress') || lower.includes('proxy')) {
        document.getElementById('stepDns').className = 'pipeline-step broken';
      } else if (lower.includes('postgre') || lower.includes('database')) {
        document.getElementById('stepDb').className = 'pipeline-step broken';
      } else if (lower.includes('payment') || lower.includes('aws') || lower.includes('settlement')) {
        document.getElementById('stepAws').className = 'pipeline-step broken';
      } else {
        document.getElementById('stepK8s').className = 'pipeline-step broken';
      }
    }

    function recordOrderInFeed(buyer, item, isSuccess, data) {
      const feed = document.getElementById('orderFeed');
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const itemEl = document.createElement('div');
      
      if (isSuccess) {
        totalOrdersCount++;
        totalRevenue += item.price;
        itemEl.className = 'feed-item';
        itemEl.innerHTML = `
          <div class="feed-header">
            <span class="feed-user">👤 ${buyer.name} · ${buyer.location}</span>
            <span class="feed-badge">200 OK (${data.routing?.latency_ms || 18}ms)</span>
          </div>
          <div class="feed-body">
            <span>${item.name}</span>
            <span style="font-weight:700; color:#FFF;">$${item.price.toFixed(2)}</span>
          </div>
        `;
      } else {
        failedOrdersCount++;
        itemEl.className = 'feed-item error';
        markPipelineFailure(data.failing_hop || data.service);
        itemEl.innerHTML = `
          <div class="feed-header">
            <span class="feed-user" style="color:#FCA5A5;">⚠️ ${buyer.name} · ${buyer.location}</span>
            <span class="feed-badge" style="background:rgba(239,68,68,0.2);color:#F87171;">HTTP ${data.code || 500}</span>
          </div>
          <div class="feed-body">
            <span>${item.name}</span>
            <span style="font-weight:700; color:#F87171;">FAILED</span>
          </div>
          <div class="feed-err-msg">${data.error || 'Transaction aborted by upstream cluster anomaly'}</div>
        `;
      }

      feed.insertBefore(itemEl, feed.firstChild);
      while (feed.children.length > 25) {
        feed.removeChild(feed.lastChild);
      }

      updateKPIs();
    }

    function updateKPIs() {
      document.getElementById('valTotalOrders').innerText = totalOrdersCount.toString();
      document.getElementById('valTotalRevenue').innerText = '$' + Math.round(totalRevenue).toLocaleString();
      
      const totalTxs = totalOrdersCount + failedOrdersCount;
      const rate = totalTxs > 0 ? ((totalOrdersCount / totalTxs) * 100).toFixed(1) : '100.0';
      document.getElementById('valSuccessRate').innerText = rate + '%';

      const successCard = document.getElementById('cardKpiSuccess');
      if (parseFloat(rate) < 95.0) {
        successCard.className = 'metric-card error';
      } else {
        successCard.className = 'metric-card healthy';
      }
    }

    function showModal(isSuccess, data) {
      const modal = document.getElementById('resultModal');
      const icon = document.getElementById('modalIcon');
      const title = document.getElementById('modalTitle');
      const desc = document.getElementById('modalDesc');
      const receipt = document.getElementById('modalReceipt');
      const actions = document.getElementById('modalActions');

      if (isSuccess) {
        icon.className = 'modal-icon success';
        icon.innerText = '✓';
        title.innerText = 'Order Authorized & Confirmed';
        desc.innerText = 'Transaction committed across local mock microservices with zero errors.';
        receipt.innerHTML = `
          <div><strong>ORDER ID:</strong> ${data.order_id}</div>
          <div><strong>TRANSACTION:</strong> ${data.transaction_id} (${data.payment?.status || 'authorized'})</div>
          <div><strong>SHIPPING:</strong> ${data.shipping?.carrier} (Tracking: ${data.shipping?.tracking_number})</div>
          <div><strong>PERSISTENCE:</strong> <span style="color:#10B981;font-weight:700;">${data.database}</span></div>
          <div><strong>ROUTING:</strong> ${data.routing?.ingress} ➔ ${data.routing?.compute} (${data.routing?.latency_ms}ms)</div>
        `;
        actions.innerHTML = `
          <button class="btn-modal-action" style="background:#10B981;color:#042F2E;font-weight:800;" onclick="closeModal()">
            Done & Continue Shopping
          </button>
        `;
      } else {
        icon.className = 'modal-icon error';
        icon.innerText = '✕';
        const code = data.code || 502;
        title.innerText = `Checkout Failed (HTTP ${code})`;
        desc.innerText = 'Real-time transaction aborted due to an active infrastructure anomaly in the mock cloud topology.';
        receipt.innerHTML = `
          <div><strong style="color:#EF4444;">ERROR SIGNATURE:</strong></div>
          <div style="color:#EF4444;word-break:break-all;margin:4px 0 8px;font-weight:700;">${data.error || 'Connection refused'}</div>
          <div><strong>FAILING SERVICE:</strong> ${data.service || 'checkout-api'}</div>
          <div><strong>CLUSTER:</strong> ${data.cluster || 'Multi-Cloud Topology'}</div>
          <div style="margin-top:10px;padding-top:10px;border-top:1px dashed #334155;color:#38BDF8;">
            <strong>⚡ AUTONOMOUS SRE:</strong> Lear Copilot has captured this telemetry trace. Trigger autonomous healing below to diagnose and restore service.
          </div>
        `;
        actions.innerHTML = `
          <div style="display:flex;gap:10px;">
            <button class="btn-modal-action" style="background:#EF4444;color:#FFF;flex:1;" onclick="triggerAutoFix()">
              🧠 Trigger Lear AI Auto-Fix
            </button>
            <button class="btn-modal-action" style="background:#334155;color:#E2E8F0;width:100px;" onclick="closeModal()">
              Dismiss
            </button>
          </div>
        `;
      }

      modal.classList.add('active');
    }

    function closeModal() {
      document.getElementById('resultModal').classList.remove('active');
    }

    // Trigger AI Auto-Fix directly from Storefront
    async function triggerAutoFix() {
      const btn = document.getElementById('btnBannerHeal');
      if (btn) {
        btn.disabled = true;
        btn.innerText = '🧠 Lear AI Diagnosing & Healing...';
      }

      try {
        const res = await fetch('/api/demo/ai-fix', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        const data = await res.json();
        
        closeModal();
        pollSystemHealth();

        // Add success line in feed
        const feed = document.getElementById('orderFeed');
        const itemEl = document.createElement('div');
        itemEl.className = 'feed-item';
        itemEl.style.borderColor = 'rgba(16, 185, 129, 0.6)';
        itemEl.innerHTML = `
          <div class="feed-header">
            <span class="feed-user" style="color:#34D399;">🧠 Lear AI (${data.inference_model || 'DeepSeek'}) Auto-Heal</span>
            <span class="feed-badge" style="background:#10B981;color:#042F2E;">RESOLVED</span>
          </div>
          <div class="feed-body" style="color:#E2E8F0;font-size:11px;">
            ${data.inference_diagnosis ? data.inference_diagnosis.slice(0, 140) + '...' : 'All services restored to 100% HEALTHY.'}
          </div>
        `;
        feed.insertBefore(itemEl, feed.firstChild);
      } catch (e) {
        console.error('AI Fix error', e);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerText = '🧠 Trigger Lear AI Auto-Fix';
        }
      }
    }

    // Toggle Simulated Traffic Stream
    function toggleSimulation() {
      simulationActive = !simulationActive;
      const icon = document.getElementById('simIcon');
      const text = document.getElementById('simText');
      if (simulationActive) {
        icon.innerText = '⏸';
        text.innerText = 'Pause Traffic Sim';
        startSimulation();
      } else {
        icon.innerText = '▶';
        text.innerText = 'Resume Traffic Sim';
        stopSimulation();
      }
    }

    function startSimulation() {
      if (simInterval) clearInterval(simInterval);
      simInterval = setInterval(() => {
        if (!simulationActive) return;
        runSingleSimulatedTransaction();
      }, 3200);
    }

    function stopSimulation() {
      if (simInterval) {
        clearInterval(simInterval);
        simInterval = null;
      }
    }

    async function runSingleSimulatedTransaction() {
      const buyer = SIMULATED_BUYERS[Math.floor(Math.random() * SIMULATED_BUYERS.length)];
      const product = PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)];

      try {
        const res = await fetch('/api/demo/customer-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            item: product.name,
            price: product.price,
            customer: buyer
          })
        });
        const data = await res.json();
        recordOrderInFeed(buyer, product, res.ok && data.status === 'COMPLETED', data);
      } catch (e) {
        recordOrderInFeed(buyer, product, false, { error: e.message, code: 504 });
      }
    }

    // Poll live mock system health every 3s
    async function pollSystemHealth() {
      try {
        const res = await fetch('/api/demo/status');
        if (!res.ok) return;
        const data = await res.json();

        const banner = document.getElementById('outageBanner');
        const headerDot = document.getElementById('headerDot');
        const headerText = document.getElementById('headerStatusText');
        const latencyVal = document.getElementById('valLatency');

        const hasOutage = !data.elb_healthy || (data.chaos_state && (data.chaos_state.active_error || data.chaos_state.gateway_timeout));

        if (hasOutage) {
          banner.classList.add('active');
          headerDot.className = 'pulse-dot error';
          headerText.innerText = 'OUTAGE DETECTED: Customer Transactions Failing';
          headerText.style.color = '#F87171';
          latencyVal.innerText = (data.latency_ms || 1850) + 'ms';
          latencyVal.style.color = '#F87171';

          let outTitle = 'CRITICAL OUTAGE ACTIVE';
          let outDesc = 'Checkout pipeline degraded.';
          if (data.latest_incident && data.latest_incident.title && data.latest_incident.status !== 'RESOLVED') {
            outTitle = data.latest_incident.title;
            outDesc = data.latest_incident.diagnosis || data.latest_incident.error_summary || outDesc;
          }
          document.getElementById('outageTitle').innerText = outTitle;
          document.getElementById('outageDesc').innerText = outDesc;
        } else {
          banner.classList.remove('active');
          headerDot.className = 'pulse-dot';
          headerText.innerText = 'All Microservices Operational (p99: 18ms)';
          headerText.style.color = '#CBD5E1';
          latencyVal.innerText = '18ms';
          latencyVal.style.color = '#FFF';
          resetPipelineSteps();
        }
      } catch (e) {}
    }

    // Initialization
    window.addEventListener('DOMContentLoaded', () => {
      renderProducts(PRODUCTS);
      startSimulation();
      pollSystemHealth();
      setInterval(pollSystemHealth, 3000);
    });
  </script>
</body>
</html>
"""

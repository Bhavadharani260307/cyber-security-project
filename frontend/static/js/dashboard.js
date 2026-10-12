/**
 * Dashboard Real-Time Visualizer
 */

let trafficStatusChart = null;
let attackCategoryChart = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardStats();
  setInterval(fetchDashboardStats, 10000); // Auto refresh every 10 sec
});

async function fetchDashboardStats() {
  try {
    const response = await fetch("/api/dashboard/statistics");
    if (!response.ok) return;

    const data = await response.json();

    // Update Summary Metrics
    document.getElementById("val-total-traffic").innerText = data.total_traffic.toLocaleString();
    document.getElementById("val-normal-traffic").innerText = data.normal_traffic.toLocaleString();
    document.getElementById("val-attacks-detected").innerText = data.attacks_detected.toLocaleString();
    document.getElementById("val-detection-rate").innerText = `${data.detection_rate}%`;

    // Render Charts
    renderTrafficStatusChart(data.normal_traffic, data.suspicious_traffic, data.malicious_traffic);
    renderAttackCategoryChart(data.attack_distribution);

    // Render Recent Alerts Table
    renderRecentAlertsTable(data.recent_alerts);
  } catch (err) {
    console.error("Failed to load dashboard statistics:", err);
  }
}

function renderTrafficStatusChart(normal, suspicious, malicious) {
  const ctx = document.getElementById("trafficStatusChart").getContext("2d");

  if (trafficStatusChart) {
    trafficStatusChart.destroy();
  }

  trafficStatusChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Normal", "Suspicious", "Malicious"],
      datasets: [
        {
          data: [normal, suspicious, malicious],
          backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
          borderColor: "#121929",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#94a3b8" } },
      },
    },
  });
}

function renderAttackCategoryChart(attackDist) {
  const ctx = document.getElementById("attackCategoryChart").getContext("2d");

  const labels = Object.keys(attackDist);
  const counts = Object.values(attackDist);

  if (attackCategoryChart) {
    attackCategoryChart.destroy();
  }

  attackCategoryChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Flow Count",
          data: counts,
          backgroundColor: "#06b6d4",
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e2d4a" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e2d4a" } },
      },
    },
  });
}

function renderRecentAlertsTable(alerts) {
  const tbody = document.getElementById("recent-alerts-tbody");
  tbody.innerHTML = "";

  if (!alerts || alerts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">No threat alerts recorded yet.</td></tr>`;
    return;
  }

  alerts.forEach((alert) => {
    const sevClass = getSeverityBadgeClass(alert.severity);
    const dateStr = alert.created_at ? new Date(alert.created_at).toLocaleString() : "N/A";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>#${alert.id}</td>
      <td class="small text-muted">${dateStr}</td>
      <td><code>${alert.source_ip}</code></td>
      <td><code>${alert.destination_ip}</code></td>
      <td><span class="fw-bold text-white">${alert.attack_type}</span></td>
      <td><span class="badge badge-sev ${sevClass}">${alert.severity}</span></td>
      <td>${(alert.confidence * 100).toFixed(1)}%</td>
      <td><span class="badge bg-secondary">${alert.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function getSeverityBadgeClass(sev) {
  switch (sev) {
    case "LOW": return "badge-sev-low";
    case "MEDIUM": return "badge-sev-medium";
    case "HIGH": return "badge-sev-high";
    case "CRITICAL": return "badge-sev-critical";
    default: return "badge-sev-medium";
  }
}

/* ============================================================
   DASHBOARD SCRIPTS
   This file is loaded after Chart.js from the template.

   Jinja variables used — DO NOT rename:
     chart_labels, chart_scores   → line chart
     risk_labels, risk_values     → doughnut chart
   ============================================================ */

/* ── SOC table score bars (unchanged behavior) ── */
document.querySelectorAll('.soc-score-fill').forEach((bar) => {
  const score = parseFloat(bar.dataset.score) || 0;
  bar.style.width = score + '%';
});

(function () {
  'use strict';

    // ===========================
    // Continuous Verification Box
    // ===========================

    const textarea = document.getElementById("verificationInput");

    if (textarea) {

        textarea.addEventListener("paste", (e) => e.preventDefault());

        textarea.addEventListener("copy", (e) => e.preventDefault());

        textarea.addEventListener("cut", (e) => e.preventDefault());

    }

  /* ----------------------------------------------------------
     DESIGN TOKENS
     Mirror the CSS custom properties so Chart.js instances
     match the rest of the dashboard without reading computed
     styles at runtime (avoids a layout-recalc on init).
  ---------------------------------------------------------- */
  const T = {
    cyan: '#34e5c4',
    cyanDim: '#1f8f7c',
    amber: '#ffb454',
    amberDim: '#7a5326',
    rose: '#ff6b81',
    roseDim: '#7a2e3a',
    line: '#1f2a35',
    textDim: '#8b98a5',
    panel: '#10151c',
    card: '#11161d',
    mono: 'ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace',
    fill0: 'rgba(52,229,196,0.16)',
    fillN: 'rgba(52,229,196,0.00)',
  };

  function riskColor(label) {
    const l = (label || '').toUpperCase();
    if (l === 'LOW') return T.cyan;
    if (l === 'MEDIUM') return T.amber;
    if (l === 'HIGH') return T.rose;
    return T.textDim;
  }

  function riskColorDim(label) {
    const l = (label || '').toUpperCase();
    if (l === 'LOW') return T.cyanDim;
    if (l === 'MEDIUM') return T.amberDim;
    if (l === 'HIGH') return T.roseDim;
    return T.line;
  }

  (function buildLineChart() {
    const labelsNode = document.getElementById('chart-data-labels');
    const valuesNode = document.getElementById('chart-data-values');
    const labels = labelsNode ? JSON.parse(labelsNode.textContent) : [];
    const values = valuesNode
      ? JSON.parse(valuesNode.textContent).map((v) => Number(v) || 0)
      : [];

    const canvas = document.getElementById('scoreChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, T.fill0);
    gradient.addColorStop(1, T.fillN);

    const tip = document.createElement('div');
    tip.className = 'viz-tooltip';
    tip.style.opacity = '0';
    canvas.parentNode.style.position = 'relative';
    canvas.parentNode.appendChild(tip);

    const externalTooltip = ({ tooltip }) => {
      if (tooltip.opacity === 0) {
        tip.style.opacity = '0';
        return;
      }
      const point = tooltip.dataPoints[0];
      const label = tooltip.title[0] || '';
      const value = point ? point.formattedValue : '';
      tip.innerHTML =
        `<div class="viz-tooltip-time">${label}</div>` +
        `<div class="viz-tooltip-value">${value}%</div>`;
      tip.style.left = `${tooltip.caretX}px`;
      tip.style.top = `${tooltip.caretY}px`;
      tip.style.opacity = '1';
    };

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            data: values,
            borderColor: T.cyan,
            borderWidth: 1.8,
            pointRadius: 3.5,
            pointHoverRadius: 6,
            pointBackgroundColor: T.card,
            pointBorderColor: T.cyan,
            pointBorderWidth: 1.8,
            pointHoverBackgroundColor: T.cyan,
            pointHoverBorderColor: T.cyan,
            fill: true,
            backgroundColor: gradient,
            tension: 0.38,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 700, easing: 'easeInOutQuart' },
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false, external: externalTooltip },
        },
        scales: {
          x: {
            border: { display: false },
            grid: { color: T.line, lineWidth: 1, drawTicks: false },
            ticks: {
              color: T.textDim,
              font: { family: T.mono, size: 10 },
              maxRotation: 0,
              padding: 8,
              maxTicksLimit: 7,
            },
          },
          y: {
            min: 0,
            suggestedMax: 100,
            border: { display: false },
            grid: { color: T.line, lineWidth: 1, drawTicks: false },
            ticks: {
              color: T.textDim,
              font: { family: T.mono, size: 10 },
              padding: 10,
              stepSize: 20,
              callback: (value) => value + '%',
            },
          },
        },
      },
    });
  })();

  (function buildDonutChart() {
    const labelsNode = document.getElementById('risk-data-labels');
    const valuesNode = document.getElementById('risk-data-values');
    const labels = labelsNode ? JSON.parse(labelsNode.textContent) : [];
    const values = valuesNode
      ? JSON.parse(valuesNode.textContent).map((v) => Number(v) || 0)
      : [];

    const canvas = document.getElementById('riskChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const total = values.reduce((sum, value) => sum + value, 0) || 1;
    const colors = labels.map(riskColor);
    const hoverColors = labels.map((label) => riskColor(label) + '40');

    let dominantIndex = 0;
    values.forEach((value, index) => {
      if (value > values[dominantIndex]) dominantIndex = index;
    });
    const dominantLabel = labels[dominantIndex] || '—';
    const dominantPct = total > 0 ? Math.round((values[dominantIndex] / total) * 100) : 0;

    const pctEl = document.getElementById('donutPct');
    const lblEl = document.getElementById('donutLbl');
    if (pctEl) pctEl.textContent = `${dominantPct}%`;
    if (lblEl) {
      lblEl.textContent = dominantLabel;
      lblEl.style.color = riskColor(dominantLabel);
    }

    const legendEl = document.getElementById('riskLegend');
    if (legendEl) {
      legendEl.innerHTML = labels
        .map((label, index) => {
          const pct = Math.round((values[index] / total) * 100);
          const color = riskColor(label);
          return `
            <div class="viz-legend-item">
              <div class="viz-legend-left">
                <span class="viz-legend-swatch" style="background:${color};box-shadow:0 0 6px ${color}55;"></span>
                <span class="viz-legend-name">${label}</span>
              </div>
              <div class="viz-legend-right">
                <span class="viz-legend-val">${values[index]}</span>
                <div class="viz-legend-bar">
                  <div class="viz-legend-bar-fill" style="width:${pct}%;background:${color};"></div>
                </div>
              </div>
            </div>`;
        })
        .join('');
    }

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: colors.map((c) => c + '26'),
            borderColor: colors,
            hoverBackgroundColor: hoverColors,
            hoverBorderColor: colors,
            borderWidth: 2,
            hoverBorderWidth: 2.5,
            spacing: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '70%',
        animation: { duration: 800, easing: 'easeInOutQuart' },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: T.panel,
            borderColor: T.cyanDim,
            borderWidth: 1,
            titleColor: T.textDim,
            bodyColor: T.cyan,
            titleFont: { family: T.mono, size: 10 },
            bodyFont: { family: T.mono, size: 14, weight: '700' },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              title: (items) => items[0].label.toUpperCase(),
              label: (item) => ' ' + item.formattedValue + ' logins',
            },
          },
        },
        onHover: (event, elements, chart) => {
          chart.data.datasets[0].hoverOffset = elements.length ? 6 : 0;
        },
      },
    });
  })();
  /* ==========================================================
   CONTINUOUS SESSION VERIFICATION
========================================================== */

const verifyBtn = document.getElementById("verifySessionBtn");

if (verifyBtn) {

    verifyBtn.addEventListener("click", async function () {

        if (!window.behaviorData) {
            alert("Please type the verification phrase first.");
            return;
        }

        try {

            const response = await fetch("/continuous_check", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    hold_time: window.behaviorData.avgHold,
                    flight_time: window.behaviorData.avgFlight,
                    typing_speed: window.behaviorData.typingSpeed
                })
            });

            const result = await response.json();
            console.log(result);
            console.log(result.prediction);
            console.log(result.risk_level);

            document.getElementById("liveHoldTime").textContent =
                result.hold_time.toFixed(2);

            document.getElementById("liveFlightTime").textContent =
                result.flight_time.toFixed(2);

            document.getElementById("liveTypingSpeed").textContent =
                result.typing_speed.toFixed(2);

            document.getElementById("sessionTrustScore").innerHTML =
                result.behavior_score.toFixed(2) +
                '<span class="unit">%</span>';

            const prediction = document.getElementById("sessionPrediction");
            prediction.textContent = result.prediction;
            prediction.className = "status-badge";
            prediction.classList.add(
                result.prediction === "Normal"
                    ? "status-normal"
                    : "status-anomaly"
            );

            const risk = document.getElementById("sessionRisk");
            risk.textContent = result.risk_level;
            risk.className = "status-badge";
            risk.classList.add(
                result.risk_level === "LOW"
                    ? "risk-low"
                    : "risk-high"
            );

            document.getElementById("lastVerification").textContent =
                new Date().toLocaleTimeString();
            // Logout if continuous verification fails

            if (result.behavior_score < 60) {

                alert(
                      "Suspicious behavior detected.\nYou will be logged out."
                );

                window.location.href = "/logout";
            }

            console.log(result);

        } catch (err) {

            console.error(err);

        }

    });

}
})();

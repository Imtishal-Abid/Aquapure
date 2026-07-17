let currentPredictionData = null;

document.addEventListener("DOMContentLoaded", async () => {
  // Navigation Logic
  const navItems = document.querySelectorAll(".nav-item");
  const views = document.querySelectorAll(".view-section");

  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      // Remove active class from all
      navItems.forEach(n => n.classList.remove("active"));
      views.forEach(v => v.classList.remove("active"));
      
      // Add active class to clicked item and target view
      item.classList.add("active");
      const targetId = item.getAttribute("data-target");
      document.getElementById(targetId).classList.add("active");
    });
  });

  // Fetch metrics and render charts
  try {
    const response = await fetch("http://127.0.0.1:5000/metrics");
    if (!response.ok) throw new Error("Failed to fetch metrics");
    const metrics = await response.json();
    
    renderComparisonChart(metrics);
    renderIndividualCharts(metrics);

  } catch (err) {
    console.error("Chart error:", err);
  }
});

function renderComparisonChart(metrics) {
  const ctx = document.getElementById('metricsChart').getContext('2d');
  
  // X-axis will be the metrics
  const labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score'];
  
  // Vibrant color for each classifier
  const classifierColors = {
    'svm': '#8B5CF6', // Vibrant Purple
    'knn': '#06B6D4', // Bright Cyan
    'nn': '#EC4899',  // Hot Pink
    'nb': '#F59E0B'   // Amber
  };
  
  const classifierNames = {
    'svm': 'Support Vector Machine (SVM)',
    'knn': 'K-Nearest Neighbors (KNN)',
    'nn': 'Neural Network (MLP)',
    'nb': 'Naive Bayes'
  };

  const datasets = ['svm', 'knn', 'nn', 'nb'].map(model => {
    return {
      label: classifierNames[model],
      backgroundColor: classifierColors[model],
      data: [
        metrics[model].accuracy,
        metrics[model].precision,
        metrics[model].recall,
        metrics[model].f1score
      ]
    };
  });

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      // Zoomed-in y-axis (0.4–1.0) so real differences between models are visible
      scales: { y: { beginAtZero: false, min: 0.4, max: 1.0 } }
    }
  });
}

function renderIndividualCharts(metrics) {
  const modelMap = {
    'svm': 'chart-svm',
    'knn': 'chart-knn',
    'nn': 'chart-nn',
    'nb': 'chart-nb'
  };

  const labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score'];
  
  // Consistent metric colors with the comparison chart (with some opacity for the radar chart)
  const backgroundColors = [
    'rgba(59, 130, 246, 0.35)',  // Blue
    'rgba(16, 185, 129, 0.35)',  // Emerald
    'rgba(245, 158, 11, 0.35)',  // Amber
    'rgba(244, 63, 94, 0.35)'    // Rose
  ];
  
  const borderColors = [
    '#3B82F6',
    '#10B981',
    '#F59E0B',
    '#F43F5E'
  ];

  for (const [key, canvasId] of Object.entries(modelMap)) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const data = [
      metrics[key].accuracy,
      metrics[key].precision,
      metrics[key].recall,
      metrics[key].f1score
    ];

    new Chart(ctx, {
      // Switched from 'polarArea' to 'radar' — polarArea encodes value as
      // area, which visually exaggerates small differences; radar is a more
      // honest, easier-to-read representation for this kind of comparison.
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Score',
          data: data,
          backgroundColor: 'rgba(79, 70, 229, 0.2)',
          borderColor: '#4F46E5',
          pointBackgroundColor: borderColors,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#4F46E5',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        // Zoomed-in scale (0.4–1.0) so the four models are visually
        // distinguishable instead of all looking like flat quarter-circles
        scales: { r: { min: 0.4, max: 1.0 } }
      }
    });
  }
}

document.getElementById("predict-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  document.getElementById("result-icon").textContent = data.prediction === 1 ? "✅" : "❌";
    document.getElementById("result-label").textContent = data.prediction === 1 ? "Potable" : "Not Potable";
    document.getElementById("result-confidence").textContent = `Confidence: ${data.confidence}%`;
    document.getElementById("result-model").textContent = `Model used: ${data.model_used}`;

    // Animate the confidence bar fill
    const fill = document.getElementById("confidence-bar-fill");
    fill.style.width = "0%";
    requestAnimationFrame(() => {
      setTimeout(() => { fill.style.width = `${data.confidence}%`; }, 50);
    });
  const form = e.target;
  const payload = {
    ph:               parseFloat(form.ph.value),
    Hardness:         parseFloat(form.Hardness.value),
    Solids:           parseFloat(form.Solids.value),
    Chloramines:      parseFloat(form.Chloramines.value),
    Sulfate:          parseFloat(form.Sulfate.value),
    Conductivity:     parseFloat(form.Conductivity.value),
    Organic_carbon:   parseFloat(form.Organic_carbon.value),
    Trihalomethanes:  parseFloat(form.Trihalomethanes.value),
    Turbidity:        parseFloat(form.Turbidity.value),
    model:            form.model.value
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    currentPredictionData = data;

    const resultBox = document.getElementById("result-box");
    resultBox.classList.remove("hidden", "potable", "not-potable");
    resultBox.classList.add(data.prediction === 1 ? "potable" : "not-potable");

    document.getElementById("result-label").textContent = data.prediction === 1 ? "✅ Potable" : "❌ Not Potable";
    document.getElementById("result-confidence").textContent = `Confidence: ${data.confidence}%`;
    document.getElementById("result-model").textContent = `Model used: ${data.model_used}`;

  } catch (err) {
    document.getElementById("error-box").classList.remove("hidden");
    document.getElementById("error-message").textContent = "Error: " + err.message;
  }
});

document.getElementById("btn-store").addEventListener("click", async () => {
  if (!currentPredictionData) return;
  try {
    const response = await fetch("http://127.0.0.1:5000/store", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentPredictionData)
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    
    const msg = document.getElementById("store-message");
    msg.textContent = "Result saved to database successfully!";
    msg.classList.remove("hidden");
  } catch (err) {
    alert("Failed to store data: " + err.message);
  }
});

document.getElementById("btn-report").addEventListener("click", async () => {
  try {
    const response = await fetch("http://127.0.0.1:5000/report");
    if (!response.ok) throw new Error("Failed to generate report");
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Water_Potability_Report.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (err) {
    alert("Error generating report: " + err.message);
  }
});
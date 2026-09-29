/**
 * 🌱 AgriSmart — Vanilla JavaScript Core
 * Handles responsive sidebar, dropdowns, Chart.js graphs, drag-and-drop file uploads,
 * real-time 7-day agricultural weather forecast refresh, and green theme chart renderers.
 */

let activeTempChart = null;
let activeRainChart = null;
let activeWindChart = null;
let activeHumidityChart = null;
let activeDashboardChart = null;

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initDropdowns();
  initToastCloser();
  initRangeSliders();
  initFileUploadDropzone();
  initWeatherRefresh();
});

/* ==========================================================================
   Sidebar & Mobile Drawer
   ========================================================================== */
function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const closeSidebarBtn = document.getElementById('closeSidebarBtn');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (hamburgerBtn) hamburgerBtn.addEventListener('click', openSidebar);
  if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeSidebar);
  if (backdrop) backdrop.addEventListener('click', closeSidebar);
}

/* ==========================================================================
   Header Dropdowns
   ========================================================================== */
function initDropdowns() {
  const profileTrigger = document.getElementById('userProfileTrigger');
  const profileDropdown = document.getElementById('userProfileDropdown');
  const notifTrigger = document.getElementById('notifTrigger');
  const notifDropdown = document.getElementById('notifDropdown');

  function toggleDropdown(dropdown) {
    if (!dropdown) return;
    const isShown = dropdown.classList.contains('show');
    closeAllDropdowns();
    if (!isShown) dropdown.classList.add('show');
  }

  function closeAllDropdowns() {
    if (profileDropdown) profileDropdown.classList.remove('show');
    if (notifDropdown) notifDropdown.classList.remove('show');
  }

  if (profileTrigger && profileDropdown) {
    profileTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleDropdown(profileDropdown);
    });
  }

  if (notifTrigger && notifDropdown) {
    notifTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleDropdown(notifDropdown);
    });
  }

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-panel') && !e.target.closest('.user-profile-menu') && !e.target.closest('.notif-wrapper')) {
      closeAllDropdowns();
    }
  });
}

/* ==========================================================================
   Toast / Alert Closer
   ========================================================================== */
function initToastCloser() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', function() {
      const alert = this.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });
}

/* ==========================================================================
   Range Sliders with Dynamic Value Badges
   ========================================================================== */
function initRangeSliders() {
  document.querySelectorAll('.slider-input').forEach(slider => {
    const targetId = slider.getAttribute('data-target');
    const badge = document.getElementById(targetId);
    if (badge) {
      slider.addEventListener('input', (e) => {
        badge.textContent = e.target.value;
      });
    }
  });
}

/* ==========================================================================
   Drag & Drop Image Uploader
   ========================================================================== */
function initFileUploadDropzone() {
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('leafImageInput');
  const previewContainer = document.getElementById('uploadPreviewContainer');
  const previewImage = document.getElementById('uploadPreviewImg');
  const previewName = document.getElementById('uploadFileName');
  const placeholderBox = document.getElementById('uploadPlaceholder');

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFilePreview(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFilePreview(e.target.files[0]);
    }
  });

  function handleFilePreview(file) {
    if (!file.type.match('image.*')) {
      alert('Please select a valid image file (JPG, PNG, WEBP)');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (previewImage) previewImage.src = e.target.result;
      if (previewName) previewName.textContent = file.name;
      if (placeholderBox) placeholderBox.style.display = 'none';
      if (previewContainer) previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}

/* ==========================================================================
   🌱 Global Location State & Real-Time Weather Fetcher
   ========================================================================== */
const DEFAULT_LOCATION = {
  city: "Patna",
  state: "Bihar",
  country: "India",
  latitude: 25.5941,
  longitude: 85.1376
};

function getStoredLocation() {
  try {
    const raw = localStorage.getItem('selectedLocation');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.latitude && parsed.longitude) {
        return parsed;
      }
    }
  } catch (e) {
    console.error('Error reading selectedLocation from localStorage', e);
  }
  return DEFAULT_LOCATION;
}

function saveStoredLocation(loc) {
  try {
    localStorage.setItem('selectedLocation', JSON.stringify(loc));
  } catch (e) {
    console.error('Error saving selectedLocation to localStorage', e);
  }
}

function initWeatherRefresh() {
  const locSelect = document.getElementById('globalLocationSelect');
  const storedLoc = getStoredLocation();

  if (locSelect) {
    // Set selected option in navbar dropdown
    let matched = false;
    for (let i = 0; i < locSelect.options.length; i++) {
      const opt = locSelect.options[i];
      const optLat = parseFloat(opt.getAttribute('data-lat'));
      const optLon = parseFloat(opt.getAttribute('data-lon'));
      if (Math.abs(optLat - storedLoc.latitude) < 0.01 && Math.abs(optLon - storedLoc.longitude) < 0.01) {
        locSelect.selectedIndex = i;
        matched = true;
        break;
      }
    }

    if (!matched) {
      // Fallback match by city name
      for (let i = 0; i < locSelect.options.length; i++) {
        if (locSelect.options[i].value.toLowerCase().includes(storedLoc.city.toLowerCase())) {
          locSelect.selectedIndex = i;
          break;
        }
      }
    }

    // Add change listener to navbar location dropdown
    locSelect.addEventListener('change', () => {
      const selectedOpt = locSelect.options[locSelect.selectedIndex];
      const lat = parseFloat(selectedOpt.getAttribute('data-lat'));
      const lon = parseFloat(selectedOpt.getAttribute('data-lon'));
      const city = selectedOpt.getAttribute('data-city') || '';
      const state = selectedOpt.getAttribute('data-state') || '';
      const country = selectedOpt.getAttribute('data-country') || 'India';

      const newLoc = {
        city: city,
        state: state,
        country: country,
        latitude: lat,
        longitude: lon
      };

      saveStoredLocation(newLoc);

      // Dispatch global event for any listening components
      window.dispatchEvent(new CustomEvent('agriSmartLocationChanged', { detail: newLoc }));

      // Automatically fetch weather data for the new coordinates
      fetchWeatherDataByCoords(lat, lon);
    });
  }

  // Automatic fetch on page load
  autoRefreshWeatherOnLoad(storedLoc);
}

function autoRefreshWeatherOnLoad(loc) {
  const hasWeatherCanvas = document.getElementById('weatherTempChartCanvas') || document.getElementById('dashboardWeatherChartCanvas');
  const hasHeroTemp = document.querySelector('.live-weather-temp');

  if (hasWeatherCanvas || hasHeroTemp) {
    fetchWeatherDataByCoords(loc.latitude, loc.longitude);
  }
}

function fetchWeatherDataByCoords(lat, lon) {
  const loadingBanner = document.getElementById('weatherLoadingState');
  if (loadingBanner) loadingBanner.style.display = 'flex';

  const errBox = document.getElementById('weatherErrorMessage');
  if (errBox) errBox.style.display = 'none';

  fetch(`/api/weather?lat=${lat}&lon=${lon}`)
    .then(res => res.json())
    .then(data => {
      if (loadingBanner) loadingBanner.style.display = 'none';

      if (!data.success) {
        showWeatherError(data.error || 'Weather forecast temporarily unavailable.');
        return;
      }

      updateWeatherDOM(data);
    })
    .catch(err => {
      if (loadingBanner) loadingBanner.style.display = 'none';
      showWeatherError('Weather forecast temporarily unavailable. Please check connection.');
    });
}

function showWeatherError(msg) {
  const errBox = document.getElementById('weatherErrorMessage');
  if (errBox) {
    const span = errBox.querySelector('span');
    if (span) span.textContent = msg;
    errBox.style.display = 'flex';
  }
}

function updateWeatherDOM(data) {
  const curr = data.current;
  if (!curr) return;
  
  // Current Location name
  document.querySelectorAll('.live-weather-location').forEach(el => {
    el.textContent = data.location || curr.location || '';
  });

  // Current Local Date
  document.querySelectorAll('.live-weather-date').forEach(el => {
    el.textContent = curr.local_date_display || data.local_date_display || '';
  });

  // Current Temperature
  document.querySelectorAll('.live-weather-temp span:first-child').forEach(el => {
    el.textContent = curr.temperature;
  });

  // Feels Like & min/max
  document.querySelectorAll('.live-weather-feels').forEach(el => {
    el.textContent = `Feels like ${curr.feels_like}°C • Min: ${curr.temp_min}°C / Max: ${curr.temp_max}°C`;
  });

  // Condition Description
  document.querySelectorAll('.live-weather-cond').forEach(el => {
    el.textContent = curr.description || curr.condition;
  });

  // Condition Icon
  if (curr.icon_url) {
    document.querySelectorAll('.live-weather-icon-img').forEach(img => {
      img.src = curr.icon_url;
      img.alt = curr.condition || 'Weather';
    });
  }

  // Humidity
  document.querySelectorAll('.live-weather-humidity').forEach(el => {
    el.textContent = `${curr.humidity}%`;
  });

  // Wind Speed
  document.querySelectorAll('.live-weather-wind').forEach(el => {
    el.textContent = `${curr.wind_speed} m/s`;
  });

  // Pressure
  document.querySelectorAll('.live-weather-pressure').forEach(el => {
    el.textContent = `${curr.pressure} hPa`;
  });

  // Rain Probability
  document.querySelectorAll('.live-weather-rain').forEach(el => {
    if (curr.rain_probability !== null && curr.rain_probability !== undefined) {
      el.textContent = `${curr.rain_probability}%`;
    } else {
      el.textContent = '0%';
    }
  });

  // Last Updated
  document.querySelectorAll('.live-weather-updated').forEach(el => {
    el.innerHTML = `<i class="fa-regular fa-clock" style="margin-right: 4px;"></i> Last updated: ${data.last_updated || 'Just now'}`;
  });

  // 🌿 Update 3 Visual Analytics Panels
  const charts = data.seven_day_charts || data.chart_data;
  if (charts && charts.labels && charts.labels.length > 0) {
    if (document.getElementById('temperatureTrendCanvas') && window.renderTemperatureTrendChart) {
      window.renderTemperatureTrendChart('temperatureTrendCanvas', charts);
    }
  }

  // Update Rain Probability progress bars
  const rainList = document.getElementById('rainProgressList');
  if (rainList && data.forecast && data.forecast.length > 0) {
    rainList.innerHTML = data.forecast.map(f => `
      <div class="progress-day-row">
        <span class="progress-date-lbl">${f.display_date}</span>
        <div class="progress-track">
          <div class="progress-fill-bar" style="width: ${f.rain_probability}%;"></div>
        </div>
        <span class="progress-pct-val">${f.rain_probability}%</span>
      </div>
    `).join('');
  }

  // Update Humidity Trend progress bars
  const humList = document.getElementById('humidityProgressList');
  if (humList && data.forecast && data.forecast.length > 0) {
    humList.innerHTML = data.forecast.map(f => `
      <div class="progress-day-row">
        <span class="progress-date-lbl">${f.display_date}</span>
        <div class="progress-track">
          <div class="progress-fill-bar" style="width: ${f.humidity}%;"></div>
        </div>
        <span class="progress-pct-val">${f.humidity}%</span>
      </div>
    `).join('');
  }

  // 🌿 Update 7-Day Forecast Cards
  if (data.forecast && data.forecast.length > 0) {
    const cardsRow = document.querySelector('.forecast-cards-row');
    if (cardsRow) {
      cardsRow.innerHTML = data.forecast.map(f => `
        <div class="forecast-card">
          <div class="forecast-day">${f.day}</div>
          <div style="font-size: 0.76rem; color: var(--primary); font-weight: 700;">${f.display_date}</div>
          <div class="forecast-icon" style="margin: 2px 0;">
            ${f.icon_url ? `<img src="${f.icon_url}" alt="${f.condition}" style="width: 44px; height: 44px; margin: 0 auto;">` : `<i class="${f.fa_icon}"></i>`}
          </div>
          <div class="forecast-temp">
            <span>${f.temp_max}°</span>
            <span style="color: var(--text-light); font-size: 0.85rem; font-weight: normal;">/ ${f.temp_min}°</span>
          </div>
          <div class="forecast-rain">
            <i class="fa-solid fa-droplet" style="font-size: 0.7rem;"></i> ${f.rain_probability}% Rain
          </div>
          <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 2px;">
            Hum: ${f.humidity}%
          </div>
          <div style="font-size: 0.7rem; color: var(--primary); font-weight: 600; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">
            ${f.condition}
          </div>
        </div>
      `).join('');
    }
  }

  // 🌿 Update Rule-Based Agriculture Advisories
  if (data.advisories) {
    const adv = data.advisories;
    if (adv.rain) {
      const rainHead = document.getElementById('advisoryRainHeadline');
      const rainBadge = document.getElementById('advisoryRainBadge');
      const rainPts = document.getElementById('advisoryRainPoints');
      if (rainHead) rainHead.textContent = adv.rain.headline;
      if (rainBadge) {
        rainBadge.className = `badge ${adv.rain.badge_class}`;
        rainBadge.textContent = adv.rain.level;
      }
      if (rainPts && adv.rain.points) {
        rainPts.innerHTML = adv.rain.points.map(p => `<li>${p}</li>`).join('');
      }
    }
    if (adv.irrigation) {
      const irrHead = document.getElementById('advisoryIrrigationHeadline');
      const irrBadge = document.getElementById('advisoryIrrigationBadge');
      const irrPts = document.getElementById('advisoryIrrigationPoints');
      if (irrHead) irrHead.textContent = adv.irrigation.headline;
      if (irrBadge) {
        irrBadge.className = `badge ${adv.irrigation.badge_class}`;
        irrBadge.textContent = adv.irrigation.level;
      }
      if (irrPts && adv.irrigation.points) {
        irrPts.innerHTML = adv.irrigation.points.map(p => `<li>${p}</li>`).join('');
      }
    }
    if (adv.temperature) {
      const tempHead = document.getElementById('advisoryTempHeadline');
      const tempBadge = document.getElementById('advisoryTempBadge');
      const tempPts = document.getElementById('advisoryTempPoints');
      if (tempHead) tempHead.textContent = adv.temperature.headline;
      if (tempBadge) {
        tempBadge.className = `badge ${adv.temperature.badge_class}`;
        tempBadge.textContent = adv.temperature.level;
      }
      if (tempPts && adv.temperature.points) {
        tempPts.innerHTML = adv.temperature.points.map(p => `<li>${p}</li>`).join('');
      }
    }
    if (adv.wind) {
      const windHead = document.getElementById('advisoryWindHeadline');
      const windBadge = document.getElementById('advisoryWindBadge');
      const windPts = document.getElementById('advisoryWindPoints');
      if (windHead) windHead.textContent = adv.wind.headline;
      if (windBadge) {
        windBadge.className = `badge ${adv.wind.badge_class}`;
        windBadge.textContent = adv.wind.level;
      }
      if (windPts && adv.wind.points) {
        windPts.innerHTML = adv.wind.points.map(p => `<li>${p}</li>`).join('');
      }
    }
  }

  // Re-render Dashboard chart if on dashboard
  if (document.getElementById('dashboardWeatherChartCanvas') && charts) {
    window.renderDashboardWeatherChart('dashboardWeatherChartCanvas', charts);
  }
}

/* ==========================================================================
   🌱 3 VISUAL ANALYTICS PANELS (Chart.js & Dynamic Progress Renderers)
   ========================================================================== */

let activeTempTrendChart = null;

/**
 * Visual Panel 1: Temperature Trend (Line Chart with Max Temp & Min Temp)
 */
window.renderTemperatureTrendChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeTempTrendChart) {
    activeTempTrendChart.destroy();
  }

  const gradientMax = ctx.createLinearGradient(0, 0, 0, 180);
  gradientMax.addColorStop(0, 'rgba(21, 128, 61, 0.22)');
  gradientMax.addColorStop(0.8, 'rgba(134, 239, 172, 0.04)');
  gradientMax.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  const maxData = chartData.temp_max || chartData.temperatures;
  const minData = chartData.temp_min || chartData.feels_like;

  activeTempTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels, // 7 dynamic calendar dates (e.g. 26 Sep, 27 Sep...)
      datasets: [
        {
          label: 'Max Temp',
          data: maxData,
          borderColor: '#15803D', // Dark green primary
          backgroundColor: gradientMax,
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: '#166534',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 5
        },
        {
          label: 'Min Temp',
          data: minData,
          borderColor: '#65A30D', // Lighter green from the same family
          borderDash: [4, 4],
          fill: false,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#65A30D',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 3.5,
          pointHoverRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            boxWidth: 6,
            boxHeight: 6,
            font: { family: 'Inter', size: 11, weight: 600 },
            color: '#166534',
            padding: 8
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          titleFont: { family: 'Inter', size: 12, weight: 700 },
          bodyFont: { family: 'Inter', size: 11 },
          padding: 8,
          cornerRadius: 6,
          callbacks: {
            label: (c) => ` ${c.dataset.label}: ${c.raw}°C`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 10, weight: 600 }, color: '#475569' }
        },
        y: {
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 10 }, color: '#475569', callback: (v) => v + '°' }
        }
      }
    }
  });
};

/**
 * CHART 1: 7-Day Temperature Forecast (Line Chart with Real Data & Green Palette)
 */
window.render7DayTemperatureChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeTempChart) {
    activeTempChart.destroy();
  }

  // Create subtle vertical green gradient fill
  const gradientFill = ctx.createLinearGradient(0, 0, 0, 260);
  gradientFill.addColorStop(0, 'rgba(21, 128, 61, 0.22)');
  gradientFill.addColorStop(0.7, 'rgba(134, 239, 172, 0.08)');
  gradientFill.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  activeTempChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels, // 7 dynamic calendar dates (e.g. 26 Sep, 27 Sep...)
      datasets: [
        {
          label: 'Temperature (°C)',
          data: chartData.temperatures,
          borderColor: '#15803d', // Dark green primary
          backgroundColor: gradientFill,
          fill: true,
          tension: 0.35,
          borderWidth: 2.8,
          pointBackgroundColor: '#166534',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Feels Like (°C)',
          data: chartData.feels_like,
          borderColor: '#22c55e', // Medium fresh green
          borderDash: [5, 4],
          fill: false,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#22c55e',
          pointRadius: 3.5,
          pointHoverRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534'
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          titleFont: { family: 'Inter', size: 13, weight: 700 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (c) => ` ${c.dataset.label}: ${c.raw}°C`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11, weight: 500 }, color: '#475569' }
        },
        y: {
          title: { display: true, text: 'Temperature (°C)', font: { size: 11, weight: 600 }, color: '#166534' },
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569' }
        }
      }
    }
  });
};

/**
 * CHART 2: 7-Day Rain Probability (Bar Chart with Green Gradient Bars)
 */
window.render7DayRainChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeRainChart) {
    activeRainChart.destroy();
  }

  // Create green gradient for bars (Darker green at top -> lighter green at bottom)
  const barGradient = ctx.createLinearGradient(0, 0, 0, 240);
  barGradient.addColorStop(0, '#15803d');
  barGradient.addColorStop(0.5, '#22c55e');
  barGradient.addColorStop(1, '#86efac');

  activeRainChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Rain Probability (%)',
          data: chartData.rain_probabilities,
          backgroundColor: barGradient,
          borderColor: '#166534',
          borderWidth: 1.5,
          borderRadius: 8,
          borderSkipped: false,
          hoverBackgroundColor: '#166534'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534'
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (c) => ` Rain Probability: ${c.raw}%`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11, weight: 500 }, color: '#475569' }
        },
        y: {
          min: 0,
          max: 100,
          title: { display: true, text: 'Probability (%)', font: { size: 11, weight: 600 }, color: '#166534' },
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569', stepSize: 20 }
        }
      }
    }
  });
};

/**
 * CHART 3: 7-Day Wind Speed (Line Chart in km/h with Green Palette)
 */
window.render7DayWindChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeWindChart) {
    activeWindChart.destroy();
  }

  const windGradient = ctx.createLinearGradient(0, 0, 0, 260);
  windGradient.addColorStop(0, 'rgba(22, 101, 52, 0.2)');
  windGradient.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  activeWindChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Wind Speed (km/h)',
          data: chartData.wind_speeds,
          borderColor: '#166534',
          backgroundColor: windGradient,
          fill: true,
          tension: 0.35,
          borderWidth: 2.6,
          pointBackgroundColor: '#15803d',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534'
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (c) => ` Wind Speed: ${c.raw} km/h`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11, weight: 500 }, color: '#475569' }
        },
        y: {
          title: { display: true, text: 'Speed (km/h)', font: { size: 11, weight: 600 }, color: '#166534' },
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569' }
        }
      }
    }
  });
};

/**
 * CHART 4: 7-Day Humidity Forecast (Line Chart with Green Area Fill)
 */
window.render7DayHumidityChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeHumidityChart) {
    activeHumidityChart.destroy();
  }

  const humGradient = ctx.createLinearGradient(0, 0, 0, 260);
  humGradient.addColorStop(0, 'rgba(34, 197, 94, 0.22)');
  humGradient.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  activeHumidityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Relative Humidity (%)',
          data: chartData.humidities,
          borderColor: '#22c55e',
          backgroundColor: humGradient,
          fill: true,
          tension: 0.35,
          borderWidth: 2.6,
          pointBackgroundColor: '#15803d',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534'
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (c) => ` Humidity: ${c.raw}%`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11, weight: 500 }, color: '#475569' }
        },
        y: {
          min: 0,
          max: 100,
          title: { display: true, text: 'Humidity (%)', font: { size: 11, weight: 600 }, color: '#166534' },
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569', stepSize: 20 }
        }
      }
    }
  });
};

/**
 * Dashboard 7-Day Summary Chart
 */
window.renderDashboardWeatherChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeDashboardChart) {
    activeDashboardChart.destroy();
  }

  const gradientFill = ctx.createLinearGradient(0, 0, 0, 260);
  gradientFill.addColorStop(0, 'rgba(21, 128, 61, 0.2)');
  gradientFill.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  activeDashboardChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: chartData.temperatures || chartData.temp_max,
          borderColor: '#15803d',
          backgroundColor: gradientFill,
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: '#166534',
          pointRadius: 4,
          yAxisID: 'y'
        },
        {
          label: 'Rain Probability (%)',
          data: chartData.rain_probabilities || chartData.rain_prob,
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#22c55e',
          pointRadius: 3.5,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534'
          }
        },
        tooltip: {
          backgroundColor: '#166534',
          titleFont: { family: 'Inter', size: 13, weight: 700 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569' }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: { display: true, text: 'Temperature (°C)', font: { size: 11, weight: 600 }, color: '#166534' },
          grid: { color: '#eef6f0' },
          ticks: { font: { family: 'Inter', size: 11 }, color: '#475569' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: { display: true, text: 'Precipitation (%)', font: { size: 11, weight: 600 }, color: '#22c55e' },
          grid: { drawOnChartArea: false },
          min: 0,
          max: 100,
          ticks: { font: { family: 'Inter', size: 11 }, color: '#22c55e' }
        }
      }
    }
  });
};

let activeMandiChart = null;

window.renderMandiPriceChart = function(canvasId, chartData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !window.Chart) return;
  const ctx = canvas.getContext('2d');

  if (activeMandiChart) {
    activeMandiChart.destroy();
  }

  // Subtle vertical green gradient for the emphasized modal price benchmark
  const gradientModal = ctx.createLinearGradient(0, 0, 0, 280);
  gradientModal.addColorStop(0, 'rgba(21, 128, 61, 0.24)');
  gradientModal.addColorStop(0.7, 'rgba(134, 239, 172, 0.08)');
  gradientModal.addColorStop(1, 'rgba(220, 252, 231, 0.0)');

  const fullLabels = chartData.full_labels || chartData.labels;

  activeMandiChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels, // 24 monthly points: Jan 2025 -> Dec 2026
      datasets: [
        {
          label: 'Modal (Benchmark) Price',
          data: chartData.modal_prices,
          borderColor: '#15803d', // Bold primary dark green (visually emphasized)
          backgroundColor: gradientModal,
          fill: true,
          tension: 0.35,
          borderWidth: 3.2,
          pointBackgroundColor: '#166534',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1.5,
          pointRadius: 4,
          pointHoverRadius: 6.5,
          order: 1
        },
        {
          label: 'Maximum Price',
          data: chartData.max_prices,
          borderColor: '#047857', // Deep emerald green
          borderDash: [5, 4],
          fill: false,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#047857',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1,
          pointRadius: 3,
          pointHoverRadius: 5,
          order: 2
        },
        {
          label: 'Minimum Price',
          data: chartData.min_prices,
          borderColor: '#65a30d', // Olive/lime green in same family
          borderDash: [4, 4],
          fill: false,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#65a30d',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1,
          pointRadius: 3,
          pointHoverRadius: 5,
          order: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            usePointStyle: true,
            boxWidth: 8,
            boxHeight: 8,
            font: { family: 'Inter', size: 12, weight: 600 },
            color: '#166534',
            padding: 12
          }
        },
        tooltip: {
          backgroundColor: '#14532d',
          titleFont: { family: 'Inter', size: 13, weight: 700 },
          bodyFont: { family: 'Inter', size: 12 },
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            title: function(items) {
              if (items.length > 0) {
                const idx = items[0].dataIndex;
                return fullLabels[idx] || items[0].label;
              }
              return '';
            },
            label: function(context) {
              return ` ${context.dataset.label}: ₹${Number(context.raw).toLocaleString('en-IN')}/Qtl`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: '#f0fdf4', display: true },
          ticks: {
            font: { family: 'Inter', size: 10, weight: 600 },
            color: '#475569',
            maxRotation: 45,
            minRotation: 0,
            autoSkip: false
          }
        },
        y: {
          title: {
            display: true,
            text: 'Price (₹/Quintal)',
            font: { family: 'Inter', size: 11, weight: 700 },
            color: '#166534'
          },
          grid: { color: '#eef6f0' },
          ticks: {
            font: { family: 'Inter', size: 11 },
            color: '#475569',
            callback: function(v) {
              return '₹' + Number(v).toLocaleString('en-IN');
            }
          }
        }
      }
    }
  });
};

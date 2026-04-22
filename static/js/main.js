// Main JavaScript for AirWatch

document.addEventListener('DOMContentLoaded', function() {
    console.log('AirWatch Django initialized');
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Active nav link based on current page
    updateActiveNav();
    
    // Initialize charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});

function updateActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

function initializeCharts() {
    // Add your chart initialization code here
    console.log('Charts initialized');
}

// API helper
async function fetchStationData(stationId) {
    try {
        const response = await fetch(`/api/station/${stationId}/data/`);
        const data = await response.json();
        console.log('Station data:', data);
        return data;
    } catch (error) {
        console.error('Error fetching station data:', error);
    }
}

// Animate elements on scroll
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.card, .pollutant-item, .health-card').forEach(element => {
        observer.observe(element);
    });
}

observeElements();

// ---------------------------------------------------------------------------
// Live data polling — mise à jour automatique depuis MySQL toutes les 30s
// ---------------------------------------------------------------------------

const POLL_INTERVAL = 30000; // 30 secondes

function formatTime(date) {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function setLastUpdated(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.textContent = ' — Mis à jour à ' + formatTime(new Date());
}

// Tableau "Dernières mesures" (index.html)
function refreshLatestData() {
    const tbody = document.getElementById('live-data-tbody');
    if (!tbody) return;

    fetch('/api/latest/')
        .then(r => r.json())
        .then(data => {
            if (!data.measurements || data.measurements.length === 0) return;

            let html = '';
            data.measurements.forEach(m => {
                const rowClass = m.over_limit ? 'class="row-over-limit"' : '';
                html += `<tr ${rowClass}>
                    <td>${m.station}</td>
                    <td>${m.pollutant}</td>
                    <td>${m.value} ${m.unit}</td>
                    <td>${m.limit_oms} ${m.unit}</td>
                    <td>${m.date}</td>
                </tr>`;
            });
            tbody.innerHTML = html;
            setLastUpdated('last-updated');
        })
        .catch(() => {}); // silently fail if offline
}

// Tableau "Statistiques par polluant" (data.html)
function refreshPollutantStats() {
    const tbody = document.getElementById('live-stats-tbody');
    if (!tbody) return;

    fetch('/api/pollutant-stats/')
        .then(r => r.json())
        .then(data => {
            if (!data.stats || data.stats.length === 0) return;

            let html = '';
            data.stats.forEach(s => {
                html += `<tr>
                    <td>${s.symbol} - ${s.name}</td>
                    <td>${s.avg} μg/m³</td>
                    <td>${s.max} μg/m³</td>
                    <td>${s.min} μg/m³</td>
                </tr>`;
            });
            tbody.innerHTML = html;
            setLastUpdated('last-updated-stats');
        })
        .catch(() => {});
}

// Démarrer le polling si les éléments sont présents
document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('live-data-tbody')) {
        setLastUpdated('last-updated');
        setInterval(refreshLatestData, POLL_INTERVAL);
    }
    if (document.getElementById('live-stats-tbody')) {
        setLastUpdated('last-updated-stats');
        setInterval(refreshPollutantStats, POLL_INTERVAL);
    }

    // Auto-dismiss messages after 5s
    setTimeout(() => {
        document.querySelectorAll('.message').forEach(el => {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 500);
        });
    }, 5000);
});

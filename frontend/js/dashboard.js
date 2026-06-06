/**
 * dashboard.js — Graphiques Chart.js DB + JSON
 */

const API = 'http://127.0.0.1:8000';

const COLORS = [
    '#1565C0','#0288D1','#00ACC1','#00897B',
    '#43A047','#7B1FA2','#E53935','#F57C00',
    '#FDD835','#6D4C41','#546E7A','#1E88E5'
];

let chartClasses, chartSources, chartMoyennes, chartTop10;

async function loadAll() {
    await Promise.all([
        loadKPI(),
        loadClassesChart(),
        loadSourcesChart(),
        loadMoyennesChart(),
        loadTop10Chart(),
    ]);
}

// ── KPI ────────────────────────────────────────────────────
async function loadKPI() {
    try {
        const res  = await fetch(`${API}/stats`);
        const data = await res.json();
        console.log('KPI data:', data);

        document.getElementById('kpi-total').textContent =
            data.total ?? '—';
        document.getElementById('kpi-actifs').textContent =
            data.actifs ?? '—';
        document.getElementById('kpi-archives').textContent =
            data.archives ?? '—';
        document.getElementById('kpi-moyenne').textContent =
            data.moyenne_globale ? data.moyenne_globale + '/20' : '—';
        document.getElementById('kpi-db').textContent =
            data.source_db ?? '—';
        document.getElementById('kpi-json').textContent =
            data.source_json ?? '—';
    } catch(e) {
        console.error('Erreur KPI:', e);
    }
}

// ── Répartition par classe ─────────────────────────────────
async function loadClassesChart() {
    try {
        const res    = await fetch(`${API}/stats/classes`);
        const data   = await res.json();
        const labels = data.map(d => d.classe);
        const values = data.map(d => d.total);

        if (chartClasses) chartClasses.destroy();
        const ctx = document.getElementById('chart-classes').getContext('2d');
        chartClasses = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Étudiants',
                    data: values,
                    backgroundColor: COLORS,
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 },
                         grid: { color: '#EEF2F7' } },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch(e) { console.error('Erreur classes chart:', e); }
}

// ── Sources DB vs JSON ─────────────────────────────────────
async function loadSourcesChart() {
    try {
        const res  = await fetch(`${API}/stats/sources`);
        const data = await res.json();

        const labels = data.map(d => d.source === 'db' ? 'Base de données' : 'JSON');
        const values = data.map(d => d.total);

        if (chartSources) chartSources.destroy();
        const ctx = document.getElementById('chart-sources').getContext('2d');
        chartSources = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#1565C0', '#00ACC1'],
                    borderWidth: 3,
                    borderColor: '#fff',
                    hoverOffset: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 20, font: { size: 12 } }
                    }
                }
            }
        });
    } catch(e) { console.error('Erreur sources chart:', e); }
}

// ── Moyenne par classe ─────────────────────────────────────
async function loadMoyennesChart() {
    try {
        const res    = await fetch(`${API}/stats/classes`);
        const data   = await res.json();
        const labels = data.map(d => d.classe);
        const values = data.map(d => parseFloat(d.moyenne) || 0);

        if (chartMoyennes) chartMoyennes.destroy();
        const ctx = document.getElementById('chart-moyennes').getContext('2d');
        chartMoyennes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Moyenne',
                    data: values,
                    backgroundColor: values.map(v =>
                        v >= 14 ? '#2E7D32' : v >= 10 ? '#F57C00' : '#C62828'
                    ),
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, max: 20,
                         grid: { color: '#EEF2F7' },
                         ticks: { callback: v => v + '/20' } },
                    y: { grid: { display: false } }
                }
            }
        });
    } catch(e) { console.error('Erreur moyennes chart:', e); }
}

// ── Top 10 ─────────────────────────────────────────────────
async function loadTop10Chart() {
    try {
        const res  = await fetch(`${API}/stats/top10`);
        const data = await res.json();

        const labels = data.map(d => `${d.prenom} ${d.nom}`);
        const values = data.map(d => parseFloat(d.moyenne_generale));

        if (chartTop10) chartTop10.destroy();
        const ctx = document.getElementById('chart-top10').getContext('2d');
        chartTop10 = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Moyenne',
                    data: values,
                    backgroundColor: values.map((_, i) =>
                        i === 0 ? '#FDD835' :
                        i === 1 ? '#B0BEC5' :
                        i === 2 ? '#8D6E63' : '#1565C0'
                    ),
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: false, min: 10, max: 20,
                         grid: { color: '#EEF2F7' },
                         ticks: { callback: v => v + '/20' } },
                    x: { grid: { display: false },
                         ticks: { maxRotation: 30, font: { size: 11 } } }
                }
            }
        });
    } catch(e) { console.error('Erreur top10 chart:', e); }
}

document.addEventListener('DOMContentLoaded', loadAll);

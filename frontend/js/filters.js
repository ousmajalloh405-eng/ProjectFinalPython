/**
 * filters.js — État global et logique principale
 */

// État global de l'application
const state = {
    page:    1,
    perPage: 5,
    search:  '',
    classe:  '',
    source:  '',
    archive: false,
};

// Charge et affiche les données
async function loadData() {
    const params = {
        page:     state.page,
        per_page: state.perPage,
        archive:  state.archive,
    };
    if (state.search) params.search = state.search;
    if (state.classe) params.classe = state.classe;
    if (state.source) params.source = state.source;

    try {
        const result = await fetchEtudiants(params);
        renderTable(result.data);
        renderPagination(result.total, result.page, result.per_page, result.pages);
        document.getElementById('table-count').textContent =
            `${result.total} étudiant(s) trouvé(s)`;
    } catch(e) {
        document.getElementById('table-body').innerHTML =
            `<tr><td colspan="9" class="empty">Erreur : ${e.message}</td></tr>`;
    }
}

// Charge les classes dans le select filtre
async function loadClasses() {
    try {
        const classes = await fetchClasses();
        const select  = document.getElementById('filter-classe');
        classes.forEach(c => {
            const opt = document.createElement('option');
            opt.value       = c;
            opt.textContent = c;
            select.appendChild(opt);
        });
    } catch(e) { console.error('Erreur classes:', e); }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {

    loadClasses();
    loadData();

    // Recherche avec délai (évite trop d'appels API)
    let timer;
    document.getElementById('search-input').addEventListener('input', e => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            state.search = e.target.value;
            state.page   = 1;
            loadData();
        }, 400);
    });

    // Filtre classe
    document.getElementById('filter-classe').addEventListener('change', e => {
        state.classe = e.target.value;
        state.page   = 1;
        loadData();
    });

    // Filtre source
    document.getElementById('filter-source').addEventListener('change', e => {
        state.source = e.target.value;
        state.page   = 1;
        loadData();
    });

    // Toggle archives
    document.getElementById('toggle-archives').addEventListener('change', e => {
        state.archive = e.target.checked;
        state.page    = 1;
        loadData();
    });

    // Lignes par page
    document.getElementById('per-page-select').addEventListener('change', e => {
        state.perPage = parseInt(e.target.value);
        state.page    = 1;
        loadData();
    });

    // ── Modal Ajout ────────────────────────────────────────
    const modalAjout = document.getElementById('modal-ajout');

    document.getElementById('btn-ajouter').addEventListener('click', () => {
        modalAjout.classList.add('open');
    });
    document.getElementById('modal-close').addEventListener('click', () => {
        modalAjout.classList.remove('open');
    });
    document.getElementById('btn-annuler').addEventListener('click', () => {
        modalAjout.classList.remove('open');
    });

    document.getElementById('form-ajout').addEventListener('submit', async e => {
        e.preventDefault();
        const errDiv = document.getElementById('form-error');
        errDiv.textContent = '';
        try {
            await createEtudiant({
                code:           document.getElementById('f-code').value.trim(),
                numero:         document.getElementById('f-numero').value.trim(),
                nom:            document.getElementById('f-nom').value.trim(),
                prenom:         document.getElementById('f-prenom').value.trim(),
                date_naissance: document.getElementById('f-date').value.trim() || null,
                classe:         document.getElementById('f-classe').value.trim() || null,
            });
            modalAjout.classList.remove('open');
            document.getElementById('form-ajout').reset();
            loadData();
        } catch(e) { errDiv.textContent = e.message; }
    });

    // ── Modal Import CSV ───────────────────────────────────
    const modalImport = document.getElementById('modal-import');

    document.getElementById('btn-import').addEventListener('click', async () => {
        modalImport.classList.add('open');
        const list = document.getElementById('import-list');
        list.innerHTML = 'Chargement...';
        try {
            const data = await fetchImportPreview();
            if (data.total === 0) {
                list.innerHTML = '<p>Tous les étudiants du CSV sont déjà en base.</p>';
                return;
            }
            list.innerHTML = `
                <table class="import-table">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="select-all"></th>
                            <th>Numéro</th>
                            <th>Nom</th>
                            <th>Prénom</th>
                            <th>Classe</th>
                            <th>Moyenne</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(e => `
                        <tr>
                            <td><input type="checkbox"
                                class="import-check" value="${e.numero}"></td>
                            <td>${e.numero}</td>
                            <td>${e.nom}</td>
                            <td>${e.prenom}</td>
                            <td>${e.classe || '—'}</td>
                            <td>${e.moyenne_generale || '—'}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>`;

            // Sélectionner tout
            document.getElementById('select-all').addEventListener('change', e => {
                document.querySelectorAll('.import-check')
                    .forEach(c => c.checked = e.target.checked);
            });

        } catch(e) { list.innerHTML = `Erreur : ${e.message}`; }
    });

    document.getElementById('import-close').addEventListener('click', () => {
        modalImport.classList.remove('open');
    });
    document.getElementById('import-annuler').addEventListener('click', () => {
        modalImport.classList.remove('open');
    });

    document.getElementById('btn-confirmer-import').addEventListener('click', async () => {
        const checks  = document.querySelectorAll('.import-check:checked');
        const numeros = [...checks].map(c => c.value);
        if (numeros.length === 0) {
            alert('Sélectionne au moins un étudiant.');
            return;
        }
        try {
            const result = await transferEtudiants(numeros);
            alert(result.message);
            modalImport.classList.remove('open');
            loadData();
        } catch(e) { alert(e.message); }
    });
});

// Charge les KPI dans la stats bar
async function loadStats() {
    try {
        const res  = await fetch('http://127.0.0.1:8000/stats');
        const data = await res.json();
        document.getElementById('stat-total').textContent   = data.total;
        document.getElementById('stat-actifs').textContent  = data.actifs;
        document.getElementById('stat-archives').textContent = data.archives;
        document.getElementById('stat-moyenne').textContent =
            data.moyenne_globale ? data.moyenne_globale + '/20' : '—';
    } catch(e) { console.error('Stats error:', e); }
}

loadStats();

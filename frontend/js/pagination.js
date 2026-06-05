/**
 * pagination.js — Gestion de la pagination
 */

function renderPagination(total, page, perPage, pages) {
    const info = document.getElementById('pagination-info');
    const ctrl = document.getElementById('pagination-controls');

    // Affiche "1–5 sur 94 étudiants"
    const debut = (page - 1) * perPage + 1;
    const fin   = Math.min(page * perPage, total);
    info.textContent = `${debut}–${fin} sur ${total} étudiants`;

    ctrl.innerHTML = '';

    // Bouton précédent
    const prev = document.createElement('button');
    prev.className   = 'page-btn';
    prev.textContent = '‹';
    prev.disabled    = page <= 1;
    prev.addEventListener('click', () => { state.page--; loadData(); });
    ctrl.appendChild(prev);

    // Boutons numérotés
    for (let i = 1; i <= pages; i++) {
        const btn = document.createElement('button');
        btn.className   = `page-btn ${i === page ? 'active' : ''}`;
        btn.textContent = i;
        btn.addEventListener('click', () => { state.page = i; loadData(); });
        ctrl.appendChild(btn);
    }

    // Bouton suivant
    const next = document.createElement('button');
    next.className   = 'page-btn';
    next.textContent = '›';
    next.disabled    = page >= pages;
    next.addEventListener('click', () => { state.page++; loadData(); });
    ctrl.appendChild(next);
}

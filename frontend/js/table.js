/**
 * table.js — Rendu du tableau avec modification au double-clic
 */

function classeMoyenne(moy) {
    if (!moy) return '';
    if (moy >= 14) return 'moyenne-high';
    if (moy >= 10) return 'moyenne-mid';
    return 'moyenne-low';
}

function renderRow(e) {
    const archived = e.est_archive;
    const isDB     = e.source === 'db';

    return `
    <tr class="${archived ? 'archived' : ''}" data-id="${e.id}">
        <td class="cell-editable ${isDB && !archived ? 'editable' : ''}"
            data-field="code" data-id="${e.id}" data-val="${e.code}">
            <span class="cell-text">${e.code}</span>
        </td>
        <td><strong>${e.numero}</strong></td>
        <td class="cell-editable ${isDB && !archived ? 'editable' : ''}"
            data-field="nom" data-id="${e.id}" data-val="${e.nom}">
            <span class="cell-text">${e.nom}</span>
        </td>
        <td class="cell-editable ${isDB && !archived ? 'editable' : ''}"
            data-field="prenom" data-id="${e.id}" data-val="${e.prenom}">
            <span class="cell-text">${e.prenom}</span>
        </td>
        <td class="cell-editable ${isDB && !archived ? 'editable' : ''}"
            data-field="date_naissance" data-id="${e.id}"
            data-val="${e.date_naissance || ''}">
            <span class="cell-text">${e.date_naissance || '—'}</span>
        </td>
        <td class="cell-editable ${isDB && !archived ? 'editable' : ''}"
            data-field="classe" data-id="${e.id}" data-val="${e.classe || ''}">
            <span class="cell-text">${e.classe || '—'}</span>
        </td>
        <td class="${classeMoyenne(e.moyenne_generale)}">
            ${e.moyenne_generale ? e.moyenne_generale.toFixed(2) : '—'}
        </td>
        <td>
            <span class="badge badge-${e.source}">
                ${e.source === 'db' ? 'DB' : 'JSON'}
            </span>
            ${archived ? '<span class="badge badge-archive">Archivé</span>' : ''}
        </td>
        <td>
            ${archived
                ? `<button class="btn btn-sm btn-secondary btn-restaurer"
                           data-id="${e.id}">↩ Restaurer</button>`
                : isDB
                    ? `<button class="btn btn-sm btn-danger btn-archiver"
                               data-id="${e.id}">🗄 Archiver</button>`
                    : '<span class="readonly-label">lecture seule</span>'
            }
        </td>
    </tr>`;
}

function renderTable(data) {
    const tbody = document.getElementById('table-body');
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty">Aucun résultat.</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(renderRow).join('');
    attachTableEvents();
}

function attachTableEvents() {

    // Double-clic pour modifier une cellule
    document.querySelectorAll('.cell-editable.editable').forEach(cell => {
        cell.title = 'Double-cliquez pour modifier';

        cell.addEventListener('dblclick', () => {
            if (cell.querySelector('input')) return; // déjà en édition

            const oldVal  = cell.dataset.val;
            const field   = cell.dataset.field;
            const id      = cell.dataset.id;
            const span    = cell.querySelector('.cell-text');

            // Remplace le texte par un input
            const input = document.createElement('input');
            input.value     = oldVal;
            input.className = 'inline-input';
            span.replaceWith(input);
            input.focus();
            input.select();

            // Sauvegarde quand on quitte le champ
            async function save() {
                const newVal = input.value.trim();
                const newSpan = document.createElement('span');
                newSpan.className = 'cell-text';

                if (newVal === oldVal) {
                    newSpan.textContent = oldVal || '—';
                    input.replaceWith(newSpan);
                    return;
                }

                try {
                    await updateEtudiant(id, { [field]: newVal });
                    cell.dataset.val    = newVal;
                    newSpan.textContent = newVal || '—';
                    input.replaceWith(newSpan);
                    showToast('✅ Modification enregistrée');
                } catch(e) {
                    newSpan.textContent = oldVal || '—';
                    input.replaceWith(newSpan);
                    showToast('❌ ' + e.message, 'error');
                }
            }

            input.addEventListener('blur', save);
            input.addEventListener('keydown', e => {
                if (e.key === 'Enter')  { input.blur(); }
                if (e.key === 'Escape') {
                    const s = document.createElement('span');
                    s.className   = 'cell-text';
                    s.textContent = oldVal || '—';
                    input.replaceWith(s);
                }
            });
        });
    });

    // Archiver
    document.querySelectorAll('.btn-archiver').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Archiver cet étudiant ?')) return;
            try {
                await archiveEtudiant(btn.dataset.id);
                showToast('✅ Étudiant archivé');
                loadData();
            } catch(e) { showToast('❌ ' + e.message, 'error'); }
        });
    });

    // Restaurer
    document.querySelectorAll('.btn-restaurer').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Restaurer cet étudiant ?')) return;
            try {
                await restaurerEtudiant(btn.dataset.id);
                showToast('✅ Étudiant restauré');
                loadData();
            } catch(e) { showToast('❌ ' + e.message, 'error'); }
        });
    });
}

// Notification toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

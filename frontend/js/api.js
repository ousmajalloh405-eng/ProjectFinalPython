/**
 * api.js — Toutes les fonctions de communication avec l'API
 */

const API = 'http://127.0.0.1:8000';

// GET /etudiants
async function fetchEtudiants(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res   = await fetch(`${API}/etudiants?${query}`);
    if (!res.ok) throw new Error('Erreur chargement étudiants');
    return res.json();
}

// GET /etudiants/classes
async function fetchClasses() {
    const res = await fetch(`${API}/etudiants/classes`);
    if (!res.ok) throw new Error('Erreur chargement classes');
    return res.json();
}

// POST /etudiants
async function createEtudiant(data) {
    const res = await fetch(`${API}/etudiants`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Erreur création');
    return json;
}

// PATCH /etudiants/{id}
async function updateEtudiant(id, data) {
    const res = await fetch(`${API}/etudiants/${id}`, {
        method:  'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Erreur modification');
    return json;
}

// PATCH /etudiants/{id}/archive
async function archiveEtudiant(id) {
    const res = await fetch(`${API}/etudiants/${id}/archive`, { method: 'PATCH' });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Erreur archivage');
    return json;
}

// PATCH /etudiants/{id}/restaurer
async function restaurerEtudiant(id) {
    const res = await fetch(`${API}/etudiants/${id}/restaurer`, { method: 'PATCH' });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Erreur restauration');
    return json;
}

// GET /import/preview
async function fetchImportPreview() {
    const res = await fetch(`${API}/import/preview`);
    if (!res.ok) throw new Error('Erreur preview import');
    return res.json();
}

// POST /import/transfer
async function transferEtudiants(numeros) {
    const res = await fetch(`${API}/import/transfer`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(numeros),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Erreur import');
    return json;
}

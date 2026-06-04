-- ============================================================
-- SCHEMA DE LA BASE DE DONNÉES - Projet Final P8
-- Auteur : Ton Nom
-- Date   : 2026
-- ============================================================

-- Suppression des tables si elles existent déjà (pour reset propre)
DROP TABLE IF EXISTS notes_devoir CASCADE;
DROP TABLE IF EXISTS matieres CASCADE;
DROP TABLE IF EXISTS etudiants CASCADE;

-- ============================================================
-- TABLE 1 : etudiants
-- Table principale — un enregistrement par étudiant
-- ============================================================
CREATE TABLE etudiants (
    id               SERIAL PRIMARY KEY,
    code             VARCHAR(20)  NOT NULL,
    numero           VARCHAR(20)  NOT NULL UNIQUE,
    nom              VARCHAR(100) NOT NULL,
    prenom           VARCHAR(100) NOT NULL,
    date_naissance   DATE,
    classe           VARCHAR(50),
    moyenne_generale NUMERIC(5,2),
    est_archive      BOOLEAN      NOT NULL DEFAULT FALSE,
    source           VARCHAR(10)  NOT NULL DEFAULT 'db',
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2 : matieres
-- Chaque étudiant peut avoir plusieurs matières
-- ============================================================
CREATE TABLE matieres (
    id               SERIAL PRIMARY KEY,
    etudiant_id      INTEGER      NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    nom_matiere      VARCHAR(100) NOT NULL,
    note_examen      NUMERIC(5,2),
    moyenne_matiere  NUMERIC(5,2)
);

-- ============================================================
-- TABLE 3 : notes_devoir
-- Chaque matière peut avoir plusieurs notes de devoir
-- ============================================================
CREATE TABLE notes_devoir (
    id          SERIAL PRIMARY KEY,
    matiere_id  INTEGER      NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    note        NUMERIC(5,2) NOT NULL,
    ordre       INTEGER      NOT NULL DEFAULT 1
);

-- ============================================================
-- INDEX — pour accélérer les recherches fréquentes
-- ============================================================
CREATE INDEX idx_etudiants_numero  ON etudiants(numero);
CREATE INDEX idx_etudiants_classe  ON etudiants(classe);
CREATE INDEX idx_etudiants_archive ON etudiants(est_archive);
CREATE INDEX idx_matieres_etudiant ON matieres(etudiant_id);

-- Message de confirmation
SELECT 'Schema créé avec succès !' AS message;

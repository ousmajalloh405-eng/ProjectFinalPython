<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=1565C0&center=true&vCenter=true&width=600&lines=🎓+Gestion+des+Étudiants;Projet+Final+P8;Full-Stack+Python+%26+Web" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Git](https://img.shields.io/badge/Git-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

<br/>

> **Application web full-stack professionnelle de gestion des étudiants**
> Développée avec FastAPI, PostgreSQL et JavaScript vanilla dans le cadre du Projet Final Intégrateur P8.

<br/>

[📋 Tableau Principal](#-fonctionnalités) • [📊 Dashboard](#-dashboard) • [🚀 Installation](#-installation) • [🔗 API](#-routes-api)

---

</div>

## ✨ Aperçu du projet

<div align="center">

### 📋 Tableau de gestion
*Interface principale — Recherche, filtres, pagination, modification inline, archivage*

┌─────────────────────────────────────────────────────────────────┐
│  🎓 Gestion des Étudiants          📋 Tableau   📊 Dashboard    │
├─────────────────────────────────────────────────────────────────┤
│  🔍 Rechercher...  [Classe ▼] [Source ▼]  [+ Ajouter] [⬆ CSV] │
├──────────┬──────────┬──────────┬─────────┬────────┬────────────┤
│   CODE   │  NUMÉRO  │   NOM    │ PRÉNOM  │MOYENNE │  ACTIONS   │
├──────────┼──────────┼──────────┼─────────┼────────┼────────────┤
│  AAD004  │ LIHGFR0  │  Diallo  │ Nourou  │ 12.51  │ 🗄 Archiver│
│  AAD005  │ 40DKG6T  │  Diallo  │   Awa   │ 15.39  │ 🗄 Archiver│
└──────────┴──────────┴──────────┴─────────┴────────┴────────────┘
│  ‹  1  2  3  ...  19  ›                        5 / page ▼      │
└─────────────────────────────────────────────────────────────────┘### 📊 Dashboard statistique
*Visualisation des données — KPI, graphiques Chart.js, Top 10*
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 👨‍🎓 Total │ │ ✅ Actifs │ │ 🗄 Archiv│ │ ⭐ Moy.  │ │ 🗄 DB   │ │ 📄 JSON  │
│    94    │ │    94    │ │    0     │ │12.51/20  │ │    94    │ │    0     │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
┌─────────────────────────┐  ┌─────────────────────────┐
│  👥 Répartition/classe  │  │  🗃 Source des données   │
│  ████ 3emA: 12         │  │      ●  DB: 94 (100%)   │
│  ██   3emB: 10         │  │      ○  JSON: 0 (0%)    │
│  ...                    │  │                          │
└─────────────────────────┘  └─────────────────────────┘</div>

---

## 🛠 Stack technique

<div align="center">

| Couche | Technologie | Rôle |
|:------:|:-----------:|:----:|
| 🐍 Backend | **Python 3 / FastAPI** | API REST performante |
| 🗄 Base de données | **PostgreSQL 16** | Stockage des données |
| 🌐 Frontend | **HTML5 / CSS3 / JS** | Interface utilisateur |
| 📊 Graphiques | **Chart.js** | Visualisation des données |
| 🔄 Versioning | **Git / GitHub** | Gestion du code source |

</div>

---

## 📁 Structure du projet
📦 ProjectFinalPython/
│
├── 🐍 backend/
│   ├── app/
│   │   ├── 📄 main.py           ← Point d'entrée FastAPI + CORS
│   │   ├── 📄 database.py       ← Connexion PostgreSQL
│   │   ├── routes/
│   │   │   ├── 📄 etudiants.py  ← CRUD complet
│   │   │   ├── 📄 stats.py      ← Statistiques & KPI
│   │   │   └── 📄 import_json.py← Import CSV → DB
│   │   └── models/
│   │       └── 📄 schemas.py    ← Modèles Pydantic
│   ├── 🔒 .env                  ← Variables d'environnement
│   └── 📄 requirements.txt      ← Dépendances Python
│
├── 🗄 database/
│   ├── 📄 schema.sql            ← Création des 3 tables
│   └── 📄 seed.py               ← Import initial CSV → DB
│
├── 📂 data/
│   └── 📊 eleves_valides.csv    ← Données sources (94 élèves)
│
├── 🌐 frontend/
│   ├── 📄 index.html            ← Tableau principal
│   ├── 📄 dashboard.html        ← Dashboard Chart.js
│   ├── css/
│   │   ├── 🎨 style.css         ← Design principal
│   │   └── 🎨 dashboard.css     ← Styles dashboard
│   └── js/
│       ├── ⚡ api.js             ← Communication API
│       ├── ⚡ table.js           ← Rendu tableau
│       ├── ⚡ pagination.js      ← Pagination
│       ├── ⚡ filters.js         ← Filtres & état global
│       └── ⚡ dashboard.js       ← Graphiques Chart.js
│
├── 🔧 scripts/
│   ├── ⚙️  setup.sh             ← Installation automatique
│   └── ▶️  run.sh               ← Lancement application
│
├── 📄 .gitignore
└── 📖 README.md---

## 🚀 Installation

### 📋 Prérequis

- ✅ Python 3.10+
- ✅ PostgreSQL 16
- ✅ Git

### ⚡ Démarrage rapide

**1️⃣ Cloner le projet**
```bash
git clone https://github.com/ousmajalloh405-eng/ProjectFinalPython.git
cd ProjectFinalPython
```

**2️⃣ Créer la base de données**
```bash
sudo -u postgres psql
```
```sql
CREATE USER p8_user WITH PASSWORD 'p8_password';
CREATE DATABASE p8_db OWNER p8_user;
GRANT ALL PRIVILEGES ON DATABASE p8_db TO p8_user;
\q
```

**3️⃣ Lancer l'installation automatique**
```bash
bash scripts/setup.sh
```

**4️⃣ Démarrer l'application**
```bash
bash scripts/run.sh
```

**5️⃣ Ouvrir l'interface**
🌐 Interface   → ouvre frontend/index.html dans le navigateur
📖 API Docs    → http://127.0.0.1:8000/docs
🔗 API Base    → http://127.0.0.1:8000---

## 🔗 Routes API

### 👨‍🎓 Étudiants
| Méthode | Route | Description |
|:-------:|:------|:------------|
| `GET` | `/etudiants` | Liste paginée avec filtres |
| `GET` | `/etudiants/{id}` | Détail complet avec matières |
| `GET` | `/etudiants/classes` | Liste des classes distinctes |
| `POST` | `/etudiants` | Créer un nouvel étudiant |
| `PATCH` | `/etudiants/{id}` | Modifier partiellement |
| `PATCH` | `/etudiants/{id}/archive` | Archiver un étudiant |
| `PATCH` | `/etudiants/{id}/restaurer` | Restaurer un archivé |

### 📊 Statistiques
| Méthode | Route | Description |
|:-------:|:------|:------------|
| `GET` | `/stats` | KPI globaux |
| `GET` | `/stats/classes` | Répartition par classe |
| `GET` | `/stats/top10` | Top 10 meilleures moyennes |
| `GET` | `/stats/sources` | Répartition DB vs JSON |

### 📥 Import
| Méthode | Route | Description |
|:-------:|:------|:------------|
| `GET` | `/import/preview` | Aperçu CSV non encore importé |
| `POST` | `/import/transfer` | Importer vers PostgreSQL |

---

## ✨ Fonctionnalités

### 📋 Tableau principal
- 🔍 **Recherche** par nom, prénom, numéro, code
- 🎯 **Filtres** par classe et par source (DB/JSON)
- 📄 **Pagination** configurable (5, 10, 25 lignes/page)
- ✏️ **Modification inline** au double-clic sur une cellule
- ➕ **Ajout** d'étudiants avec validation anti-doublon
- 🗄 **Archivage** et restauration
- 📥 **Import CSV** vers PostgreSQL depuis l'interface
- 🎨 **Couleurs** selon la moyenne (vert/orange/rouge)

### 📊 Dashboard
- 📈 **6 KPI cards** — Total, Actifs, Archivés, Moyenne, DB, JSON
- 📊 **Répartition par classe** — Graphique en barres
- 🍩 **Source des données** — Graphique donut
- 📉 **Moyenne par classe** — Barres horizontales colorées
- 🏆 **Top 10** — Podium des meilleures moyennes

### 🗄 Base de données
```sql
etudiants (94 enregistrements)
    └── matieres (557 enregistrements)
            └── notes_devoir (1143 enregistrements)
```

---

## 🗄 Schéma de base de données

```sql
TABLE etudiants
  id               SERIAL PRIMARY KEY
  code             VARCHAR(20)
  numero           VARCHAR(20) UNIQUE
  nom              VARCHAR(100)
  prenom           VARCHAR(100)
  date_naissance   DATE
  classe           VARCHAR(50)
  moyenne_generale NUMERIC(5,2)
  est_archive      BOOLEAN DEFAULT FALSE
  source           VARCHAR(10) DEFAULT 'db'
  created_at       TIMESTAMP DEFAULT NOW()

TABLE matieres
  id               SERIAL PRIMARY KEY
  etudiant_id      INTEGER REFERENCES etudiants(id)
  nom_matiere      VARCHAR(100)
  note_examen      NUMERIC(5,2)
  moyenne_matiere  NUMERIC(5,2)

TABLE notes_devoir
  id               SERIAL PRIMARY KEY
  matiere_id       INTEGER REFERENCES matieres(id)
  note             NUMERIC(5,2)
  ordre            INTEGER
```

---

## 👨‍💻 Auteur

<div align="center">

**Ousmane Jalloh**

[![GitHub](https://img.shields.io/badge/GitHub-ousmajalloh405--eng-181717?style=for-the-badge&logo=github)](https://github.com/ousmajalloh405-eng)

*Projet Final Intégrateur P8 — Développement Python & Web*
*Formation Développeur Full-Stack — 2026*

---

⭐ **N'oublie pas de mettre une étoile sur le dépôt si ce projet t'a aidé !** ⭐

</div>

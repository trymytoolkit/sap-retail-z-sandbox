# Inventaire des écrans de saisie — Backend Retail Z
### Extrait du code source (github.com/Koraeos/sap-retail-z-sandbox) — pour MyToolKit

Couvre les 24 entrées du launchpad `ZRET_R_LAUNCHPAD` (codes 010 → 055).
Lancement : programme via `/nSA38` → nom → **F8** (ou `/nSE38`) ; `ZGENART` est une transaction (`/nZGENART`).

**Notes de fiabilité :**
- Les **noms techniques** (P_xxx, SO_xxx, GV_xxx) sont extraits VERBATIM du code → fiables.
- Les **libellés affichés** dépendent des selection-texts (non présents dans le source) → colonne "Libellé" = rôle du champ, à confirmer à l'écran.
- `ZRET_R_OUTBOUND_DEMO` est documenté dans sa **version corrigée** (paramètres P_ART/P_SITE). Si le repo n'a pas encore reçu le push, l'ancienne version n'a pas d'écran.

**Valeurs de domaine utiles :**
- Article type : `HARD` / `SOFT` / `ACCE` / `CONS`
- Customer type : `M` (Store) / `W` (Web) / `B` (B2B) / `E` (Export)
- Site type : `S` (Store) / `W` (Warehouse)
- Statut commande (SO) : `O` Open / `D` Delivered / `B` Billed / `C` Cancelled
- Statut livraison : `C` Created / `S` Shipped / `R` Returned
- Statut facture : `O` / `P` / `V`
- Statut tâche entrepôt : `O` Open / `C` Confirmed / `X` Cancelled
- Statut PO : `O` / `I` / `D` / `C` / `X`

---

# 01 — Master Setup

## 010 · ZRET_R_ARTICLE_CREATE — Créer un article
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_ID | Article ID | zret_t_article-article_id | ✅ | — | Nouvel ID article (ex. ART201) |
| P_NAME | Article name | zret_t_article-article_name | ✅ | — | Libellé de l'article |
| P_TYPE | Article type | zret_t_article-article_type | ✅ | `HARD` | HARD / SOFT / ACCE / CONS |
| P_EAN | EAN | zret_t_article-ean | ❌ | — | Code EAN (13 chiffres) |
| P_UOM | Base UoM | zret_t_article-base_uom | ✅ | `PC` | Unité (PC…) |
| P_PRICE | Price | zret_t_article-price | ✅ | — | Prix (décimale = virgule sur ce système) |
| P_CURR | Currency | zret_t_article-currency | ✅ | `EUR` | Devise |

**Succès :** `Article <ID> created successfully` (S)
**Erreurs :** `Creation failed: article ID is missing` (E, ID vide) · `Creation failed for article <ID> (duplicate, invalid name/price, or DB error)` (E)

## 011 · ZRET_R_CUSTOMER_CREATE — Créer un client
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_ID | Customer ID | zret_t_customer-customer_id | ✅ | — | Nouvel ID client (ex. STORE003) |
| P_NAME | Customer name | zret_t_customer-customer_name | ✅ | — | Nom du client |
| P_TYPE | Customer type | zret_t_customer-customer_type | ✅ | `M` | M / W / B / E |
| P_CITY | City | zret_t_customer-city | ❌ | — | Ville |
| P_CNTRY | Country | zret_t_customer-country | ❌ | `FR` | Pays (ISO) |
| P_CURR | Default currency | zret_t_customer-default_currency | ❌ | `EUR` | Devise par défaut |

**Succès :** `Customer <ID> created successfully` (S)
**Erreur :** `Customer creation failed: invalid input, duplicate ID, or invalid type` (E)

## 012 · ZRET_R_SITE_CREATE — Créer un site
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_ID | Site ID | zret_t_site-site_id | ✅ | — | Nouvel ID site (ex. WH03) |
| P_NAME | Site name | zret_t_site-site_name | ✅ | — | Nom du site |
| P_TYPE | Site type | zret_t_site-site_type | ✅ | `S` | S (Store) / W (Warehouse) |
| P_ADDR | Address line | zret_t_site-address_line | ❌ | — | Adresse |
| P_CITY | City | zret_t_site-city | ❌ | — | Ville |
| P_CNTRY | Country | zret_t_site-country | ❌ | `FR` | Pays |

**Succès :** `Site <ID> created successfully` (S)
**Erreur :** `Site creation failed: invalid input, duplicate ID, or invalid type` (E)

## 013 · ZRET_R_SEED_SUPPLIERS — Seed 3 fournisseurs
**Écran de sélection : NON** (exécution directe)
**Succès :** `Suppliers seeded: <n> rows` (WRITE) · **Erreur :** `ERROR while inserting suppliers`

## 014 · ZRET_R_SEED_WHSE — Seed zones + stock initial
**Écran de sélection : NON** (exécution directe)
⚠️ **Limite :** charge du stock seulement pour les **4 premiers articles × 3 premiers sites**.
**Succès :** `Warehouse zones seeded: <n> rows` · `Stock 100 PC loaded - …` · **Erreurs :** `ERROR while inserting zones` · `ERROR loading stock for article <X> in site <Y>` · `No articles found …` · `No sites found …`

## 015 · ZRET_R_SEED_GENERIC — Seed articles génériques + variantes
**Écran de sélection : NON** — messages informatifs seulement (`GEN001 already exists or error - skipped`).

## 016 · ZRET_R_SEED_PARTNERS — Seed rôles partenaires B2B/B2C
**Écran de sélection : NON** — **Erreurs :** `Error creating customers` · `Error seeding partner functions.` · `Error in B2B scenario`

---

# 02 — Master Lists

## 020 · ZRET_R_ARTICLE_LIST — Liste des articles (ALV)
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| SO_TYPE | Article type (filtre) | SELECT-OPTIONS FOR zret_t_article-article_type | ❌ | — | Vide = tous ; ou HARD/SOFT/ACCE/CONS |
| P_ACTV | Actifs uniquement | CHECKBOX | ❌ | `X` | Coché = seulement les actifs |

**Messages :** `Aucun article trouvé` (I) · exception ALV (E)

## 021 · ZRET_R_GEN_ART_LIST — Articles génériques + variantes
**Écran de sélection : NON** — `No generic articles found in ZRET_T_GEN_ART` (I) · `No variants found for generic <ID>` (I) · exception (E)

## 022 · ZRET_R_CUST_PART_LIST — Matrice Client × fonctions partenaires
**Écran de sélection : NON** — exception ALV (E)

## 023 · ZGENART — Transaction Z "Create Generic Article" (dynpro 9000)
**Transaction** (`/nZGENART`) — module pool `ZRET_M_GEN_ART`, écran **9000**.

| Zone (technique) | Libellé écran | Oblig. | Quoi mettre |
|---|---|---|---|
| GV_ID | Generic_Article_ID | ✅ | ID générique (ex. GEN010) |
| GV_NAME | Name | ✅ | Nom |
| GV_TYPE | Article_Type | ❌ | HARD / SOFT / ACCE / CONS |
| GV_BASE_UOM | Base_UOM | ❌ | Unité (PC…) |
| GV_DESCRIPTION | Description | ❌ | Description libre |
| OK_CODE | (technique, invisible) | — | Rempli par les boutons |

**Boutons (STATUS_9000) :** SAVE / EXECUTE, DISPLAY, DELETE, RESET / CANCEL, BACK / EXIT.
**Messages :** `Generic ID and Name are required` (E) · `Generic Article <ID> created successfully` (S) · `Generic Article <ID> updated successfully` (S) · `Please enter a Generic Article ID first` (E) · `Generic Article <ID> not found` (W) · `Loaded <ID>` (S) · `Generic Article <ID> deactivated` (S) · `Cannot deactivate (active variants exist?)` (E) · `Error loading generic article` (E)

---

# 03 — Procurement

## 030 · ZRET_R_PO_DEMO — Créer PO + Réception (auto-Putaway)
**Écran de sélection : NON** (démo scriptée : 1er fournisseur, 2 premiers articles, site WH01)
**Messages :** `ERROR: No supplier in ZRET_T_SUPPLIER. Add one via SE16 first.` · `ERROR: Need at least 2 articles in ZRET_T_ARTICLE.` · `ERROR: Site WH01 not found in ZRET_T_SITE.` · `ERROR: <exception>`

## 031 · ZRET_R_PO_LIST — Liste des commandes d'achat (ALV)
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_PON | PO number | zret_t_po-po_number | ❌ | `''` | Vide = toutes les PO ; renseigné = postes de cette PO |

**Messages :** `No purchase orders found in ZRET_T_PO` (I) · `No items found for PO <n>` (I) · exception (E)

## 032 · ZRET_R_VINV_DEMO — Facture fournisseur (3-way match)
**Écran de sélection : NON** (démo scriptée)
**Messages :** `No PO found with goods receipt. Run ZRET_R_PO_DEMO first.` · `No delivered quantity yet. Run ZRET_R_PO_DEMO first to post a GR.` · `ERROR creating matching invoice` · `ERROR creating mismatching invoice`

## 033 · ZRET_R_VINV_LIST — Liste factures fournisseur (ALV)
**Écran de sélection : OUI** (bloc encadré B1)

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| S_VINV | Vendor invoice n° | SELECT-OPTIONS FOR vinv_number | ❌ | — | Filtre n° facture (vide = toutes) |
| S_STATUS | Status | SELECT-OPTIONS FOR status | ❌ | — | Filtre statut (M / B) |
| S_SUPP | Supplier | SELECT-OPTIONS FOR supplier_id | ❌ | — | Filtre fournisseur |

**Messages :** `No items found for vendor invoice <n>` (I) · exception (E)

---

# 04 — Warehouse

## 040 · ZRET_R_WH_TASK_LIST — Liste des tâches d'entrepôt (ALV)
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_STAT | Task status | zret_t_wh_task-status | ❌ | `''` | Vide = toutes ; O / C / X |

**Messages :** `No warehouse tasks found` (I) · exception (E) — 👉 repérer le n° de tâche Open pour le 041.

## 041 · ZRET_R_WH_TASK_CONFIRM — Confirmer une tâche
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_TASK | Warehouse task n° | zret_t_wh_task-wh_task_num | ✅ | — | Un n° de tâche **Open** (issu de 040) |

**Messages :** `ERROR: Task <n> not found` · `ERROR during confirm: <exception>` · sinon trace succès.

## 042 · ZRET_R_OUTBOUND_DEMO — Cycle Pick → Load → Goods Issue
**Écran de sélection : OUI** *(version corrigée)*

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_ART | Article | zret_t_stock-article_id | ✅ | `ART001` | Article ayant du **stock en STORAGE** (ex. ART101) |
| P_SITE | Site | zret_t_stock-site_id | ✅ | `WH01` | Site entrepôt (WH01) |

**Messages :** `ERROR: No Load task auto-created!` · `ERROR: <exception>` (souvent stock insuffisant) · sinon trace complète.

## 043 · ZRET_R_STOCK_DASH — Dashboard stock (SALV)
**Écran de sélection : NON** — `No stock records found in ZRET_T_STOCK` (I) · exception (E)

---

# 05 — Sales

## 050 · ZRET_R_SO_CREATE — Créer une commande client
**Écran de sélection : OUI** (SKIP 1 entre en-tête et postes)

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_CUSTID | Customer | zret_t_so-customer_id | ✅ | — | Client existant (ex. STORE001) |
| P_CURR | Currency | zret_t_so-currency | ✅ | `EUR` | Devise |
| P_ART1 | Article 1 | zret_t_so_item-article_id | ❌ | — | Article existant (ex. ART101) |
| P_QTY1 | Quantity 1 | p length 7 decimals 3 | ❌ | — | Quantité poste 1 |
| P_ART2 | Article 2 | zret_t_so_item-article_id | ❌ | — | Article poste 2 (optionnel) |
| P_QTY2 | Quantity 2 | p length 7 decimals 3 | ❌ | — | Quantité poste 2 |
| P_ART3 | Article 3 | zret_t_so_item-article_id | ❌ | — | Article poste 3 (optionnel) |
| P_QTY3 | Quantity 3 | p length 7 decimals 3 | ❌ | — | Quantité poste 3 |

**Succès :** `Sales Order <n> created successfully` (S) · **Erreur :** `Sales Order creation failed: invalid customer, article, or input` (E)

## 051 · ZRET_R_SO_LIST — Liste des commandes (ALV + popup postes)
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| SO_CUST | Customer (filtre) | SELECT-OPTIONS FOR zret_t_so-customer_id | ❌ | — | Vide = tous ; ou un client |
| SO_STAT | Status (filtre) | SELECT-OPTIONS FOR zret_t_so-status | ❌ | — | Vide = tous ; O/D/B/C |

**Messages :** `Cannot load Sales Order details` (I) · `Error displaying SO items` (I) · `No Sales Order found for these filters` (I) · exception (E)

## 052 · ZRET_R_DELIV_CREATE — Créer une livraison depuis une commande
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_SO | Sales order n° | zret_t_so-so_number | ✅ | — | N° de commande au statut **Open** (issu de 050) |
| P_SITE | Source site | zret_t_site-site_id | ✅ | `WH01` | Site source de type **entrepôt** |

**Succès :** `Delivery <n> created from SO <SO>. SO status is now Delivered.` (S) · **Erreur :** `Delivery creation failed: SO not found, not in Open status, or source site is not a warehouse` (E)

## 053 · ZRET_R_DELIV_LIST — Liste des livraisons (ALV)
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| SO_SITE | Source site (filtre) | SELECT-OPTIONS FOR zret_t_deliv-source_site_id | ❌ | — | Vide = tous ; ou un site |
| SO_STAT | Status (filtre) | SELECT-OPTIONS FOR zret_t_deliv-status | ❌ | — | Vide = tous ; C/S/R |

**Messages :** `Cannot load Delivery details` (I) · `Error displaying delivery items` (I) · `No delivery found for these filters` (I) · exception (E)

## 054 · ZRET_R_INV_CREATE — Créer une facture client depuis une livraison
**Écran de sélection : OUI**

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| P_DELIV | Delivery n° | zret_t_deliv-deliv_number | ✅ | — | N° de livraison (issu de 052) |

**Succès :** `Invoice <n> created from Delivery <DL>. SO status is now Billed.` (S) · **Erreur :** `Invoice creation failed: delivery not found, SO not in Delivered status, or already billed` (E)

## 055 · ZRET_R_INV_LIST — Liste des factures client (ALV)
**Écran de sélection : OUI** (bloc encadré B1)

| Champ | Libellé | Type / réf | Oblig. | Défaut | Quoi mettre |
|---|---|---|---|---|---|
| S_INVNUM | Invoice n° | SELECT-OPTIONS FOR invoice_number | ❌ | — | Filtre n° facture (vide = toutes) |
| S_CUSTID | Customer | SELECT-OPTIONS FOR customer_id | ❌ | — | Filtre client |
| S_STATUS | Status | SELECT-OPTIONS FOR status | ❌ | — | Filtre statut |

**Messages :** `No items found for invoice <n>` (I) · exception (E)

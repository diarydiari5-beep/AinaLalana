-- ============================================================
-- AinaWeb — Schéma de la base de données
-- Compatible MySQL 5.6 (WAMP)
-- Import : mysql -u root < database/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS ainalalana
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ainalalana;

CREATE TABLE IF NOT EXISTS utilisateurs (
  id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  prenom VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  mdp VARCHAR(255) NOT NULL,
  role ENUM('citoyen','gestionnaire_csb','chef_district') NOT NULL DEFAULT 'citoyen',
  actif TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lieux (
  id_lieu VARCHAR(50) PRIMARY KEY,
  nom_lieu VARCHAR(200) NOT NULL,
  type ENUM('village','csb') NOT NULL,
  lits_disponibles INT DEFAULT NULL,
  medecin_present TINYINT(1) DEFAULT NULL,
  derniere_mise_a_jour DATETIME DEFAULT NULL
) ENGINE=InnoDB;

-- Rattachement d'un gestionnaire_csb à un CSB (voir migration_id_csb.sql)
ALTER TABLE utilisateurs ADD COLUMN id_csb VARCHAR(50) DEFAULT NULL,
  ADD FOREIGN KEY (id_csb) REFERENCES lieux(id_lieu) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS routes (
  id_route INT AUTO_INCREMENT PRIMARY KEY,
  id_lieu_depart VARCHAR(50) NOT NULL,
  id_lieu_arrivee VARCHAR(50) NOT NULL,
  distance_km DECIMAL(10,2) NOT NULL,
  etat ENUM('praticable','difficile','coupee') NOT NULL DEFAULT 'praticable',
  FOREIGN KEY (id_lieu_depart) REFERENCES lieux(id_lieu),
  FOREIGN KEY (id_lieu_arrivee) REFERENCES lieux(id_lieu)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS signalements (
  id_signalement INT AUTO_INCREMENT PRIMARY KEY,
  id_utilisateur INT NOT NULL,
  id_route INT NOT NULL,
  etat_signale ENUM('praticable','difficile','coupee') NOT NULL,
  date_signalement DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  commentaire TEXT DEFAULT NULL,
  FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur),
  FOREIGN KEY (id_route) REFERENCES routes(id_route)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS itineraires (
  id_itineraire INT AUTO_INCREMENT PRIMARY KEY,
  id_utilisateur INT NOT NULL,
  id_lieu_depart VARCHAR(50) NOT NULL,
  id_csb_recommande VARCHAR(50) NOT NULL,
  distance_totale_km DECIMAL(10,2) NOT NULL,
  algorithme VARCHAR(50) DEFAULT 'dijkstra',
  date_calcul DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  notification TEXT DEFAULT NULL,
  FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur),
  FOREIGN KEY (id_lieu_depart) REFERENCES lieux(id_lieu),
  FOREIGN KEY (id_csb_recommande) REFERENCES lieux(id_lieu)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS etapes_itineraire (
  id_etape INT AUTO_INCREMENT PRIMARY KEY,
  id_itineraire INT NOT NULL,
  id_lieu VARCHAR(50) NOT NULL,
  ordre INT NOT NULL,
  FOREIGN KEY (id_itineraire) REFERENCES itineraires(id_itineraire),
  FOREIGN KEY (id_lieu) REFERENCES lieux(id_lieu)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Données de test
-- ------------------------------------------------------------
INSERT INTO lieux (id_lieu, nom_lieu, type, lits_disponibles, medecin_present) VALUES
('village-001', 'Ambohimanambola', 'village', NULL, NULL),
('village-002', 'Antsirabe', 'village', NULL, NULL),
('village-003', 'Ambalavao', 'village', NULL, NULL),
('village-004', 'Fianarantsoa', 'village', NULL, NULL),
('village-005', 'Mahajanga', 'village', NULL, NULL),
('village-006', 'Toliara', 'village', NULL, NULL),
('village-007', 'Toamasina', 'village', NULL, NULL),
('village-008', 'Morondava', 'village', NULL, NULL),
('csb-001', 'CSB Ambohimanambola', 'csb', 8, 1),
('csb-002', 'CSB Antsirabe', 'csb', 12, 1),
('csb-003', 'CSB Ambalavao', 'csb', 0, 0),
('csb-004', 'CSB Fianarantsoa', 'csb', 6, 1);

INSERT INTO utilisateurs (nom, prenom, email, mdp, role, id_csb) VALUES
('Rakoto', 'Admin', 'admin@test.com', 'admin123', 'chef_district', NULL),
('Rabe', 'Gest', 'gest@test.com', 'gest123', 'gestionnaire_csb', 'csb-001'),
('Citoyen', 'Test', 'citoyen@test.com', 'citoyen123', 'citoyen', NULL);

INSERT INTO routes (id_lieu_depart, id_lieu_arrivee, distance_km, etat) VALUES
('village-001', 'village-002', 3.2, 'praticable'),
('village-002', 'village-003', 5.0, 'difficile'),
('village-003', 'village-004', 4.1, 'praticable'),
('village-001', 'csb-001', 2.5, 'praticable'),
('village-002', 'csb-002', 1.8, 'praticable'),
('village-003', 'csb-003', 3.0, 'praticable'),
('village-004', 'csb-004', 2.2, 'praticable'),
('village-001', 'csb-002', 5.0, 'praticable'),
('village-003', 'csb-004', 10.0, 'difficile');

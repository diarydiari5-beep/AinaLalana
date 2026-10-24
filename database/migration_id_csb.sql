-- Associe chaque gestionnaire_csb à un seul CSB (lieux.id_lieu)
USE ainalalana;

ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS id_csb VARCHAR(50) DEFAULT NULL;

-- FK optionnelle (ignorer si déjà présente)
-- ALTER TABLE utilisateurs ADD FOREIGN KEY (id_csb) REFERENCES lieux(id_lieu) ON DELETE SET NULL;

-- ============================================================
-- Signalements anciens (avril – mi-mai 2026)
-- ============================================================
-- Utilisateurs : 1=Admin, 2=Gest, 3=Test Citoyen
-- Routes : voir ci-dessous
-- ============================================================

-- Route 9 : village-003 → csb-004 (coupée → restée coupée)
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 9, 'coupee',  '2026-04-02 08:15:00', 'Route complètement inondée, impossible de passer à pied.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 9, 'difficile','2026-04-10 10:30:00', 'L''eau a baissé mais la boue rend le passage très difficile.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (1, 9, 'praticable','2026-04-18 14:00:00', 'Réparations terminées, la route est de nouveau praticable.');

-- Route 4 : village-001 → csb-001 (alternance difficile/praticable)
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (2, 4, 'difficile','2026-04-05 06:45:00', 'Nid-de-poules sur 2 km après le pont.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 4, 'praticable','2026-04-12 09:20:00', 'Les nids-de-poules ont été comblés.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (2, 4, 'difficile','2026-04-28 16:10:00', 'De nouveaux nids-de-poules sont apparus après les pluies.');

-- Route 7 : village-004 → csb-004 (coupée longue durée)
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 7, 'coupee',  '2026-04-08 11:00:00', 'Pont endommagé par une crue, circulation interrompue.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (1, 7, 'coupee',  '2026-04-22 08:30:00', 'Travaux de réparation du pont en cours, toujours coupée.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (1, 7, 'difficile','2026-05-10 13:45:00', 'Pont rouvert mais limité aux véhicules légers.');

-- Route 5 : village-002 → csb-002 (praticable presque tout le temps)
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 5, 'praticable','2026-04-03 07:00:00', 'Route en bon état.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (2, 5, 'praticable','2026-04-15 12:00:00', 'Entretien régulier effectué.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 5, 'difficile','2026-04-25 17:30:00', 'Quelques branches tombées après la tempête.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (2, 5, 'praticable','2026-05-02 09:15:00', 'Branches dégagées, route nettoyée.');

-- Route 9 encore : signalements récents (mai)
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (3, 9, 'difficile','2026-05-05 11:20:00', 'Nouvel éboulement sur la portion nord.');
INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
VALUES (1, 9, 'coupee',  '2026-05-12 15:00:00', 'Éboulement non dégagé, route à nouveau coupée.');

-- ------------------------------------------------------------------
-- Route 11 : village-009 -> csb-005 (signalements récents)
-- Désactivé : ces lieux et cette route n'existent pas dans database/schema.sql
-- (8 villages, 4 CSB, 9 routes). À réactiver si le jeu de données est étendu.
-- ------------------------------------------------------------------
-- INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
-- VALUES (3, 11, 'difficile','2026-05-03 10:00:00', 'Piste dégradée par les pluies.');
-- INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
-- VALUES (2, 11, 'coupee',  '2026-05-07 14:30:00', 'Radier submergé, route impraticable.');
-- INSERT INTO signalements (id_utilisateur, id_route, etat_signale, date_signalement, commentaire)
-- VALUES (1, 11, 'difficile','2026-05-18 08:45:00', 'Eau retirée mais boue abondante.');

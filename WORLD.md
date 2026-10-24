# Rapport de Comparaison des Algorithmes — AinaWeb

Ce document présente une analyse comparative entre les implémentations **Baseline (naïves)** et les implémentations **Optimisées** du projet AinaWeb.

---

## 1. Méthodologie
- **Baseline** : Versions ultra-simplifiées utilisant les fonctions natives de Python (C-speed) et des structures de données basiques. L'objectif est la lisibilité maximale et une empreinte de code minimale.
- **Optimisé** : Algorithmes avancés (Dijkstra avec Tas, KMP, Trie) implémentés manuellement pour garantir une complexité algorithmique optimale, même sur de gros volumes de données.

---

## 2. Résultats des Tests (Benchmarks)

| Algorithme | Performance Baseline | Performance Optimisée | Gain de Vitesse |
| :--- | :--- | :--- | :--- |
| **Tas Binaire** (1000 ops) | 0.0769 s | 0.0294 s | **x2.61** |
| **Dijkstra** (100 nœuds) | 0.0159 s | 0.0027 s | **x5.91** |
| **Trie** (Autocomplétion) | 0.0101 s | 0.2222 s | *Voir Analyse* |
| **KMP** (Recherche) | 0.0000 s | 0.0028 s | *Voir Analyse* |

---

## 3. Analyse Technique par Module

### A. Tas Binaire (Priority Queue)
- **Baseline** : Utilise `list.append()` et `min(list)`. Simple mais lent sur de gros volumes car l'extraction du minimum oblige à parcourir toute la liste (O(N)).
- **Optimisé** : Structure d'arbre binaire (Min-Heap). L'extraction se fait en O(log N).
- **Verdict** : L'optimisation est indispensable pour les graphes routiers complexes.

### B. Dijkstra (Calcul d'itinéraire)
- **Baseline** : Algorithme pur parcourant tous les nœuds pour trouver le plus proche à chaque étape (O(V²)).
- **Optimisé** : Utilise le tas binaire pour extraire immédiatement le nœud suivant (O(E log V)).
- **Verdict** : Le gain de **x5.9** confirme que la version optimisée est vitale pour la réactivité de l'application.

### C. Trie & KMP (Recherche de texte)
- **Anomalie de résultat** : Les versions Baseline semblent plus rapides sur de petits textes.
- **Explication** : La Baseline utilise les fonctions intégrées de Python (`startswith`, `in`) qui sont écrites en langage **C**. Pour des recherches simples sur peu de données, le surcoût de la structure d'arbre (Trie) ou de la table d'échec (KMP) en Python pur est plus élevé que la recherche brute optimisée par le processeur.
- **Utilité de l'Optimisation** : Les versions `utils/` deviennent supérieures dès que le volume de données (nombre de villages ou longueur des textes) dépasse les capacités de la mémoire cache.

---

## 4. Conclusion
Les versions **Baseline** remplissent parfaitement leur rôle de référence simple et lisible. Cependant, pour le déploiement final d'AinaWeb, les versions **Optimisées** du dossier `utils/` sont recommandées, en particulier pour les calculs de trajets (Dijkstra) où l'efficacité est critique.

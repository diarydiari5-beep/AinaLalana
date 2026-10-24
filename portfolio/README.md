# Page portfolio — AinaLalana

Page d'étude de cas **autonome** (HTML + CSS, aucune dépendance, aucune police distante).
Elle reprend la palette de l'application et met en avant le problème, les trois rôles,
les captures, l'architecture et les choix algorithmiques.

## Contenu

```
portfolio/
  ainaweb.html          la page (à ouvrir directement dans un navigateur)
  ainaweb.css           styles
  assets/*.png          captures d'écran (1440×900, densité 2×)
```

## Avant de publier — 3 liens à remplacer

Dans `ainaweb.html`, remplacer les `href="#"` :

| Emplacement | Lien à mettre |
|---|---|
| Bouton « Voir la démo en ligne » (×2) | URL de l'application déployée |
| Bouton « Code source (GitHub) » / « Lire le code » | URL du dépôt |
| « ← Retour au portfolio » (×2) | URL de votre page projets |

## Intégration — 3 options

### 1. Site statique (le plus simple)

Copier le dossier `portfolio/` tel quel sur le site et faire pointer un lien vers
`portfolio/ainaweb.html`. Rien d'autre à installer.

### 2. Site React / Next.js / Vue

Copier les sections de `ainaweb.html` dans un composant, et `ainaweb.css` dans un
fichier de styles importé. Points à convertir :

- `class=` → `className=`
- `href="assets/..."` → `/assets/...` (placer les images dans `public/`)
- `<a>` internes → `Link` / `router`

La page n'utilise ni JavaScript ni animation indispensable : la conversion est mécanique.

### 3. WordPress / Wix / Squarespace

Créer une page, puis :

- soit coller le HTML dans un bloc « HTML personnalisé » et le CSS dans
  *Apparence → Personnaliser → CSS additionnel* ;
- soit, plus propre, reproduire les sections avec l'éditeur et importer les images.

## Remplacer les captures

Les images de `assets/` proviennent de l'application réelle. Pour les régénérer après
une modification de l'interface, voir `docs/screenshots/` (mêmes noms de fichiers) :
il suffit de recopier les PNG dans `portfolio/assets/`.

## Vérifications avant publication

- [ ] Les 3 liens (`démo`, `code`, `retour`) sont renseignés
- [ ] La démo répond et les comptes de test fonctionnent
- [ ] Le texte « 2026 » correspond à l'année de soutenance
- [ ] Les captures ne montrent aucune donnée personnelle
- [ ] La page s'affiche correctement sur mobile (test à 390 px de large)

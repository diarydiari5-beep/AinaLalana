import i18n from './i18n.js';

async function apiFetch(path, options = {}) {
    try {
        const res = await fetch(path, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        return await res.json();
    } catch (error) {
        console.error(`API error ${path}:`, error);
        return null;
    }
}

export const api = {
    connexion: async (email, mdp) => {
        const data = await apiFetch('/api/auth/connexion', {
            method: 'POST',
            body: JSON.stringify({ email, mdp }),
        });
        return data?.succes ? data.utilisateur : null;
    },

    stats: async () => {
        const data = await apiFetch('/api/admin/stats');
        return data;
    },

    listSignalements: async () => {
        const data = await apiFetch('/api/signalement/liste');
        return Array.isArray(data) ? data : [];
    },

    annulerSignalement: async (idSignalement, idRoute) => {
        const data = await apiFetch('/api/signalement/annuler', {
            method: 'POST',
            body: JSON.stringify({ id_signalement: idSignalement, id_route: idRoute }),
        });
        return data?.succes === true;
    },

    rechercherVillage: async (q) => {
        const data = await apiFetch(`/api/citoyen/rechercher?q=${encodeURIComponent(q)}`);
        return Array.isArray(data) ? data : [];
    },

    validerVillage: async (nom) => {
        const data = await apiFetch(`/api/citoyen/valider?nom=${encodeURIComponent(nom)}`);
        return data?.succes === true;
    },

    csbDisponibles: async (depart) => {
        const data = await apiFetch(`/api/citoyen/csb?depart=${encodeURIComponent(depart)}`);
        return Array.isArray(data) ? data : [];
    },

    calculerItineraire: async (dep, arr) => {
        const data = await apiFetch(`/api/citoyen/itineraire?dep=${encodeURIComponent(dep)}&arr=${encodeURIComponent(arr)}`);
        return data || { chemin: [], distance: 0, etapes: [] };
    },

    trouverRoute: async (a, b) => {
        const data = await apiFetch(`/api/route/trouver?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`);
        return data?.id_route || 0;
    },

    creerSignalement: async (idRoute, etat, commentaire) => {
        const data = await apiFetch('/api/signalement/creer', {
            method: 'POST',
            body: JSON.stringify({ id_route: idRoute, etat, commentaire }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    gestionnaireCsb: async () => {
        const data = await apiFetch('/api/gestionnaire/csb');
        return Array.isArray(data) ? data : [];
    },

    modifierCsb: async (idCsb, lits, medecin) => {
        const data = await apiFetch('/api/gestionnaire/csb/modifier', {
            method: 'POST',
            body: JSON.stringify({ id_csb: idCsb, lits, medecin }),
        });
        return data?.succes === true;
    },

    // Admin CRUD Lieux
    adminLieux: async () => {
        const data = await apiFetch('/api/admin/lieux');
        return Array.isArray(data) ? data : [];
    },

    creerLieu: async (nom, type, lits, medecin) => {
        const data = await apiFetch('/api/admin/lieu/creer', {
            method: 'POST',
            body: JSON.stringify({ nom, type, lits, medecin }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    modifierLieu: async (id, nom, type, lits, medecin) => {
        const data = await apiFetch('/api/admin/lieu/modifier', {
            method: 'POST',
            body: JSON.stringify({ id, nom, type, lits, medecin }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    supprimerLieu: async (id) => {
        const data = await apiFetch('/api/admin/lieu/supprimer', {
            method: 'POST',
            body: JSON.stringify({ id }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    // Admin recherche
    rechercherLieux: async (q) => {
        if (!q.trim()) return [];
        const data = await apiFetch(`/api/admin/lieux/rechercher?q=${encodeURIComponent(q)}`);
        return Array.isArray(data) ? data : [];
    },

    rechercherRoutes: async (q) => {
        if (!q.trim()) return [];
        const data = await apiFetch(`/api/admin/routes/rechercher?q=${encodeURIComponent(q)}`);
        return Array.isArray(data) ? data : [];
    },

    // Admin CRUD Routes
    adminRoutes: async () => {
        const data = await apiFetch('/api/admin/routes');
        return Array.isArray(data) ? data : [];
    },

    creerRoute: async (depart, arrivee, distance_km, etat) => {
        const data = await apiFetch('/api/admin/route/creer', {
            method: 'POST',
            body: JSON.stringify({ depart, arrivee, distance_km, etat }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    modifierRoute: async (id_route, depart, arrivee, distance_km, etat) => {
        const data = await apiFetch('/api/admin/route/modifier', {
            method: 'POST',
            body: JSON.stringify({ id_route, depart, arrivee, distance_km, etat }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },

    supprimerRoute: async (id_route) => {
        const data = await apiFetch('/api/admin/route/supprimer', {
            method: 'POST',
            body: JSON.stringify({ id_route }),
        });
        return data || { succes: false, message: i18n.t('api.networkError') };
    },
};

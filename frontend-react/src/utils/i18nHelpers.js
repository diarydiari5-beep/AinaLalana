import i18n from '../i18n.js';

const API_MESSAGES = {
    'Erreur réseau.': 'api.networkError',
    'Email ou mot de passe incorrect.': 'api.invalidCredentials',
    'CSB mis à jour avec succès !': 'api.csbUpdated',
    'Signalement envoyé avec succès !': 'api.reportSent',
    'Demande de réouverture enregistrée. En attente de validation par un administrateur.': 'signalement.reopened',
    'Erreur lors du signalement.': 'api.reportError',
    'Erreur lors de la mise à jour.': 'api.updateError',
};

export function translateApiMessage(message) {
    if (!message) return message;
    const key = API_MESSAGES[message];
    return key ? i18n.t(key) : message;
}

export function translateEtat(etat) {
    if (!etat) return etat;
    const key = `etat.${etat}`;
    const translated = i18n.t(key);
    return translated !== key ? translated : etat;
}

export function translateStatut(statut) {
    if (!statut) return statut;
    const key = `statut.${statut}`;
    const translated = i18n.t(key);
    return translated !== key ? translated : statut;
}

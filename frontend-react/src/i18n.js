import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import fr from './locales/fr.json';
import mg from './locales/mg.json';

export const LANG_KEY = 'ainaweb_lang';

const savedLang = localStorage.getItem(LANG_KEY);
const initialLang = savedLang === 'mg' ? 'mg' : 'fr';

i18n.use(initReactI18next).init({
    resources: {
        fr: { translation: fr },
        mg: { translation: mg },
    },
    lng: initialLang,
    fallbackLng: 'fr',
    interpolation: { escapeValue: false },
});

i18n.on('languageChanged', (lng) => {
    localStorage.setItem(LANG_KEY, lng);
    document.documentElement.lang = lng === 'mg' ? 'mg' : 'fr';
});

document.documentElement.lang = initialLang === 'mg' ? 'mg' : 'fr';

export default i18n;

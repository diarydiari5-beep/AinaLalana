import { useTranslation } from 'react-i18next';

const LANGUAGES = [
    { code: 'fr' },
    { code: 'mg' },
];

export default function LanguageSwitcher({ compact = false }) {
    const { i18n, t } = useTranslation();
    const current = i18n.language === 'mg' ? 'mg' : 'fr';

    const setLang = (lng) => {
        if (lng !== current) i18n.changeLanguage(lng);
    };

    return (
        <div
            className={`lang-switcher${compact ? ' lang-switcher-compact' : ''}`}
            role="group"
            aria-label={t('lang.switch')}
        >
            {LANGUAGES.map(({ code }) => {
                const active = current === code;
                return (
                    <button
                        key={code}
                        type="button"
                        className={`lang-btn${active ? ' active' : ''}`}
                        onClick={() => setLang(code)}
                        aria-pressed={active}
                        aria-label={t(`lang.${code}`)}
                        title={t(`lang.${code}`)}
                    >
                        <span className={`lang-flag lang-flag-${code}`} aria-hidden="true" />
                        <span className="lang-label">{compact ? code.toUpperCase() : t(`lang.${code}`)}</span>
                    </button>
                );
            })}
        </div>
    );
}

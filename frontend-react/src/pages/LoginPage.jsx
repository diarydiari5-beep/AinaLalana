import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';
import LanguageSwitcher from '../components/LanguageSwitcher.jsx';

// Comptes de démonstration (créés par database/schema.sql)
const COMPTES_DEMO = [
    { role: 'chef_district', email: 'admin@test.com', password: 'admin123' },
    { role: 'gestionnaire_csb', email: 'gest@test.com', password: 'gest123' },
    { role: 'citoyen', email: 'citoyen@test.com', password: 'citoyen123' },
];

export default function LoginPage({ onLogin }) {
    const { t } = useTranslation();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const remplirCompte = (compte) => {
        setEmail(compte.email);
        setPassword(compte.password);
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        const user = await api.connexion(email, password);
        if (user) {
            onLogin(user);
        } else {
            setError(t('api.invalidCredentials'));
        }
        setLoading(false);
    };

    return (
        <div className="login-page">
            <div className="login-left">
                <div className="login-left-content">
                    <div className="login-left-icon brand-mark brand-mark-lg" aria-hidden="true">
                        <span>AL</span>
                    </div>
                    <h1>AinaLalana</h1>
                    <p>{t('login.hero')}</p>
                </div>
            </div>
            <div className="login-right">
                <div className="login-box">
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
                        <LanguageSwitcher compact />
                    </div>
                    <h2>{t('login.title')}</h2>
                    <p className="login-sub">{t('login.subtitle')}</p>
                    {error && <div className="alert alert-error">⚠️ {error}</div>}
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <label>{t('common.email')}</label>
                            <input type="email" value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="exemple@email.com" required disabled={loading} />
                        </div>
                        <div className="form-row">
                            <label>{t('common.password')}</label>
                            <input type="password" value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••" required disabled={loading} />
                        </div>
                        <button className="btn btn-primary btn-lg btn-block" type="submit" disabled={loading}>
                            {loading ? t('login.connecting') : t('login.submit')}
                        </button>
                    </form>
                    <div className="login-demo">
                        <div className="login-demo-head">
                            <span>{t('login.demoTitle')}</span>
                            <small>{t('login.demoHint')}</small>
                        </div>
                        {COMPTES_DEMO.map((compte) => (
                            <button key={compte.email} type="button" className="login-demo-item"
                                onClick={() => remplirCompte(compte)} disabled={loading}>
                                <span className="login-demo-role">{t(`roles.${compte.role}`)}</span>
                                <span className="login-demo-creds">
                                    <code>{compte.email}</code>
                                    <code>{compte.password}</code>
                                </span>
                            </button>
                        ))}
                    </div>
                    <div className="login-divider">
                        {t('login.footer')}
                    </div>
                </div>
            </div>
        </div>
    );
}

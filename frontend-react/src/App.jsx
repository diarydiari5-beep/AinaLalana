import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import LoginPage from './pages/LoginPage.jsx';
import AdminPage from './pages/AdminPage.jsx';
import CitoyenPage from './pages/CitoyenPage.jsx';
import GestionnairePage from './pages/GestionnairePage.jsx';
import ItinerairePage from './pages/ItinerairePage.jsx';
import SignalementPage from './pages/SignalementPage.jsx';
import LanguageSwitcher from './components/LanguageSwitcher.jsx';

const routeForRole = {
    citoyen: 'citoyen',
    gestionnaire_csb: 'gestionnaire',
    chef_district: 'admin',
};

function getNavItems(role, t) {
    if (role === 'citoyen') {
        return [
            { key: 'citoyen', label: t('nav.home'), icon: '🏠' },
            { key: 'itineraire', label: t('nav.itinerary'), icon: '🗺️' },
            { key: 'signalement', label: t('nav.report'), icon: '⚠️' },
        ];
    }
    if (role === 'gestionnaire_csb') {
        return [
            { key: 'gestionnaire', label: t('nav.myCsb'), icon: '🏥' },
        ];
    }
    if (role === 'chef_district') {
        return [
            { key: 'admin', label: t('nav.dashboard'), icon: '📊' },
        ];
    }
    return [];
}

function Sidebar({ user, page, navigate, onLogout, open, onToggle, dark, onToggleDark }) {
    const { t } = useTranslation();
    const items = getNavItems(user?.role, t);

    return (
        <>
            <div className={`overlay${open ? ' open' : ''}`} onClick={onToggle} />
            <aside className={`sidebar${open ? ' open' : ''}`}>
                <div className="sidebar-logo">
                    <div className="brand-mark" aria-hidden="true"><span>AL</span></div>
                    <div className="brand-text">
                        <h1>AinaLalana</h1>
                        <p>{t('nav.brandSub')}</p>
                    </div>
                </div>
                <div className="sidebar-user">
                    <div className="sidebar-user-name">{user?.prenom} {user?.nom}</div>
                    {user?.role !== 'chef_district' && (
                        <div className="sidebar-user-role">
                            {t(`roles.${user?.role}`, { defaultValue: user?.role })}
                        </div>
                    )}
                </div>
                <nav className="sidebar-nav">
                    {items.map(item => (
                        <button key={item.key}
                            className={page === item.key ? 'active' : ''}
                            onClick={() => navigate(item.key)}>
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </button>
                    ))}
                </nav>
                <div className="sidebar-footer">
                    <LanguageSwitcher />
                    <button className="theme-toggle" onClick={onToggleDark} style={{ marginBottom: 8 }}>
                        {dark ? `☀️ ${t('theme.light')}` : `🌙 ${t('theme.dark')}`}
                    </button>
                    <button onClick={onLogout}>🚪 {t('nav.logout')}</button>
                </div>
            </aside>
        </>
    );
}

function App() {
    const { t } = useTranslation();
    const [user, setUser] = useState(null);
    const [page, setPage] = useState('login');
    const [loading, setLoading] = useState(true);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [dark, setDark] = useState(() => {
        const saved = localStorage.getItem('ainaweb_theme');
        return saved === 'dark';
    });

    useEffect(() => {
        document.documentElement.classList.toggle('dark', dark);
        localStorage.setItem('ainaweb_theme', dark ? 'dark' : 'light');
    }, [dark]);

    useEffect(() => {
        const session = localStorage.getItem('ainaweb_user');
        if (session) {
            try {
                const saved = JSON.parse(session);
                setUser(saved);
                setPage(routeForRole[saved.role] || 'citoyen');
            } catch {
                localStorage.removeItem('ainaweb_user');
            }
        }
        setLoading(false);
    }, []);

    const handleLogin = (userData) => {
        localStorage.setItem('ainaweb_user', JSON.stringify(userData));
        setUser(userData);
        setPage(routeForRole[userData.role] || 'citoyen');
    };

    const handleLogout = () => {
        localStorage.removeItem('ainaweb_user');
        setUser(null);
        setPage('login');
    };

    const navigate = (p) => {
        setPage(p);
        setSidebarOpen(false);
    };

    if (loading) {
        return <div className="loading">{t('common.loading')}</div>;
    }

    if (page === 'login') {
        return <LoginPage onLogin={handleLogin} />;
    }

    return (
        <div className="app-shell">
            <button className="hamburger" onClick={() => setSidebarOpen(!sidebarOpen)}>
                {sidebarOpen ? '✕' : '☰'}
            </button>
            <Sidebar user={user} page={page} navigate={navigate}
                onLogout={handleLogout} open={sidebarOpen}
                onToggle={() => setSidebarOpen(false)}
                dark={dark} onToggleDark={() => setDark(d => !d)} />
            <div className="main-area">
                {page === 'citoyen' && (
                    <CitoyenPage user={user} onLogout={handleLogout} onNavigate={navigate} />
                )}
                {page === 'itineraire' && (
                    <ItinerairePage user={user} onNavigate={navigate} />
                )}
                {page === 'signalement' && (
                    <SignalementPage user={user} onNavigate={navigate} />
                )}
                {page === 'gestionnaire' && (
                    <GestionnairePage user={user} onLogout={handleLogout} />
                )}
                {page === 'admin' && (
                    <AdminPage user={user} onLogout={handleLogout} />
                )}
            </div>
        </div>
    );
}

export default App;

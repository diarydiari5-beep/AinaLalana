import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';
import { ToastContainer } from '../components/Toast.jsx';
import { translateApiMessage } from '../utils/i18nHelpers.js';

function TabButton({ active, onClick, children }) {
    return (
        <button className={`btn ${active ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={onClick} style={{ width: 'auto' }}>
            {children}
        </button>
    );
}

export default function SignalementPage({ user, onNavigate }) {
    const { t } = useTranslation();
    const [mode, setMode] = useState('probleme'); // 'probleme' | 'reouverture'
    const [villageA, setVillageA] = useState('');
    const [villageB, setVillageB] = useState('');
    const [etat, setEtat] = useState('');
    const [commentaire, setCommentaire] = useState('');
    const [loading, setLoading] = useState(false);

    const [toasts, setToasts] = useState([]);
    const addToast = useCallback((message, type = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
    }, []);
    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const isReouverture = mode === 'reouverture';
        if (!villageA || !villageB) {
            addToast(t('signalement.fillRequired'), 'error');
            return;
        }
        if (!isReouverture && !etat) {
            addToast(t('signalement.fillRequired'), 'error');
            return;
        }
        setLoading(true);
        const idRoute = await api.trouverRoute(villageA, villageB);
        if (!idRoute) {
            addToast(t('signalement.noRoute'), 'error');
            setLoading(false);
            return;
        }
        const etatFinal = isReouverture ? 'praticable' : etat;
        const result = await api.creerSignalement(idRoute, etatFinal, commentaire);
        if (result.succes) {
            addToast(translateApiMessage(result.message) || (isReouverture ? t('signalement.reopened') : t('api.reportSent')));
            setVillageA('');
            setVillageB('');
            setEtat('');
            setCommentaire('');
        } else {
            addToast(translateApiMessage(result.message) || t('api.reportError'), 'error');
        }
        setLoading(false);
    };

    return (
        <>
            <ToastContainer toasts={toasts} removeToast={removeToast} />
            <div className="page-header">
                <h2>⚠️ {t('signalement.title')}</h2>
                <p>{t('signalement.subtitle')}</p>
            </div>
            <div className="page-content">
                <div className="flex gap-8 mb-24" style={{ flexWrap: 'wrap' }}>
                    <TabButton active={mode === 'probleme'} onClick={() => setMode('probleme')}>⚠️ {t('signalement.report')}</TabButton>
                    <TabButton active={mode === 'reouverture'} onClick={() => setMode('reouverture')}>✅ {t('signalement.reopen')}</TabButton>
                </div>

                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">{mode === 'reouverture' ? t('signalement.reopenTitle') : t('signalement.cardTitle')}</div>
                            <div className="card-subtitle">{mode === 'reouverture' ? t('signalement.reopenSub') : t('signalement.cardSub')}</div>
                        </div>
                    </div>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <label>{t('signalement.villageA')}</label>
                            <input type="text" value={villageA}
                                onChange={(e) => setVillageA(e.target.value)}
                                placeholder="Ex: Ambohimanambola" required disabled={loading} />
                        </div>
                        <div className="form-row">
                            <label>{t('signalement.villageB')}</label>
                            <input type="text" value={villageB}
                                onChange={(e) => setVillageB(e.target.value)}
                                placeholder="Ex: Antsirabe" required disabled={loading} />
                        </div>
                        {mode === 'probleme' ? (
                            <div className="form-row">
                                <label>{t('signalement.routeState')}</label>
                                <select value={etat} onChange={(e) => setEtat(e.target.value)} required disabled={loading}>
                                    <option value="">{t('signalement.selectState')}</option>
                                    <option value="difficile">{t('etat.difficile')}</option>
                                    <option value="coupee">{t('etat.coupee')}</option>
                                </select>
                            </div>
                        ) : (
                            <div className="text-muted text-sm" style={{ padding: '12px 0' }}>
                                ✅ {t('signalement.reopenSub')}
                            </div>
                        )}
                        <div className="form-row">
                            <label>{t('signalement.comment')}</label>
                            <textarea value={commentaire}
                                onChange={(e) => setCommentaire(e.target.value)}
                                placeholder={t('signalement.commentPlaceholder')} disabled={loading} />
                        </div>
                        <div className="flex gap-12">
                            <button className="btn btn-primary btn-lg" type="submit" disabled={loading}>
                                {loading ? t('signalement.sending') : `📤 ${t('signalement.submit')}`}
                            </button>
                            <button className="btn btn-outline btn-lg" type="button"
                                onClick={() => onNavigate('citoyen')}>
                                {t('common.cancel')}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
}

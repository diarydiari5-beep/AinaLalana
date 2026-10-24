import { useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';

export default function CitoyenPage({ user, onLogout, onNavigate }) {
    const { t } = useTranslation();
    const [query, setQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [village, setVillage] = useState('');
    const [csbList, setCsbList] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const debounceRef = useRef(null);

    const handleSearch = useCallback((value) => {
        setQuery(value);
        setError('');
        if (debounceRef.current) clearTimeout(debounceRef.current);
        if (value.length < 2) {
            setSuggestions([]);
            return;
        }
        debounceRef.current = setTimeout(async () => {
            const res = await api.rechercherVillage(value);
            setSuggestions(res || []);
        }, 250);
    }, []);

    const selectVillage = async (nom) => {
        setQuery(nom);
        setVillage(nom);
        setSuggestions([]);
        setLoading(true);
        setError('');
        const csbs = await api.csbDisponibles(nom);
        setCsbList(csbs || []);
        setLoading(false);
    };

    const handleKeyDown = async (e) => {
        if (e.key === 'Enter' && query.trim()) {
            setSuggestions([]);
            setLoading(true);
            const csbs = await api.csbDisponibles(query.trim());
            if (csbs.length > 0) {
                setVillage(query.trim());
                setCsbList(csbs);
            } else {
                setError(t('citoyen.noVillage'));
            }
            setLoading(false);
        }
    };

    const idxCsbRecommande = csbList.findIndex((x) => x.accessible);

    return (
        <>
            <div className="page-header">
                <h2>📍 {t('citoyen.title')}</h2>
                <p>{t('citoyen.subtitle')}</p>
            </div>
            <div className="page-content">
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">{t('citoyen.where')}</div>
                            <div className="card-subtitle">{t('citoyen.whereSub')}</div>
                        </div>
                    </div>
                    <div className="search-box">
                        <input type="text"
                            placeholder={t('citoyen.searchPlaceholder')}
                            value={query}
                            onChange={(e) => handleSearch(e.target.value)}
                            onKeyDown={handleKeyDown} />
                    </div>
                    {suggestions.length > 0 && (
                        <div className="suggestions-box">
                            {suggestions.map((v) => (
                                <button key={v} className="suggestion-item"
                                    onClick={() => selectVillage(v)}>
                                    📍 {v}
                                </button>
                            ))}
                        </div>
                    )}
                    {error && <div className="alert alert-error mt-12">⚠️ {error}</div>}
                </div>

                {loading && <div className="loading">{t('citoyen.searching')}</div>}

                {village && !loading && (
                    <>
                        <div className="village-badge">📍 {village}</div>

                        {csbList.length === 0 ? (
                            <div className="alert alert-warning">
                                ⚠️ {t('citoyen.noCsb', { village })}
                            </div>
                        ) : (
                            <>
                                <p className="text-muted text-sm mb-16">
                                    {t('citoyen.csbFound', { count: csbList.length, village })}
                                </p>
                                {csbList.map((c, i) => (
                                    <div key={c.id} className="csb-card">
                                        <div className="csb-card-top">
                                            <div className="csb-card-icon">🏥</div>
                                            <div className="csb-card-info">
                                                <div className="csb-card-name">{c.nom}</div>
                                                <div className="csb-card-sub">{t('citoyen.csbType')}</div>
                                            </div>
                                            <div className="csb-card-badges">
                                                {!c.accessible && <span className="badge badge-red">{t('citoyen.inaccessible')}</span>}
                                                {c.accessible && i === idxCsbRecommande && <span className="badge badge-green">{t('citoyen.recommended')}</span>}
                                            </div>
                                        </div>
                                        <div className="csb-card-details">
                                            <div className="csb-detail">
                                                🛣️ <strong>{(c.distance || 0).toFixed(1)} km</strong>
                                            </div>
                                            <div className="csb-detail" style={{ color: c.lits > 0 ? 'var(--success)' : 'var(--error)' }}>
                                                {c.lits > 0 ? '🛏️' : '🚫'} <strong>{t('common.bed', { count: c.lits })}</strong>
                                            </div>
                                            <div className="csb-detail" style={{ color: c.medecin ? 'var(--success)' : 'var(--warning)' }}>
                                                🧑‍⚕️ <strong>{c.medecin ? t('citoyen.doctorPresent') : t('citoyen.noDoctor')}</strong>
                                            </div>
                                        </div>
                                        <div className="csb-actions">
                                            <button className="btn btn-primary btn-sm"
                                                onClick={() => {
                                                    localStorage.setItem('ainaweb_itineraire', JSON.stringify({ dep: village, arr: c.nom }));
                                                    onNavigate('itineraire');
                                                }}>
                                                🗺️ {t('citoyen.viewRoute')}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </>
                        )}
                    </>
                )}
            </div>
        </>
    );
}

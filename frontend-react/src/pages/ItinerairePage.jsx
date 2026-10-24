import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';
import { translateEtat } from '../utils/i18nHelpers.js';

function statusColor(etat) {
    if (etat === 'coupee') return '#DC2626';
    if (etat === 'difficile') return '#F59E0B';
    return '#16A34A';
}

function statusBadge(etat) {
    if (etat === 'coupee') return 'badge-red';
    if (etat === 'difficile') return 'badge-orange';
    return 'badge-green';
}

export default function ItinerairePage({ user, onNavigate }) {
    const { t } = useTranslation();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const load = async () => {
            try {
                const raw = localStorage.getItem('ainaweb_itineraire');
                if (!raw) {
                    setError(t('itineraire.noneDefined'));
                    setLoading(false);
                    return;
                }
                const { dep, arr } = JSON.parse(raw);
                const res = await api.calculerItineraire(dep, arr);
                setData({ ...res, depart: dep, arrivee: arr });
            } catch {
                setError(t('itineraire.calcError'));
            }
            setLoading(false);
        };
        load();
    }, [t]);

    const handleBack = () => {
        localStorage.removeItem('ainaweb_itineraire');
        onNavigate('citoyen');
    };

    if (loading) return <div className="loading">{t('itineraire.calculating')}</div>;

    return (
        <>
            <div className="page-header">
                <h2>🗺️ {t('itineraire.title')}</h2>
                <p>{data ? t('itineraire.tripFrom', { depart: data.depart, arrivee: data.arrivee }) : ''}</p>
            </div>
            <div className="page-content">
                {error ? (
                    <div className="alert alert-error">⚠️ {error}</div>
                ) : data ? (
                    <>
                        <div className="itineraire-summary">
                            <div className="itineraire-card">
                                <label>{t('itineraire.depart')}</label>
                                <div className="value">📍 {data.depart}</div>
                            </div>
                            <div className="itineraire-card">
                                <label>{t('itineraire.arrivee')}</label>
                                <div className="value">🏥 {data.arrivee}</div>
                            </div>
                            <div className="itineraire-card full">
                                <label>{t('itineraire.totalDistance')}</label>
                                <div className="value" style={{ color: 'var(--primary)' }}>
                                    🛣️ {(data.distance || 0).toFixed(1)} km
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="card-title mb-16">{t('itineraire.steps')}</div>
                            {data.etapes && data.etapes.length > 0 ? (
                                <div className="timeline">
                                    {data.etapes.map((e, i) => {
                                        const isFirst = i === 0;
                                        const isLast = i === data.etapes.length - 1;
                                        const label = isFirst ? t('itineraire.stepDepart') : isLast ? t('itineraire.stepArrival') : t('itineraire.stepVillage');
                                        const icon = isFirst ? '📍' : isLast ? '🏥' : '●';
                                        return (
                                            <div key={i} className="timeline-step">
                                                <div className="timeline-dot" style={{ background: statusColor(e.etat) }}>
                                                    {icon}
                                                </div>
                                                <div className="timeline-line" />
                                                <div className="timeline-content">
                                                    <div className="timeline-name">{e.nom}</div>
                                                    <div className="timeline-label">{label}</div>
                                                </div>
                                                <div className="timeline-right">
                                                    <span className={`badge ${statusBadge(e.etat)}`}>{translateEtat(e.etat)}</span>
                                                    {e.distance_km > 0 && (
                                                        <div className="timeline-dist">{e.distance_km.toFixed(1)} km</div>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-state-icon">🗺️</div>
                                    <p>{t('itineraire.noSteps')}</p>
                                </div>
                            )}
                        </div>

                        <button className="btn btn-outline" onClick={handleBack}>
                            ← {t('itineraire.backHome')}
                        </button>
                    </>
                ) : (
                    <div className="card">
                        <div className="empty-state">
                            <div className="empty-state-icon">🗺️</div>
                            <p>{t('itineraire.noRouteHint')}</p>
                        </div>
                        <button className="btn btn-primary btn-block" onClick={() => onNavigate('citoyen')}>
                            ← {t('itineraire.goHome')}
                        </button>
                    </div>
                )}
            </div>
        </>
    );
}

import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';
import Modal from '../components/Modal.jsx';
import { ToastContainer } from '../components/Toast.jsx';
import { translateEtat } from '../utils/i18nHelpers.js';

function TabButton({ active, onClick, children }) {
    return (
        <button className={`btn ${active ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={onClick} style={{ width: 'auto' }}>
            {children}
        </button>
    );
}

export default function AdminPage({ user, onLogout }) {
    const { t, i18n } = useTranslation();
    const dateLocale = i18n.language === 'mg' ? 'mg-MG' : 'fr-FR';

    const [tab, setTab] = useState('dashboard');
    const [stats, setStats] = useState(null);
    const [signalements, setSignalements] = useState([]);
    const [lieux, setLieux] = useState([]);
    const [routes, setRoutes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [dateDebut, setDateDebut] = useState('');
    const [dateFin, setDateFin] = useState('');
    const [etatsFiltres, setEtatsFiltres] = useState([]);
    const [toasts, setToasts] = useState([]);
    const addToast = useCallback((message, type = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
    }, []);
    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);
    const [confirm, setConfirm] = useState({ open: false, title: '', message: '', onConfirm: null });
    const [lieuForm, setLieuForm] = useState({ open: false, edit: null, nom: '', type: 'village', lits: 0, medecin: false });
    const [lieuMsg, setLieuMsg] = useState('');
    const [routeForm, setRouteForm] = useState({ open: false, edit: null, depart: '', arrivee: '', distance_km: '', etat: 'praticable' });
    const [routeMsg, setRouteMsg] = useState('');

    const loadDashboard = async () => {
        try {
            const [s, sig] = await Promise.all([api.stats(), api.listSignalements()]);
            setStats(s || null);
            setSignalements(sig || []);
        } catch {
            setStats(null);
        }
    };

    const loadLieux = async () => {
        const l = await api.adminLieux();
        setLieux(l);
    };

    const loadRoutes = async () => {
        const r = await api.adminRoutes();
        setRoutes(r);
    };

    const loadAll = async () => {
        setLoading(true);
        await Promise.all([
            loadDashboard().catch(() => {}),
            loadLieux().catch(() => {}),
            loadRoutes().catch(() => {}),
        ]);
        setLoading(false);
    };

    useEffect(() => { loadAll(); }, []);

    const openAddLieu = () => {
        setLieuMsg('');
        setLieuForm({ open: true, edit: null, nom: '', type: 'village', lits: 0, medecin: false });
    };
    const openEditLieu = (l) => {
        setLieuMsg('');
        setLieuForm({ open: true, edit: l.id, nom: l.nom, type: l.type, lits: l.lits, medecin: l.medecin });
    };

    const saveLieu = async () => {
        setLieuMsg('');
        if (!lieuForm.nom.trim()) { setLieuMsg(t('admin.nameRequired')); return; }
        const isEdit = !!lieuForm.edit;
        const f = isEdit
            ? await api.modifierLieu(lieuForm.edit, lieuForm.nom, lieuForm.type, lieuForm.lits, lieuForm.medecin)
            : await api.creerLieu(lieuForm.nom, lieuForm.type, lieuForm.lits, lieuForm.medecin);

        if (f.succes) {
            addToast(isEdit ? t('admin.villageModified') : t('admin.villageAdded'));
            setLieuForm({ open: false, edit: null, nom: '', type: 'village', lits: 0, medecin: false });
            await Promise.all([loadLieux(), loadDashboard()]);
        } else {
            setLieuMsg(f.message || t('admin.saveError'));
        }
    };

    const deleteLieu = async (id) => {
        setConfirm({
            open: true,
            title: t('admin.confirmDelete'),
            message: t('admin.deleteVillageMsg'),
            onConfirm: async () => {
                const f = await api.supprimerLieu(id);
                if (f.succes) {
                    addToast(t('admin.villageDeleted'));
                    await Promise.all([loadLieux(), loadDashboard()]);
                } else {
                    addToast(f.message || t('admin.cannotDelete'), 'error');
                }
                setConfirm({ open: false, title: '', message: '', onConfirm: null });
            }
        });
    };

    const openAddRoute = () => {
        setRouteMsg('');
        setRouteForm({ open: true, edit: null, depart: '', arrivee: '', distance_km: '', etat: 'praticable' });
    };
    const openEditRoute = (r) => {
        setRouteMsg('');
        setRouteForm({ open: true, edit: r.id_route, depart: r.depart, arrivee: r.arrivee, distance_km: String(r.distance_km), etat: r.etat });
    };

    const saveRoute = async () => {
        setRouteMsg('');
        if (!routeForm.depart || !routeForm.arrivee || !routeForm.distance_km) {
            setRouteMsg(t('admin.allFieldsRequired'));
            return;
        }
        const isEdit = !!routeForm.edit;
        const f = isEdit
            ? await api.modifierRoute(routeForm.edit, routeForm.depart, routeForm.arrivee, routeForm.distance_km, routeForm.etat)
            : await api.creerRoute(routeForm.depart, routeForm.arrivee, routeForm.distance_km, routeForm.etat);

        if (f.succes) {
            addToast(isEdit ? t('admin.routeModified') : t('admin.routeAdded'));
            setRouteForm({ open: false, edit: null, depart: '', arrivee: '', distance_km: '', etat: 'praticable' });
            await Promise.all([loadRoutes(), loadDashboard()]);
        } else {
            setRouteMsg(f.message || t('admin.saveError'));
        }
    };

    const deleteRoute = async (id) => {
        setConfirm({
            open: true,
            title: t('admin.confirmDelete'),
            message: t('admin.deleteRouteMsg'),
            onConfirm: async () => {
                const f = await api.supprimerRoute(id);
                if (f.succes) {
                    addToast(t('admin.routeDeleted'));
                    await Promise.all([loadRoutes(), loadDashboard()]);
                } else {
                    addToast(f.message || t('admin.cannotDelete'), 'error');
                }
                setConfirm({ open: false, title: '', message: '', onConfirm: null });
            }
        });
    };

    const filteredLieux = lieux;
    const filteredRoutes = routes;

    const handleAnnuler = async (idSig, idRoute) => {
        const ok = await api.annulerSignalement(idSig, idRoute);
        if (ok) {
            setSignalements((prev) =>
                prev.filter((s) => Number(s.id_signalement) !== Number(idSig))
            );
            addToast(t('admin.reportResolved'));
            try {
                const s = await api.stats();
                setStats(s || null);
            } catch {
                /* stats optionnelles après résolution */
            }
        } else {
            addToast(t('admin.resolveError'), 'error');
        }
    };

    const toggleEtatFiltre = (etat) => {
        setEtatsFiltres(prev =>
            prev.includes(etat) ? prev.filter(e => e !== etat) : [...prev, etat]
        );
    };

    const hasActiveFilters = !!(dateDebut || dateFin || etatsFiltres.length);
    const clearAllFilters = () => {
        setDateDebut('');
        setDateFin('');
        setEtatsFiltres([]);
    };

    const signalementsFiltres = signalements.filter(sig => {
        if (etatsFiltres.length > 0 && !etatsFiltres.includes(sig.etat_signale)) return false;
        if (!sig.date_signalement) return !dateDebut && !dateFin;
        const d = new Date(sig.date_signalement);
        if (dateDebut && d < new Date(dateDebut + 'T00:00:00')) return false;
        if (dateFin) {
            const fin = new Date(dateFin + 'T23:59:59');
            if (d > fin) return false;
        }
        return true;
    });

    if (loading) return <div className="loading">{t('common.loading')}</div>;

    return (
        <>
            <ToastContainer toasts={toasts} removeToast={removeToast} />

            <Modal
                isOpen={confirm.open}
                onClose={() => setConfirm({ ...confirm, open: false })}
                title={confirm.title}
                footer={
                    <>
                        <button className="btn btn-outline btn-sm" onClick={() => setConfirm({ ...confirm, open: false })}>{t('common.cancel')}</button>
                        <button className="btn btn-danger btn-sm" onClick={confirm.onConfirm}>{t('common.confirm')}</button>
                    </>
                }
            >
                <p>{confirm.message}</p>
            </Modal>

            <div className="page-header">
                <h2>📊 {t('admin.title')}</h2>
                <p>{t('admin.subtitle')}</p>
            </div>
            <div className="page-content">
                <div className="flex gap-8 mb-24" style={{ flexWrap: 'wrap' }}>
                    <TabButton active={tab === 'dashboard'} onClick={() => setTab('dashboard')}>📊 {t('admin.tabDashboard')}</TabButton>
                    <TabButton active={tab === 'lieux'} onClick={() => setTab('lieux')}>🏘️ {t('admin.tabLieux')}</TabButton>
                    <TabButton active={tab === 'routes'} onClick={() => setTab('routes')}>🛣️ {t('admin.tabRoutes')}</TabButton>
                </div>

                {tab === 'dashboard' && !stats && (
                    <div className="alert alert-error">⚠️ {t('admin.loadError')}</div>
                )}
                {tab === 'dashboard' && stats && (
                    <>
                        {stats.coupees > 0 && (
                            <div className="alert alert-error">⚠️ {t('admin.routesCut', { count: stats.coupees })}</div>
                        )}
                        {stats.csb_pleins > 0 && (
                            <div className="alert alert-warning">⚠️ {t('admin.csbFull', { count: stats.csb_pleins })}</div>
                        )}

                        <div className="stats-grid">
                            {[
                                { label: t('admin.statVillages'), value: stats.villages, icon: '📍', color: '#16A34A' },
                                { label: t('admin.statCsb'), value: stats.csb, icon: '🏥', color: '#065F46' },
                                { label: t('admin.statRoutes'), value: stats.routes, icon: '🛣️', color: '#F59E0B' },
                                { label: t('admin.statCut'), value: stats.coupees, icon: '🚫', color: '#DC2626' },
                                { label: t('admin.statAvailable'), value: stats.csb_dispo, icon: '✅', color: '#16A34A' },
                                { label: t('admin.statFull'), value: stats.csb_pleins, icon: '🛏️', color: '#DC2626' },
                            ].map((item) => (
                                <div key={item.label} className="stat-card">
                                    <div className="stat-card-icon">{item.icon}</div>
                                    <div className="stat-card-value" style={{ color: item.color }}>{item.value}</div>
                                    <div className="stat-card-label">{item.label}</div>
                                </div>
                            ))}
                        </div>

                        <div className="card">
                            <div className="card-title mb-16">{t('admin.networkState')}</div>
                            {[
                                { label: t('admin.praticables'), value: stats.praticables, color: '#16A34A' },
                                { label: t('admin.difficiles'), value: stats.difficiles, color: '#F59E0B' },
                                { label: t('admin.coupees'), value: stats.coupees, color: '#DC2626' },
                            ].map((item) => (
                                <div key={item.label} className="progress-item">
                                    <div className="progress-label">{item.label}</div>
                                    <div className="progress-track">
                                        <div className="progress-fill" style={{
                                            width: `${(item.value / Math.max(stats.routes, 1)) * 100}%`,
                                            background: item.color
                                        }} />
                                    </div>
                                    <div className="progress-count">{item.value}/{stats.routes}</div>
                                </div>
                            ))}
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <div>
                                    <div className="card-title">{t('admin.recentReports')}</div>
                                    <div className="card-subtitle">
                                        {signalements.length > 0
                                            ? t('admin.displayed', { count: Math.min(signalementsFiltres.length, 20) })
                                            : t('common.none')}
                                    </div>
                                </div>
                            </div>
                            {hasActiveFilters && (
                                <div className="filter-active-bar">
                                    <span className="filter-active-dot" />
                                    {t('admin.activeFilter')}
                                    {(dateDebut || dateFin) && (
                                        <>
                                            <span className="filter-active-sep" />
                                            {dateDebut && <>{t('common.from')} <strong>{new Date(dateDebut + 'T00:00:00').toLocaleDateString(dateLocale)}</strong></>}
                                            {dateFin && <><span className="filter-active-sep" />{t('common.to')} <strong>{new Date(dateFin + 'T00:00:00').toLocaleDateString(dateLocale)}</strong></>}
                                        </>
                                    )}
                                    {etatsFiltres.length > 0 && (
                                        <>
                                            <span className="filter-active-sep" />
                                            {etatsFiltres.map(e => translateEtat(e)).join(' · ')}
                                        </>
                                    )}
                                </div>
                            )}
                            <div className="filter-bar">
                                <span className="filter-label">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: 4, verticalAlign: 'middle' }}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
                                    {t('common.period')}
                                </span>
                                <div className="filter-group">
                                    <span className="filter-group-label">{t('common.from')}</span>
                                    <input type="date" value={dateDebut} onChange={e => setDateDebut(e.target.value)}
                                        className={`filter-input${dateDebut ? ' is-active' : ''}`} />
                                </div>
                                <div className="filter-group">
                                    <span className="filter-group-label">{t('common.to')}</span>
                                    <input type="date" value={dateFin} onChange={e => setDateFin(e.target.value)}
                                        className={`filter-input${dateFin ? ' is-active' : ''}`} />
                                </div>
                            </div>
                            <div className="filter-bar filter-bar-secondary">
                                <span className="filter-label">{t('admin.filterRouteState')}</span>
                                <div className="filter-chips" role="group" aria-label={t('admin.filterRouteState')}>
                                    {['praticable', 'difficile', 'coupee'].map((etat) => {
                                        const active = etatsFiltres.includes(etat);
                                        return (
                                            <button
                                                key={etat}
                                                type="button"
                                                className={`filter-chip filter-chip-${etat}${active ? ' active' : ''}`}
                                                onClick={() => toggleEtatFiltre(etat)}
                                                aria-pressed={active}
                                            >
                                                {translateEtat(etat)}
                                            </button>
                                        );
                                    })}
                                </div>
                                {hasActiveFilters && (
                                    <button type="button" className="btn btn-filter-clear" onClick={clearAllFilters}>
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                                        {t('common.clear')}
                                    </button>
                                )}
                            </div>
                            {signalementsFiltres.length === 0 ? (
                                <div className="empty-state"><div className="empty-state-icon">📋</div><p>{t('admin.noReport')}</p></div>
                            ) : (
                                signalementsFiltres.slice(0, 20).map((sig) => {
                                    const d = sig.date_signalement ? new Date(sig.date_signalement) : null;
                                    const dateStr = d ? d.toLocaleDateString(dateLocale, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';
                                    return (
                                    <div key={sig.id_signalement} className="signalement-item">
                                        <div className="flex" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div className="signalement-route">{sig.route_depart || `#${sig.id_route}`} → {sig.route_arrivee || ''}</div>
                                            <div className="signalement-meta" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{dateStr}</div>
                                        </div>
                                        <div className="signalement-meta">{t('common.by')} {sig.user_prenom} {sig.user_nom}</div>
                                        <div className="signalement-comment">{sig.commentaire || t('admin.noComment')}</div>
                                        <div className="signalement-footer">
                                            <span className={`badge ${sig.etat_signale === 'coupee' ? 'badge-red' : sig.etat_signale === 'praticable' ? 'badge-green' : 'badge-orange'}`}>{translateEtat(sig.etat_signale)}</span>
                                            <button className="btn btn-outline btn-sm" onClick={() => handleAnnuler(sig.id_signalement, sig.id_route)}>✅ {t('admin.resolved')}</button>
                                        </div>
                                    </div>
                                    );
                                })
                            )}
                        </div>
                    </>
                )}

                {tab === 'lieux' && (
                    <div className="card">
                        <div className="card-header">
                            <div>
                                <div className="card-title">🏘️ {t('admin.lieuxTitle')}</div>
                                <div className="card-subtitle">{t('admin.lieuxCount', { count: lieux.length })}</div>
                            </div>
                            <button className="btn btn-primary btn-sm" onClick={openAddLieu}>+ {t('common.add')}</button>
                        </div>

                        <Modal
                            isOpen={lieuForm.open}
                            onClose={() => setLieuForm({ ...lieuForm, open: false })}
                            title={lieuForm.edit ? t('admin.editLieu') : t('admin.addLieu')}
                            footer={
                                <>
                                    <button className="btn btn-outline btn-sm" onClick={() => setLieuForm({ ...lieuForm, open: false })}>{t('common.cancel')}</button>
                                    <button className="btn btn-primary btn-sm" onClick={saveLieu}>💾 {t('common.save')}</button>
                                </>
                            }
                        >
                            <div className="form-content">
                                <div className="form-row">
                                    <label>{t('common.name')} *</label>
                                    <input type="text" value={lieuForm.nom} onChange={(e) => setLieuForm({ ...lieuForm, nom: e.target.value })} placeholder={t('admin.placeName')} />
                                </div>
                                <div className="form-row">
                                    <label>{t('common.type')}</label>
                                    <select value={lieuForm.type} onChange={(e) => setLieuForm({ ...lieuForm, type: e.target.value })}>
                                        <option value="village">{t('admin.village')}</option>
                                        <option value="csb">CSB</option>
                                    </select>
                                </div>
                                {lieuForm.type === 'csb' && (
                                    <>
                                        <div className="form-row">
                                            <label>{t('gestionnaire.bedsAvailable')}</label>
                                            <input type="number" value={lieuForm.lits} onChange={(e) => setLieuForm({ ...lieuForm, lits: parseInt(e.target.value) || 0 })} />
                                        </div>
                                        <div className="checkbox-row">
                                            <input type="checkbox" checked={lieuForm.medecin} onChange={(e) => setLieuForm({ ...lieuForm, medecin: e.target.checked })} id="lieu-med" />
                                            <label htmlFor="lieu-med">{t('gestionnaire.doctorPresent')}</label>
                                        </div>
                                    </>
                                )}
                                {lieuMsg && <div className="alert alert-error">{lieuMsg}</div>}
                            </div>
                        </Modal>

                        {filteredLieux.map((l) => (
                            <div key={l.id} className="csb-card" style={{ padding: 16, marginBottom: 10 }}>
                                <div className="flex flex-center" style={{ justifyContent: 'space-between' }}>
                                    <div className="flex flex-center gap-8">
                                        <span style={{ fontSize: 20 }}>{l.type === 'csb' ? '🏥' : '📍'}</span>
                                        <div>
                                            <strong>{l.nom}</strong>
                                            <div className="text-muted text-sm">{l.type === 'csb' ? 'CSB' : t('admin.village')} — {l.id}</div>
                                        </div>
                                    </div>
                                    <div className="flex gap-8">
                                        <span className={`badge ${l.type === 'csb' ? 'badge-blue' : 'badge-green'}`}>{l.type === 'csb' ? 'CSB' : t('admin.village')}</span>
                                        <button className="btn-icon btn-icon-edit" data-tip={t('common.edit')} onClick={() => openEditLieu(l)}>
                                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                        </button>
                                        <button className="btn-icon btn-icon-delete" data-tip={t('common.delete')} onClick={() => deleteLieu(l.id)}>
                                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                                        </button>
                                    </div>
                                </div>
                                {l.type === 'csb' && (
                                    <div className="flex gap-12 mt-8 text-sm text-muted">
                                        <span>🛏️ {t('common.bed', { count: l.lits })}</span>
                                        <span>🧑‍⚕️ {l.medecin ? t('admin.doctor') : t('admin.noDoctorShort')}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {tab === 'routes' && (
                    <div className="card">
                        <div className="card-header">
                            <div>
                                <div className="card-title">🛣️ {t('admin.routesTitle')}</div>
                                <div className="card-subtitle">{t('admin.routesCount', { count: routes.length })}</div>
                            </div>
                            <button className="btn btn-primary btn-sm" onClick={openAddRoute}>+ {t('common.add')}</button>
                        </div>

                        <Modal
                            isOpen={routeForm.open}
                            onClose={() => setRouteForm({ ...routeForm, open: false })}
                            title={routeForm.edit ? t('admin.editRoute') : t('admin.addRoute')}
                            footer={
                                <>
                                    <button className="btn btn-outline btn-sm" onClick={() => setRouteForm({ ...routeForm, open: false })}>{t('common.cancel')}</button>
                                    <button className="btn btn-primary btn-sm" onClick={saveRoute}>💾 {t('common.save')}</button>
                                </>
                            }
                        >
                            <div className="form-content">
                                <div className="form-row">
                                    <label>{t('admin.departVillage')}</label>
                                    <select value={routeForm.depart} onChange={(e) => setRouteForm({ ...routeForm, depart: e.target.value })}>
                                        <option value="">{lieux.length === 0 ? t('admin.noVillageAvailable') : t('common.select')}</option>
                                        {lieux.map((l) => <option key={l.id} value={l.id}>{l.nom} ({l.id})</option>)}
                                    </select>
                                </div>
                                <div className="form-row">
                                    <label>{t('admin.arriveeVillage')}</label>
                                    <select value={routeForm.arrivee} onChange={(e) => setRouteForm({ ...routeForm, arrivee: e.target.value })}>
                                        <option value="">{lieux.length === 0 ? t('admin.noVillageAvailable') : t('common.select')}</option>
                                        {lieux.map((l) => <option key={l.id} value={l.id}>{l.nom} ({l.id})</option>)}
                                    </select>
                                </div>
                                {lieux.length === 0 && (
                                    <div className="alert alert-warning" style={{ fontSize: '0.8rem', padding: '8px' }}>
                                        ⚠️ {t('admin.addVillagesFirst')}
                                    </div>
                                )}
                                <div className="form-row">
                                    <label>{t('admin.distanceKm')}</label>
                                    <input type="number" step="0.1" value={routeForm.distance_km} onChange={(e) => setRouteForm({ ...routeForm, distance_km: e.target.value })} placeholder="Ex: 5.0" />
                                </div>
                                <div className="form-row">
                                    <label>{t('common.state')}</label>
                                    <select value={routeForm.etat} onChange={(e) => setRouteForm({ ...routeForm, etat: e.target.value })}>
                                        <option value="praticable">{t('etat.praticable')}</option>
                                        <option value="difficile">{t('etat.difficile')}</option>
                                        <option value="coupee">{t('etat.coupee')}</option>
                                    </select>
                                </div>
                                {routeMsg && <div className="alert alert-error">{routeMsg}</div>}
                            </div>
                        </Modal>

                        {filteredRoutes.map((r) => (
                            <div key={r.id_route} className="signalement-item" style={{ padding: 14, marginBottom: 10 }}>
                                <div className="flex" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <div className="signalement-route" style={{ fontSize: 14 }}>
                                            {r.depart_nom} → {r.arrivee_nom}
                                        </div>
                                        <div className="text-muted text-sm mt-8">
                                            🛣️ {r.distance_km} km &nbsp;|&nbsp; ID: {r.id_route}
                                        </div>
                                    </div>
                                    <div className="flex gap-8 flex-center">
                                        <span className={`badge ${r.etat === 'praticable' ? 'badge-green' : r.etat === 'difficile' ? 'badge-orange' : 'badge-red'}`}>{translateEtat(r.etat)}</span>
                                        <button className="btn-icon btn-icon-edit" data-tip={t('common.edit')} onClick={() => openEditRoute(r)}>
                                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                                        </button>
                                        <button className="btn-icon btn-icon-delete" data-tip={t('common.delete')} onClick={() => deleteRoute(r.id_route)}>
                                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}

import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api.js';
import Modal from '../components/Modal.jsx';
import { ToastContainer } from '../components/Toast.jsx';
import { translateStatut } from '../utils/i18nHelpers.js';

export default function GestionnairePage({ user, onLogout }) {
    const { t } = useTranslation();
    const [csbList, setCsbList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editId, setEditId] = useState(null);
    const [editLits, setEditLits] = useState(0);
    const [editMedecin, setEditMedecin] = useState(false);
    const [editNom, setEditNom] = useState('');

    const [toasts, setToasts] = useState([]);
    const addToast = useCallback((message, type = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
    }, []);
    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    const load = async () => {
        setLoading(true);
        const csbs = await api.gestionnaireCsb();
        setCsbList(csbs || []);
        setLoading(false);
    };

    useEffect(() => { load(); }, []);

    const startEdit = (csb) => {
        setEditId(csb.id);
        setEditNom(csb.nom);
        setEditLits(csb.lits);
        setEditMedecin(csb.medecin);
    };

    const saveEdit = async () => {
        const ok = await api.modifierCsb(editId, editLits, editMedecin);
        if (ok) {
            addToast(t('gestionnaire.csbUpdated'));
            setEditId(null);
            load();
        } else {
            addToast(t('gestionnaire.updateError'), 'error');
        }
    };

    if (loading) return <div className="loading">{t('gestionnaire.loading')}</div>;

    return (
        <>
            <ToastContainer toasts={toasts} removeToast={removeToast} />

            <Modal
                isOpen={!!editId}
                onClose={() => setEditId(null)}
                title={t('gestionnaire.modify', { nom: editNom })}
                footer={
                    <>
                        <button className="btn btn-outline btn-sm" onClick={() => setEditId(null)}>{t('common.cancel')}</button>
                        <button className="btn btn-primary btn-sm" onClick={saveEdit}>💾 {t('common.save')}</button>
                    </>
                }
            >
                <div className="form-content">
                    <div className="form-row">
                        <label>{t('gestionnaire.bedsAvailable')}</label>
                        <input type="number" value={editLits}
                            onChange={(e) => setEditLits(parseInt(e.target.value) || 0)} />
                    </div>
                    <div className="checkbox-row">
                        <input type="checkbox" checked={editMedecin}
                            onChange={(e) => setEditMedecin(e.target.checked)} id="modal-med" />
                        <label htmlFor="modal-med">{t('gestionnaire.doctorPresent')}</label>
                    </div>
                </div>
            </Modal>

            <div className="page-header">
                <h2>🏥 {t('gestionnaire.title')}</h2>
                <p>{t('gestionnaire.subtitle')}</p>
            </div>
            <div className="page-content">
                {csbList.length === 0 ? (
                    <div className="card">
                        <div className="empty-state">
                            <div className="empty-state-icon">🏥</div>
                            <p>{t('gestionnaire.noCsb')}</p>
                        </div>
                    </div>
                ) : (
                    csbList.map((csb) => (
                        <div key={csb.id} className="csb-card">
                            <div className="csb-card-top">
                                <div className="csb-card-icon">🏥</div>
                                <div className="csb-card-info">
                                    <div className="csb-card-name">{csb.nom}</div>
                                    <div className="csb-card-sub">{t('citoyen.csbType')}</div>
                                </div>
                                <div className="csb-card-badges">
                                    <span className={`badge ${csb.statut === 'disponible' ? 'badge-green' : 'badge-red'}`}>
                                        {translateStatut(csb.statut)}
                                    </span>
                                </div>
                            </div>
                            <div className="csb-card-details">
                                <div className="csb-detail">
                                    🛏️ <strong>{t('common.bed', { count: csb.lits })}</strong> {t('common.available', { count: csb.lits })}
                                </div>
                                <div className="csb-detail" style={{ color: csb.medecin ? 'var(--success)' : 'var(--warning)' }}>
                                    🧑‍⚕️ <strong>{csb.medecin ? t('citoyen.doctorPresent') : t('citoyen.noDoctor')}</strong>
                                </div>
                            </div>

                            <div className="csb-actions">
                                <button className="btn btn-outline btn-sm"
                                    onClick={() => startEdit(csb)}>✏️ {t('common.edit')}</button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </>
    );
}

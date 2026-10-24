import { useEffect } from 'react';

export function Toast({ message, type = 'success', onClose, duration = 3000 }) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, duration);
        return () => clearTimeout(timer);
    }, [onClose, duration]);

    const icon = type === 'success' ? '✅' : '⚠️';

    return (
        <div className={`toast toast-${type}`}>
            <div className="toast-icon">{icon}</div>
            <div className="toast-content">
                <div className="toast-message">{message}</div>
            </div>
            <button className="modal-close" onClick={onClose} style={{ width: 24, height: 24, fontSize: 10 }}>
                ✕
            </button>
        </div>
    );
}

export function ToastContainer({ toasts, removeToast }) {
    return (
        <div className="toast-container">
            {toasts.map(toast => (
                <Toast
                    key={toast.id}
                    message={toast.message}
                    type={toast.type}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>
    );
}

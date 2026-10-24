import logging
import os
import threading

import mysql.connector
from mysql.connector import Error, OperationalError

def _config_depuis_environnement():
    """Configuration MySQL lue dans l'environnement (valeurs par défaut = WAMP local)."""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'database': os.getenv('DB_NAME', 'ainalalana'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'autocommit': False,
    }
    # Bases managées (TiDB, Aiven, Railway...) : TLS obligatoire
    ca = os.getenv('DB_SSL_CA')
    if ca:
        config['ssl_ca'] = ca
        config['ssl_disabled'] = False
    elif os.getenv('DB_SSL', '').lower() in ('1', 'true', 'yes'):
        config['ssl_disabled'] = False
    return config


class ConnexionBase:
    _config = _config_depuis_environnement()
    _local = threading.local()

    @staticmethod
    def get_instance():
        conn = getattr(ConnexionBase._local, 'connection', None)
        if conn is None:
            conn = RobustConnection(ConnexionBase._config)
            ConnexionBase._local.connection = conn
        return conn

    @staticmethod
    def reset_instance():
        conn = getattr(ConnexionBase._local, 'connection', None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            ConnexionBase._local.connection = None


class RobustConnection:
    def __init__(self, config):
        self.config = config
        self._lock = threading.RLock()
        self._conn = None

    def _fermer_connexion(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _connect(self):
        with self._lock:
            self._fermer_connexion()
            try:
                self._conn = mysql.connector.connect(**self.config)
                if self._conn.is_connected():
                    print("Connexion à la base de données réussie.")
            except Error as e:
                logging.error("Erreur lors de la connexion MySQL : %s", e)
                self._conn = None

    def _assurer_connexion(self):
        with self._lock:
            try:
                if self._conn is None or not self._conn.is_connected():
                    self._connect()
                else:
                    self._conn.ping(reconnect=True, attempts=3, delay=1)
            except (Error, OperationalError, ReferenceError):
                self._connect()

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('buffered', True)
        self._assurer_connexion()
        with self._lock:
            if self._conn is None:
                raise Exception("Impossible de se connecter à la base de données.")
            try:
                return self._conn.cursor(*args, **kwargs)
            except (OperationalError, ReferenceError):
                self._connect()
                if self._conn is None:
                    raise Exception("Impossible de se connecter à la base de données.")
                return self._conn.cursor(*args, **kwargs)

    def commit(self):
        with self._lock:
            if self._conn and self._conn.is_connected():
                self._conn.commit()

    def rollback(self):
        with self._lock:
            if self._conn and self._conn.is_connected():
                self._conn.rollback()

    def close(self):
        with self._lock:
            self._fermer_connexion()

    @property
    def is_connected(self):
        return self._conn is not None and self._conn.is_connected()

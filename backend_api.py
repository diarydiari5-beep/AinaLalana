import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

# Charge `.env` s'il existe (dépendance optionnelle : python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

logging.basicConfig(level=logging.WARNING)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database.DAO.ConnexionBase import ConnexionBase
from backend.controllers.controleur_auth import ControleurAuth
from backend.controllers.controleur_citoyen import ControleurCitoyen
from backend.controllers.controleur_gestionnaire import ControleurGestionnaire
from backend.controllers.controleur_admin import ControleurAdmin
from backend.services.service_csb import ServiceCSB
from backend.services.service_routage import ServiceRoutage
from backend.services.service_signalement import ServiceSignalement
from database.DAO.lieuDAO import LieuDAO
from database.DAO.SignalementDAO import SignalementDAO
from database.DAO.RouteDAO import RouteDAO
from backend.utils.trie import _normaliser_texte

app = Flask(__name__, static_folder=None)
CORS(app)

def _db():
    return ConnexionBase.get_instance()

def _message_erreur(e):
    """Détail de l'erreur en local, message générique en production.

    DEBUG_ERREURS=1 (par défaut) renvoie le détail : pratique en développement.
    DEBUG_ERREURS=0 masque les messages internes (schéma SQL, chemins...).
    """
    if os.getenv("DEBUG_ERREURS", "1") == "1":
        return str(e)
    logging.error("Erreur interne de l'API", exc_info=True)
    return "Une erreur interne est survenue."

# Initialisation des services (Shared Instances)
csb_svc = ServiceCSB()
routage_svc = ServiceRoutage()
signalement_svc = ServiceSignalement()
from backend.services.service_recherche import ServiceRecherche
recherche_svc = ServiceRecherche()

# Initialisation des contrôleurs avec injection des services partagés
auth_ctrl = ControleurAuth()

citoyen_ctrl = ControleurCitoyen()
citoyen_ctrl._service_csb = csb_svc
citoyen_ctrl._service_routage = routage_svc
citoyen_ctrl._service_recherche = recherche_svc
citoyen_ctrl._service_signalement = signalement_svc

gestionnaire_ctrl = ControleurGestionnaire()
gestionnaire_ctrl._service_csb = csb_svc
gestionnaire_ctrl._service_auth = auth_ctrl._service_auth

admin_ctrl = ControleurAdmin()
admin_ctrl._service_csb = csb_svc
admin_ctrl._service_routage = routage_svc

# DAOs
lieu_dao = LieuDAO()
signalement_dao = SignalementDAO()
route_dao = RouteDAO()

_nom_vers_id = {}
_id_vers_nom = {}

def _charger_cache():
    try:
        lieux = lieu_dao.get_all()
        _nom_vers_id.clear()
        _id_vers_nom.clear()
        for lieu in lieux:
            try:
                nom_norm = _normaliser_texte(lieu.nom_lieu)
                _nom_vers_id[nom_norm] = str(lieu.id_lieu)
                _id_vers_nom[str(lieu.id_lieu)] = lieu.nom_lieu
            except Exception as e:
                logging.warning(f"Impossible de normaliser le lieu {lieu.nom_lieu}: {e}")
        
        # Rafraîchir les caches des services partagés
        csb_svc.actualiser_cache()
        routage_svc._initialiser()
        recherche_svc.actualiser_cache()
        logging.info("Tous les caches des services partagés ont été actualisés.")
    except Exception as e:
        logging.error(f"Erreur lors du chargement du cache : {e}")

_cache_pret = False

def _initialiser_si_pret():
    global _cache_pret
    if _cache_pret:
        return
    _charger_cache()
    _cache_pret = True

@app.before_request
def _avant_requete():
    _db()._assurer_connexion()
    _initialiser_si_pret()

# API Routes

@app.route("/api/auth/connexion", methods=["POST"])
def api_connexion():
    data = request.get_json() or {}
    r = auth_ctrl.connexion(data.get("email"), data.get("mdp"))
    if r.get("succes") and r.get("utilisateur"):
        return jsonify({"succes": True, "utilisateur": r["utilisateur"]})
    return jsonify({"succes": False, "message": "Email ou mot de passe incorrect."})

@app.route("/api/admin/stats", methods=["GET"])
def api_stats():
    try:
        r = admin_ctrl.dashboard()
        if not r.get("succes"):
            return jsonify(r), 500
        d = r.get("dashboard", {})
        s = d.get("statistiques", {})
        return jsonify({
            "villages": s.get("total_villages", 0),
            "csb": s.get("total_csb", 0),
            "routes": s.get("total_routes", 0),
            "praticables": s.get("routes_praticables", 0),
            "difficiles": s.get("routes_difficiles", 0),
            "coupees": s.get("routes_coupees", 0),
            "csb_dispo": s.get("csb_disponibles", 0),
            "csb_pleins": s.get("csb_complets", 0),
        })
    except Exception as e:
        logging.error(f"Erreur api_stats : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

# Admin CRUD Lieux 

@app.route("/api/admin/lieux", methods=["GET"])
def api_admin_lieux():
    try:
        lieux = lieu_dao.get_all()
        logging.info(f"api_admin_lieux: {len(lieux)} lieux trouvés.")
        res = []
        for l in lieux:
            res.append({
                "id": str(l.id_lieu),
                "nom": str(l.nom_lieu),
                "type": str(l.type_lieu),
                "lits": int(l.lits_disponibles) if l.lits_disponibles is not None else 0,
                "medecin": bool(l.medecin_present),
            })
        return jsonify(res)
    except Exception as e:
        logging.error(f"Erreur api_admin_lieux : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/admin/lieu/creer", methods=["POST"])
def api_admin_lieu_creer():
    data = request.get_json() or {}
    nom = data.get("nom", "").strip()
    typ = data.get("type", "village")
    if not nom:
        return jsonify({"succes": False, "message": "Le nom est requis."})
    try:
        c = _db().cursor(dictionary=True)
        c.execute("SELECT id_lieu FROM lieux WHERE nom_lieu = %s", (nom,))
        if c.fetchone():
            c.close()
            return jsonify({"succes": False, "message": "Ce nom existe déjà."})
        
        # Meilleure génération d'ID
        c.execute("SELECT id_lieu FROM lieux WHERE id_lieu LIKE %s", (f"{typ}-%",))
        rows = c.fetchall()
        nxt = 1
        if rows:
            max_num = 0
            import re
            for r in rows:
                m = re.search(r'(\d+)$', r["id_lieu"])
                if m:
                    max_num = max(max_num, int(m.group(1)))
            nxt = max_num + 1
        
        new_id = f"{typ}-{nxt:03d}"
        c.execute("INSERT INTO lieux (id_lieu, nom_lieu, type) VALUES (%s, %s, %s)",
                  (new_id, nom, typ))
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True, "id": new_id})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

@app.errorhandler(Exception)
def handle_global_exception(e):
    logging.error(f"Erreur globale : {e}", exc_info=True)
    return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/admin/lieux/rechercher", methods=["GET"])
def api_admin_lieux_rechercher():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    try:
        motif = q.lower()
        from backend.utils.kmp import filtrer_liste as kmp_filtrer
        lieux = lieu_dao.get_all()
        noms_lower = [str(l.nom_lieu).strip().lower() for l in lieux]
        matching = kmp_filtrer(noms_lower, motif)
        matching_set = set(matching)
        return jsonify([{
            "id": str(l.id_lieu),
            "nom": str(l.nom_lieu),
            "type": str(l.type_lieu),
            "lits": int(l.lits_disponibles) if l.lits_disponibles is not None else 0,
            "medecin": bool(l.medecin_present),
        } for l in lieux if str(l.nom_lieu).strip().lower() in matching_set])
    except Exception as e:
        logging.error(f"Erreur api_admin_lieux_rechercher : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/admin/lieu/modifier", methods=["POST"])
def api_admin_lieu_modifier():
    data = request.get_json() or {}
    id_lieu = data.get("id")
    nom = data.get("nom", "").strip()
    typ = data.get("type")
    lits = data.get("lits")
    medecin = data.get("medecin")
    if not id_lieu or not nom:
        return jsonify({"succes": False, "message": "ID et nom requis."})
    try:
        c = _db().cursor()
        if typ:
            c.execute("UPDATE lieux SET nom_lieu=%s, type=%s WHERE id_lieu=%s", (nom, typ, id_lieu))
        else:
            c.execute("UPDATE lieux SET nom_lieu=%s WHERE id_lieu=%s", (nom, id_lieu))
        if typ == "csb":
            lv = int(lits) if lits is not None else 0
            mv = 1 if medecin else 0
            c.execute("UPDATE lieux SET lits_disponibles=%s, medecin_present=%s WHERE id_lieu=%s", (lv, mv, id_lieu))
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

@app.route("/api/admin/lieu/supprimer", methods=["POST"])
def api_admin_lieu_supprimer():
    data = request.get_json() or {}
    id_lieu = data.get("id")
    if not id_lieu:
        return jsonify({"succes": False, "message": "ID requis."})
    try:
        c = _db().cursor(dictionary=True)
        c.execute("SELECT COUNT(*) AS cnt FROM routes WHERE id_lieu_depart=%s OR id_lieu_arrivee=%s", (id_lieu, id_lieu))
        row = c.fetchone()
        if row["cnt"] > 0:
            c.close()
            return jsonify({"succes": False, "message": f"Impossible : {row['cnt']} route(s) utilisent ce lieu."})
        c.execute("DELETE FROM lieux WHERE id_lieu=%s", (id_lieu,))
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

# Admin CRUD Routes

@app.route("/api/admin/routes", methods=["GET"])
def api_admin_routes():
    try:
        routes = route_dao.get_all()
        return jsonify([{
            "id_route": r["id_route"],
            "depart": r["id_lieu_depart"],
            "arrivee": r["id_lieu_arrivee"],
            "distance_km": float(r["distance_km"]),
            "etat": r["etat"],
            "depart_nom": _id_vers_nom.get(r["id_lieu_depart"], r["id_lieu_depart"]),
            "arrivee_nom": _id_vers_nom.get(r["id_lieu_arrivee"], r["id_lieu_arrivee"]),
        } for r in routes])
    except Exception as e:
        logging.error(f"Erreur api_admin_routes : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/admin/route/creer", methods=["POST"])
def api_admin_route_creer():
    data = request.get_json() or {}
    dep = data.get("depart")
    arr = data.get("arrivee")
    dist = data.get("distance_km")
    etat = data.get("etat", "praticable")
    if not dep or not arr or not dist:
        return jsonify({"succes": False, "message": "Départ, arrivée et distance requis."})
    if dep == arr:
        return jsonify({"succes": False, "message": "Le départ et l'arrivée doivent être différents."})
    try:
        c = _db().cursor(dictionary=True)
        c.execute("SELECT id_route FROM routes WHERE (id_lieu_depart=%s AND id_lieu_arrivee=%s) OR (id_lieu_depart=%s AND id_lieu_arrivee=%s)",
                  (dep, arr, arr, dep))
        if c.fetchone():
            c.close()
            return jsonify({"succes": False, "message": "Une route existe déjà entre ces deux lieux."})
        c.execute("INSERT INTO routes (id_lieu_depart, id_lieu_arrivee, distance_km, etat) VALUES (%s, %s, %s, %s)",
                  (dep, arr, float(dist), etat))
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

@app.route("/api/admin/routes/rechercher", methods=["GET"])
def api_admin_routes_rechercher():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    try:
        motif = q.lower()
        from backend.utils.kmp import contient_motif
        routes = route_dao.get_all()
        res = []
        for r in routes:
            dn = (_id_vers_nom.get(r["id_lieu_depart"], "") or "").lower()
            an = (_id_vers_nom.get(r["id_lieu_arrivee"], "") or "").lower()
            if contient_motif(dn, motif) or contient_motif(an, motif):
                res.append({
                    "id_route": r["id_route"],
                    "depart": r["id_lieu_depart"],
                    "arrivee": r["id_lieu_arrivee"],
                    "distance_km": float(r["distance_km"]),
                    "etat": r["etat"],
                    "depart_nom": _id_vers_nom.get(r["id_lieu_depart"], r["id_lieu_depart"]),
                    "arrivee_nom": _id_vers_nom.get(r["id_lieu_arrivee"], r["id_lieu_arrivee"]),
                })
        return jsonify(res)
    except Exception as e:
        logging.error(f"Erreur api_admin_routes_rechercher : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/admin/route/modifier", methods=["POST"])
def api_admin_route_modifier():
    data = request.get_json() or {}
    id_route = data.get("id_route")
    dep = data.get("depart")
    arr = data.get("arrivee")
    dist = data.get("distance_km")
    etat = data.get("etat")
    if not id_route:
        return jsonify({"succes": False, "message": "ID route requis."})
    try:
        c = _db().cursor()
        updates = []
        params = []
        if dep: updates.append("id_lieu_depart=%s"); params.append(dep)
        if arr: updates.append("id_lieu_arrivee=%s"); params.append(arr)
        if dist is not None: updates.append("distance_km=%s"); params.append(float(dist))
        if etat: updates.append("etat=%s"); params.append(etat)
        if not updates:
            return jsonify({"succes": False, "message": "Aucun champ à modifier."})
        params.append(id_route)
        c.execute(f"UPDATE routes SET {', '.join(updates)} WHERE id_route=%s", params)
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

@app.route("/api/admin/route/supprimer", methods=["POST"])
def api_admin_route_supprimer():
    data = request.get_json() or {}
    id_route = data.get("id_route")
    if not id_route:
        return jsonify({"succes": False, "message": "ID route requis."})
    try:
        c = _db().cursor()
        c.execute("DELETE FROM routes WHERE id_route=%s", (id_route,))
        _db().commit()
        c.close()
        _charger_cache()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "message": _message_erreur(e)})

# --- Signalement ---

@app.route("/api/signalement/liste", methods=["GET"])
def api_liste_signalements():
    signalements = signalement_dao.get_all()
    route_map = {}
    for r in routage_svc.obtenir_toutes_routes():
        route_map[str(r["id_route"])] = r
    for sig in signalements:
        rid = str(sig["id_route"])
        r = route_map.get(rid, {})
        sig["route_depart"] = _id_vers_nom.get(str(r.get("depart", "")), "Inconnu")
        sig["route_arrivee"] = _id_vers_nom.get(str(r.get("arrivee", "")), "Inconnu")
    return jsonify(signalements)

@app.route("/api/signalement/annuler", methods=["POST"])
def api_annuler_signalement():
    data = request.get_json() or {}
    id_sig = int(data["id_signalement"])
    id_route = int(data["id_route"])
    try:
        signalement_dao.supprimer(id_sig)
    except Exception as e:
        return jsonify({"succes": False, "error": _message_erreur(e)})
    try:
        routage_svc.appliquer_signalement(id_route, "praticable")
    except Exception:
        pass
    return jsonify({"succes": True})

@app.route("/api/citoyen/rechercher", methods=["GET"])
def api_rechercher():
    r = citoyen_ctrl.rechercher_village(request.args.get("q", ""))
    return jsonify(r.get("resultats", []))

@app.route("/api/citoyen/valider", methods=["GET"])
def api_valider():
    r = citoyen_ctrl.valider_village(request.args.get("nom", ""))
    return jsonify({"succes": r.get("succes", False)})

@app.route("/api/citoyen/csb", methods=["GET"])
def api_csb():
    try:
        depart = request.args.get("depart", "")
        logging.info(f"api_csb: Recherche depuis '{depart}'")
        r = citoyen_ctrl.obtenir_csb_disponibles()
        csbs = r.get("csb", [])
        
        id_dep = ""
        try:
            nom_norm = _normaliser_texte(depart)
            id_dep = _nom_vers_id.get(nom_norm, "")
        except:
            pass
            
        if not id_dep:
            logging.warning(f"api_csb: Village '{depart}' non trouvé dans le cache.")
        
        resultats = []
        for c in csbs:
            dist = float('inf')
            if id_dep:
                itin = routage_svc.calculer_itineraire(str(id_dep), str(c["id"]))
                if itin:
                    dist = float(itin.get("distance", float('inf')))
            
            medecin = bool(c.get("medecin_present"))
            route_ok = dist != float('inf')
            logging.info(
                f"api_csb: CSB {c['nom']} ({c['id']}) distance={dist} medecin={medecin}"
            )
            
            resultats.append({
                "id": c["id"], "nom": c["nom"],
                "lits": c.get("lits_disponibles") or 0,
                "medecin": medecin,
                "distance": dist if route_ok else None,
                "accessible": route_ok and medecin,
            })
        
        # Accessibles (médecin + route) en premier, puis par distance
        resultats.sort(
            key=lambda x: (
                not x["accessible"],
                x["distance"] if x["distance"] is not None else float('inf'),
            )
        )
        
        logging.info(f"api_csb: Top résultat = {resultats[0]['nom'] if resultats else 'Aucun'}")
        return jsonify(resultats)
    except Exception as e:
        logging.error(f"Erreur api_csb : {e}", exc_info=True)
        return jsonify({"succes": False, "message": _message_erreur(e)}), 500

@app.route("/api/citoyen/itineraire", methods=["GET"])
def api_itineraire():
    dep = request.args.get("dep", "")
    arr = request.args.get("arr", "")
    
    id_dep, id_arr = dep, arr
    try:
        id_dep = _nom_vers_id.get(_normaliser_texte(dep), dep)
    except: pass
    try:
        id_arr = _nom_vers_id.get(_normaliser_texte(arr), arr)
    except: pass

    r = citoyen_ctrl.afficher_detail_trajet(str(id_dep), str(id_arr))
    if not r.get("succes"):
        itin = routage_svc.calculer_itineraire(str(id_dep), str(id_arr))
        if not itin:
            return jsonify({"chemin": [], "distance": 0, "etapes": []})
        chemin = itin.get("chemin", [])
        distance = itin.get("distance", 0)
    else:
        chemin = r["itineraire"]["chemin"]
        distance = r["itineraire"]["distance_km"]
    
    # Sécurité JSON pour Infinity
    safe_distance = float(distance) if distance != float('inf') else None
    
    etapes = []
    for i, id_lieu in enumerate(chemin):
        nom = _id_vers_nom.get(str(id_lieu), f"Lieu {id_lieu}")
        etat = "praticable"
        dist_seg = 0
        if i > 0:
            routes = routage_svc.obtenir_toutes_routes()
            for route in routes:
                dep_r, arr_r = str(route["depart"]), str(route["arrivee"])
                prev, cur = str(chemin[i-1]), str(id_lieu)
                if (dep_r == prev and arr_r == cur) or (arr_r == prev and dep_r == cur):
                    etat = route["etat"]
                    dist_seg = route["distance_km"]
                    break
        etapes.append({"nom": nom, "etat": etat, "distance_km": dist_seg})
    return jsonify({"chemin": chemin, "distance": safe_distance, "etapes": etapes})

@app.route("/api/signalement/creer", methods=["POST"])
def api_creer_signalement():
    data = request.get_json() or {}
    session = auth_ctrl._service_auth.obtenir_session()
    if not session:
        return jsonify({"succes": False, "message": "Non connecté."})
    try:
        ok = signalement_svc.enregistrer_signalement_citoyen(
            int(session["id_utilisateur"]), int(data["id_route"]),
            data["etat"], data.get("commentaire", ""), routage_svc
        )
        if ok:
            msg = (
                "Demande de réouverture enregistrée. En attente de validation par un administrateur."
                if data.get("etat") == "praticable"
                else "Signalement envoyé avec succès !"
            )
            return jsonify({"succes": True, "message": msg})
        return jsonify({"succes": False, "message": "Échec de l'enregistrement du signalement."})
    except Exception as e:
        return jsonify({"succes": False, "message": f"Erreur serveur: {_message_erreur(e)}"})

@app.route("/api/gestionnaire/csb", methods=["GET"])
def api_gestionnaire_csb():
    session = auth_ctrl._service_auth.obtenir_session()
    if not session:
        return jsonify({"succes": False, "message": "Non connecté."}), 401
    if session.get("role") != "gestionnaire_csb":
        return jsonify({"succes": False, "message": "Accès refusé."}), 403
    r = gestionnaire_ctrl.consulter_csb()
    csb_list = r.get("csb", [])
    if not isinstance(csb_list, list):
        csb_list = [csb_list] if csb_list else []
    return jsonify([{
        "id": str(c["id"]), "nom": c["nom"],
        "lits": c.get("lits_disponibles") or 0,
        "medecin": bool(c.get("medecin_present")),
        "statut": (
            "disponible"
            if (c.get("lits_disponibles") or 0) > 0
            else "complet"
        )
    } for c in csb_list])

@app.route("/api/gestionnaire/csb/modifier", methods=["POST"])
def api_gestionnaire_modifier():
    session = auth_ctrl._service_auth.obtenir_session()
    if not session:
        return jsonify({"succes": False, "message": "Non connecté."}), 401
    if session.get("role") != "gestionnaire_csb":
        return jsonify({"succes": False, "message": "Accès refusé."}), 403
    data = request.get_json() or {}
    ok = gestionnaire_ctrl.mettre_a_jour_csb(
        str(data.get("id_csb")), data.get("lits"), data.get("medecin")
    )
    return jsonify({
        "succes": ok.get("succes", False),
        "message": ok.get("message", ""),
    })

@app.route("/api/route/trouver", methods=["GET"])
def api_trouver_route():
    a, b = request.args.get("a", ""), request.args.get("b", "")
    id_a, id_b = "", ""
    try:
        id_a = _nom_vers_id.get(_normaliser_texte(a), "")
        id_b = _nom_vers_id.get(_normaliser_texte(b), "")
    except: pass
    
    if not id_a or not id_b:
        return jsonify({"id_route": 0})
    for r in routage_svc.obtenir_toutes_routes():
        dep, arr = str(r["depart"]), str(r["arrivee"])
        if (dep == id_a and arr == id_b) or (dep == id_b and arr == id_a):
            return jsonify({"id_route": r["id_route"]})
    return jsonify({"id_route": 0})

# --- Servir le frontend React (build) ---

REACT_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend-react", "dist")

@app.route("/")
def servir_index():
    return send_from_directory(REACT_DIST, "index.html")

@app.route("/assets/<path:filename>")
def servir_assets(filename):
    return send_from_directory(os.path.join(REACT_DIST, "assets"), filename)

@app.route("/<path:path>")
def servir_spa(path):
    return send_from_directory(REACT_DIST, "index.html")

@app.route("/api/admin/debug/etat", methods=["GET"])
def api_debug_etat():
    # Endpoint de diagnostic : désactivé par défaut (ENABLE_DEBUG_API=1 pour l'activer)
    if os.getenv("ENABLE_DEBUG_API", "0") != "1":
        return jsonify({"erreur": "Endpoint désactivé."}), 404
    try:
        csbs = csb_svc.obtenir_tous_csb()
        routes = routage_svc.obtenir_toutes_routes()
        lieux = lieu_dao.get_all()
        return jsonify({
            "csbs": csbs,
            "routes_count": len(routes),
            "lieux_count": len(lieux),
            "nom_vers_id": _nom_vers_id,
            "id_vers_nom": _id_vers_nom
        })
    except Exception as e:
        return jsonify({"erreur": _message_erreur(e)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"Serveur AinaWeb lancé sur http://localhost:{port} (debug={debug})")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        exclude_patterns=[
            "*/site-packages/*",
            "*/Lib/site-packages/*",
        ],
    )

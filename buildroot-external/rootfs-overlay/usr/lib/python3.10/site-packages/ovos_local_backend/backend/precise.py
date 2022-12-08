from flask import request

from ovos_local_backend.backend.decorators import noindex, requires_auth, check_selene_pairing
from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.database.wakewords import save_ww_recording
from ovos_local_backend.utils.selene import upload_ww


def get_precise_routes(app):
    @app.route('/precise/upload', methods=['POST'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def precise_upload():
        if CONFIGURATION["record_wakewords"]:
            auth = request.headers.get('Authorization', '').replace("Bearer ", "")
            uuid = auth.split(":")[-1]  # this split is only valid here, not selene
            save_ww_recording(uuid, request.files)

        uploaded = False
        selene_cfg = CONFIGURATION.get("selene") or {}
        if selene_cfg.get("upload_wakewords"):
            # contribute to mycroft open dataset
            uploaded = upload_ww(request.files)

        return {"success": True,
                "sent_to_mycroft": uploaded,
                "saved": CONFIGURATION["record_wakewords"]}

    @app.route('/device/<uuid>/wake-word-file', methods=['POST'])
    @noindex
    @check_selene_pairing
    @requires_auth
    def precise_upload_v2(uuid):
        if CONFIGURATION["record_wakewords"]:
            save_ww_recording(uuid, request.files)

        uploaded = False
        selene_cfg = CONFIGURATION.get("selene") or {}
        if selene_cfg.get("upload_wakewords"):
            # contribute to mycroft open dataset
            uploaded = upload_ww(request.files)

        return {"success": True,
                "sent_to_mycroft": uploaded,
                "saved": CONFIGURATION["record_wakewords"]}

    return app

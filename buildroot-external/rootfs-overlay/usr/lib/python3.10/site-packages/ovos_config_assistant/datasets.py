import json
import os
import time
from base64 import b64encode

from json_database import JsonDatabaseXDG
from ovos_config import Configuration
from pywebio.input import actions, file_upload, input_group, textarea, select
from pywebio.output import put_text, put_code, use_scope, put_markdown, popup, put_image, put_file, put_html, \
    put_buttons, put_table


def _render_ww(idx, db=None):
    db = db or JsonDatabaseXDG("ovos_wakewords")

    def on_tag(bt):
        data["tag"] = bt
        db[idx]["tag"] = bt
        db.commit()
        _render_ww(idx, db)

    with use_scope("main_view", clear=True):
        data = db[idx]  # id == db_position + 1
        data["tag"] = data.get("tag") or "untagged"

        if os.path.isfile(data["path"]):
            content = open(data["path"], 'rb').read()
            html = f"""
            <audio controls src="data:audio/x-wav;base64,{b64encode(content).decode('ascii')}" />
            """
            put_table([
                ['metadata', put_code(json.dumps(data, indent=4), "json")],
                ['playback', put_html(html)],
                ['file', put_file(data["path"].split("/")[-1], content, 'Download')],
                ['classify', put_buttons(["wake_word", "speech", "noise", "silence"],
                                         onclick=on_tag)]
            ])

        else:
            put_table([
                ['metadata', put_code(json.dumps(data, indent=4), "json")],
                ['playback', put_markdown("**WARNING** - file not found")],
                ['file', put_markdown("**WARNING** - file not found")],
                ['classify', put_buttons(["untagged", "wake_word", "speech", "noise", "silence"],
                                         onclick=on_tag)]
            ])


def ww_select(back_handler=None, uuid=None, ww=None):
    buttons = []
    db = JsonDatabaseXDG("ovos_wakewords")
    if not len(db):
        with use_scope("main_view", clear=True):
            put_text("No wake words uploaded yet!")
        datasets_menu(back_handler=back_handler)
        return

    for m in db:
        if uuid is not None and m["uuid"] != uuid:
            continue
        if ww is not None and m["transcription"] != ww:
            continue
        name = f"{m['wakeword_id']}-{m['transcription']}"
        buttons.append({'label': name, 'value': m['wakeword_id']})

    if len(buttons) == 0:
        with use_scope("main_view", clear=True):
            put_text("No wake words uploaded from this device yet!")
        opt = "main"
    else:
        if back_handler:
            buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
        opt = actions(label="Select a WakeWord recording",
                      buttons=buttons)
    if opt == "main":
        ww_menu(back_handler=back_handler)
        return

    _render_ww(opt - 1, db)

    ww_select(back_handler=back_handler, ww=ww, uuid=uuid)


def utt_select(back_handler=None, uuid=None, utt=None):
    buttons = []
    db = JsonDatabaseXDG("ovos_utterances")
    if not len(db):
        with use_scope("main_view", clear=True):
            put_text("No utterances uploaded yet!")
        datasets_menu(back_handler=back_handler)
        return

    for m in db:
        if uuid is not None and m["uuid"] != uuid:
            continue
        if utt is not None and m["transcription"] != utt:
            continue
        name = f"{m['utterance_id']}-{m['transcription']}"
        buttons.append({'label': name, 'value': m['utterance_id']})

    if len(buttons) == 0:
        with use_scope("main_view", clear=True):
            put_text("No utterances uploaded from this device yet!")
        opt = "main"
    else:
        if back_handler:
            buttons.insert(0, {'label': '<- Go Back', 'value': "main"})
        opt = actions(label="Select a Utterance recording",
                      buttons=buttons)
    if opt == "main":
        utt_menu(back_handler=back_handler)
        return

    with use_scope("main_view", clear=True):
        data = db[opt - 1]  # id == db_position + 1
        put_code(json.dumps(data, indent=4), "json")
        if os.path.isfile(data["path"]):
            content = open(data["path"], 'rb').read()
            html = f"""<audio controls src="data:audio/x-wav;base64,{b64encode(content).decode('ascii')}" />"""
            put_html(html)
            put_file(data["path"].split("/")[-1], content, 'Download Audio')
        else:
            put_markdown("**WARNING** - audio file not found")

    utt_select(back_handler=back_handler, uuid=uuid, utt=utt)


def ww_opts(back_handler=None, uuid=None):
    wws = list(set([ww["transcription"] for ww in JsonDatabaseXDG("ovos_wakewords")]))
    buttons = [{'label': "All Wake Words", 'value': "all"}] + \
              [{'label': ww, 'value': ww} for ww in wws]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if wws:
        ww = actions(label="What wake word would you like to inspect?", buttons=buttons)
        if ww == "main":
            datasets_menu(back_handler=back_handler)
            return
        if ww == "all":
            ww = None
        ww_select(ww=ww, back_handler=back_handler, uuid=uuid)
    else:
        with use_scope("main_view", clear=True):
            put_text("No wake words uploaded yet!")
        ww_menu(back_handler=back_handler)


def utt_opts(back_handler=None, uuid=None):
    utts = list(set([ww["transcription"] for ww in JsonDatabaseXDG("ovos_utterances")]))
    buttons = [{'label': "All Utterances", 'value': "all"}] + \
              [{'label': ww, 'value': ww} for ww in utts]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if utts:
        utt = actions(label="What utterance would you like to inspect?", buttons=buttons)
        if utt == "main":
            datasets_menu(back_handler=back_handler)
            return
        if utt == "all":
            utt = None
        utt_select(utt=utt, back_handler=back_handler, uuid=uuid)
    else:
        with use_scope("main_view", clear=True):
            put_text("No recordings uploaded yet!")
        utt_menu(back_handler=back_handler)


def _render_ww_tagger(selected_idx, selected_wws, db=None, untagged_only=False):
    db = db or JsonDatabaseXDG("ovos_wakewords")

    def on_tag(tag):
        nonlocal selected_idx, selected_wws

        if all((ww.get("tag") != "untagged" for ww in selected_wws)):
            if untagged_only:
                popup("No more wake words to tag!")
                return

        if tag == "Skip ->":
            selected_idx += 1
            if selected_idx >= len(selected_wws):
                selected_idx = 0
            if untagged_only and selected_wws[selected_idx]["tag"] != "untagged":
                return on_tag(tag)  # recurse

        elif selected_idx is not None:
            db_id = selected_wws[selected_idx]["wakeword_id"]
            db[db_id]["tag"] = selected_wws[selected_idx]["tag"] = tag
            db.commit()

        _render_ww_tagger(selected_idx, selected_wws, db, untagged_only=untagged_only)

    def on_gender(tag):
        nonlocal selected_idx, selected_wws

        if selected_idx is not None:
            db_id = selected_wws[selected_idx]["wakeword_id"]
            db[db_id]["speaker_type"] = selected_wws[selected_idx]["speaker_type"] = tag
            db.commit()

        _render_ww_tagger(selected_idx, selected_wws, db, untagged_only=untagged_only)

    with use_scope("main_view", clear=True):
        content = open(selected_wws[selected_idx]["path"], 'rb').read()
        html = f"""
        <audio controls src="data:audio/x-wav;base64,{b64encode(content).decode('ascii')}" />
        """

        put_table([
            ['wake word', selected_wws[selected_idx]["transcription"]],
            ['metadata', put_code(
                json.dumps(selected_wws[selected_idx], indent=4), "json")],
            ['playback', put_html(html)],
            ['speaker type', put_buttons(["male", "female", "children"],
                                         onclick=on_gender)],
            ['tag', put_buttons(["wake_word", "speech", "noise", "silence", "Skip ->"],
                                onclick=on_tag)],
        ])


def ww_tagger(back_handler=None, selected_wws=None, selected_idx=None, untagged_only=True):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/wakewords.png', 'rb').read()
        put_image(img)

    db = JsonDatabaseXDG("ovos_wakewords")

    def get_next_untagged():
        nonlocal selected_idx
        if untagged_only:
            for idx, ww in enumerate(selected_wws):
                if ww.get("tag", "untagged") == "untagged":
                    selected_idx = idx
                    break
            else:
                selected_idx = 0

    if not selected_wws:
        wws = set([w["transcription"] for w in db
                   if os.path.isfile(w["path"])])
        if not len(wws):
            with use_scope("main_view", clear=True):
                put_text("No wake words uploaded yet!")
            datasets_menu(back_handler=back_handler)
            return
        current_ww = select("Target WW", wws)
        selected_wws = [w for w in db
                        if w["transcription"] == current_ww
                        and os.path.isfile(w["path"])]
        selected_idx = 0
    else:
        selected_idx = selected_idx or 0
        current_ww = selected_wws[selected_idx]["transcription"]
        if untagged_only:
            get_next_untagged()

    # add "untagged" tag if needed
    for idx, ww in enumerate(selected_wws):
        if "tag" not in ww:
            selected_wws[idx]["tag"] = "untagged"
        if "speaker_type" not in ww:
            selected_wws[idx]["speaker_type"] = "untagged"

    _render_ww_tagger(selected_idx, selected_wws, db, untagged_only)

    buttons = [
        {'label': "Show all recordings" if untagged_only else 'Show untagged only', 'value': "toggle"},
        {'label': f'Delete {current_ww} database', 'value': "delete_ww"}
    ]

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)

    if opt == "toggle":
        untagged_only = not untagged_only
        get_next_untagged()

    if opt == "delete_ww":
        with use_scope("main_view", clear=True):
            put_markdown(f"""Are you sure you want to delete the {current_ww} wake word database?
            **this can not be undone**, proceed with caution!
            **ALL** {current_ww} recordings will be **lost**""")
        opt = actions(label=f"Delete {current_ww} database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:

            for ww in selected_wws:
                if os.path.isfile(ww["path"]):
                    os.remove(ww["path"])
                dbid = db.get_item_id(ww)
                if dbid >= 0:
                    db.remove_item(dbid)
            db.commit()

            with use_scope("main_view", clear=True):
                put_text(f"{current_ww} database deleted!")
        ww_tagger(back_handler=back_handler, untagged_only=untagged_only)
        return

    if opt == "main":
        with use_scope("main_view", clear=True):
            datasets_menu(back_handler=back_handler)
        return
    ww_tagger(back_handler=back_handler,
              selected_idx=selected_idx,
              selected_wws=selected_wws,
              untagged_only=untagged_only)


def ww_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/wakewords.png', 'rb').read()
        put_image(img)

    db = JsonDatabaseXDG("ovos_wakewords")

    buttons = [{'label': 'Upload Wake Word', 'value': "upload"} ]
    if len(db):
        buttons.append({'label': 'Inspect Wake Words', 'value': "ww"})
        buttons.append({'label': 'Delete wake words database', 'value': "delete_ww"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)
    if opt == "ww":
        ww_opts(back_handler=back_handler)
    if opt == "upload":
        with use_scope("main_view", clear=True):
            data = input_group("Upload wake word", [
                textarea("wake word name", placeholder="hey mycroft", required=True, name="name"),
                file_upload("wake word recording", name="file")
            ])

            name = data["name"]
            filename = data["file"]["filename"]
            mime = data["file"]["mime_type"]
            content = data["file"]["content"]
            if mime != "audio/x-wav":
                popup("invalid format!")

            else:
                os.makedirs(f"{Configuration()['data_path']}/wakewords", exist_ok=True)

                uuid = "AnonDevice"  # TODO from identity
                wav_path = f"{Configuration()['data_path']}/wakewords/{name}.{filename}"
                meta_path = f"{Configuration()['data_path']}/wakewords/{name}.{filename}.meta"
                meta = {
                    "transcription": name,
                    "path": wav_path,
                    "meta": {
                        "name": name,
                        "time": time.time(),
                        "accountId": "0",
                        "sessionId": "0",
                        "model": "uploaded_file",
                        "engine": "uploaded_file"
                    },
                    "uuid": uuid
                }
                db.add_item(meta)
                db.commit()
                with open(wav_path, "wb") as f:
                    f.write(content)
                with open(meta_path, "w") as f:
                    json.dump(meta, f)
                with popup("wake word uploaded!"):
                    put_code(json.dumps(meta, indent=4), "json")

    if opt == "delete_ww":
        with use_scope("main_view", clear=True):
            put_markdown("""Are you sure you want to delete the wake word database?
            **this can not be undone**, proceed with caution!
            **ALL** wake word recordings will be **lost**""")
        opt = actions(label="Delete wake words database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            # remove ww files from path
            for ww in db:
                if os.path.isfile(ww["path"]):
                    os.remove(ww["path"])
            # remove db itself
            os.remove(db.db.path)
            with use_scope("main_view", clear=True):
                put_text("wake word database deleted!")
        datasets_menu(back_handler=back_handler)
        return
    if opt == "main":
        with use_scope("main_view", clear=True):
            datasets_menu(back_handler=back_handler)
        return
    ww_menu(back_handler=back_handler)


def utt_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/utterances.png', 'rb').read()
        put_image(img)

    db = JsonDatabaseXDG("ovos_utterances")

    buttons = [{'label': 'Upload Utterance', 'value': "upload"}]
    if len(db):
        buttons.append({'label': 'Inspect Recordings', 'value': "utt"})
        buttons.append({'label': 'Delete utterances database', 'value': "delete_utt"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)
    if opt == "utt":
        utt_opts(back_handler=back_handler)
    if opt == "upload":
        with use_scope("main_view", clear=True):
            data = input_group("Upload utterance", [
                textarea("transcript", placeholder="hello world", required=True, name="utterance"),
                file_upload("speech recording", name="file")
            ])

            utterance = data["utterance"]
            filename = data["file"]["filename"]
            mime = data["file"]["mime_type"]
            content = data["file"]["content"]
            if mime != "audio/x-wav":
                popup("invalid format!")
            # if mime in ["application/json"]:
            else:
                os.makedirs(f"{Configuration()['data_path']}/utterances", exist_ok=True)

                uuid = "AnonDevice"  # TODO - from identity2.json
                path = f"{Configuration()['data_path']}/utterances/{utterance}.{filename}"

                meta = {
                    "transcription": utterance,
                    "path": path,
                    "uuid": uuid
                }
                db.add_item(meta)
                db.commit()
                with open(path, "wb") as f:
                    f.write(content)

                with popup("utterance recording uploaded!"):
                    put_code(json.dumps(meta, indent=4), "json")

    if opt == "delete_utt":
        with use_scope("main_view", clear=True):
            put_markdown("""Are you sure you want to delete the utterances database?
                        **this can not be undone**, proceed with caution!
                        **ALL** utterance recordings will be **lost**""")
        opt = actions(label="Delete utterances database?",
                      buttons=[{'label': "yes", 'value': True},
                               {'label': "no", 'value': False}])
        if opt:
            # TODO - also remove files from path
            os.remove(db.db.path)
            with use_scope("main_view", clear=True):
                put_text("utterance database deleted!")
        datasets_menu(back_handler=back_handler)
        return
    if opt == "main":
        with use_scope("main_view", clear=True):
            datasets_menu(back_handler=back_handler)
        return

    utt_menu(back_handler=back_handler)


def datasets_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/open_dataset.png', 'rb').read()
        put_image(img)

    buttons = [
        {'label': 'Manage Wake Words', 'value': "ww"},
        {'label': 'Manage Utterance Recordings', 'value': "utt"},
    ]
    if len(JsonDatabaseXDG("ovos_wakewords")):
        buttons.insert(0, {'label': 'Tag Wake Words', 'value': "dataset"})

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)

    if opt == "dataset":
        ww_tagger(back_handler=back_handler)
    elif opt == "utt":
        utt_menu(back_handler=back_handler)
    elif opt == "ww":
        ww_menu(back_handler=back_handler)
    elif opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    datasets_menu(back_handler=back_handler)

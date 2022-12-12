import random
import time

from ovos_plugin_common_play.ocp.base import OCPAbstractComponent
from ovos_plugin_common_play.ocp.media import Playlist
from ovos_plugin_common_play.ocp.mycroft_cps import \
    MycroftCommonPlayInterface
from ovos_plugin_common_play.ocp.settings import OCPSettings
from ovos_plugin_common_play.ocp.status import *
from ovos_plugin_common_play.ocp.stream_handlers import available_extractors
from ovos_utils.gui import is_gui_connected, is_gui_running
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message, get_mycroft_bus


class OCPQuery:
    def __init__(self, query, ocp_search=None, media_type=MediaType.GENERIC, bus=None):
        self.query = query
        self.media_type = media_type
        self.ocp_search = ocp_search
        self._bus = bus
        self.__dedicated_bus = False
        self.reset()

    def bind(self, bus=None):
        bus = bus or self._bus
        if not bus:
            self.__dedicated_bus = True
            bus = get_mycroft_bus()
        self._bus = bus

    def reset(self):
        self.active_skills = []
        self.query_replies = []
        self.searching = False
        self.search_start = 0
        self.query_timeouts = self.settings.min_timeout

    @property
    def settings(self):
        if self.ocp_search:
            return self.ocp_search.settings
        return OCPSettings()

    @property
    def search_playlist(self):
        if self.ocp_search:
            return self.ocp_search.search_playlist
        return Playlist()

    @property
    def bus(self):
        if self._bus:
            return self._bus
        if self.ocp_search:
            return self.ocp_search.bus

    @property
    def gui(self):
        if self.ocp_search:
            return self.ocp_search.gui

    def send(self):
        self.query_replies = []
        self.query_timeouts = self.settings.min_timeout
        self.search_start = time.time()
        self.searching = True
        self.register_events()
        self.bus.emit(Message('ovos.common_play.query',
                              {"phrase": self.query,
                               "question_type": self.media_type}))

    def wait(self):
        # if there is no match type defined, lets increase timeout a bit
        # since all skills need to search
        if self.media_type == MediaType.GENERIC:
            timeout = self.settings.max_timeout + 3  # timeout bonus
        else:
            timeout = self.settings.max_timeout
        while self.searching and time.time() - self.search_start <= timeout:
            time.sleep(0.1)
        self.searching = False
        self.remove_events()

    @property
    def results(self):
        return [s for s in self.query_replies if s.get("results")]

    def register_events(self):
        self.bus.on("ovos.common_play.skill.search_start",
                                  self.handle_skill_search_start)
        self.bus.on("ovos.common_play.skill.search_end",
                                  self.handle_skill_search_end)
        self.bus.on("ovos.common_play.query.response",
                                  self.handle_skill_response)

    def remove_events(self):
        self.bus.remove_all_listeners("ovos.common_play.skill.search_start")
        self.bus.remove_all_listeners("ovos.common_play.skill.search_end")
        self.bus.remove_all_listeners("ovos.common_play.query.response")

    def __enter__(self):
        """ Context handler, registers bus events """
        self.bind()
        return self

    def __exit__(self, _type, value, traceback):
        """ Removes the bus events """
        self.close()

    def close(self):
        self.remove_events()
        if self._bus and self.__dedicated_bus:
            self._bus.close()
            self._bus = None

    def handle_skill_search_start(self, message):
        skill_id = message.data["skill_id"]
        LOG.debug(f"{message.data['skill_id']} is searching")
        if skill_id not in self.active_skills:
            self.active_skills.append(skill_id)

    def handle_skill_response(self, message):
        search_phrase = message.data["phrase"]
        if search_phrase != self.query:
            # not an answer for this search query
            return
        timeout = message.data.get("timeout")
        skill_id = message.data['skill_id']
        # LOG.debug(f"OVOSCommonPlay result: {skill_id}")

        if message.data.get("searching"):
            # extend the timeout by N seconds
            if timeout and self.settings.allow_extensions:
                self.query_timeouts += timeout
            # else -> expired search

        else:
            # Collect replies until the timeout
            if not self.searching and not len(self.query_replies):
                LOG.debug("  too late!! ignored in track selection process")
                LOG.warning(
                    f"{message.data['skill_id']} is not answering fast "
                    "enough!")

            # populate search playlist
            has_gui = is_gui_running() or is_gui_connected(self.bus)
            results = message.data.get("results", [])
            for idx, res in enumerate(results):
                if self.media_type not in [MediaType.ADULT, MediaType.HENTAI]:
                    # skip adult content results unless explicitly enabled
                    if not self.settings.adult_content and \
                            res.get("media_type", MediaType.GENERIC) in [MediaType.ADULT, MediaType.HENTAI]:
                        continue

                # filter uris we can play, usually files and http streams, but some
                # skills might return results that depend on additional packages,
                # eg. soundcloud, rss, youtube, deezer....
                uri = res.get("uri", "")
                if res.get("playlist") and not uri:
                    res["playlist"] = [
                        r for r in res["playlist"]
                        if r.get("uri") and any(r.get("uri").startswith(e)
                                                for e in
                                                available_extractors())]
                    if not len(res["playlist"]):
                        results[idx] = None  # can't play this search result!
                        LOG.error(f"Empty playlist for {res}")
                        continue
                elif uri and res.get("playback") not in [
                    PlaybackType.SKILL, PlaybackType.UNDEFINED] and \
                        not any(
                            uri.startswith(e) for e in available_extractors()):
                    results[idx] = None  # can't play this search result!
                    LOG.error(f"stream handler not available for {res}")
                    continue

                # filter video results if GUI not connected
                if not has_gui:
                    # force allowed stream types to be played audio only
                    if res.get("media_type", "") in \
                            OCPSettings.cast2audio:
                        LOG.debug(
                            "unable to use GUI, forcing result to play audio only")
                        res["playback"] = PlaybackType.AUDIO
                        res["match_confidence"] -= 10
                        results[idx] = res

                if res not in self.search_playlist:
                    self.search_playlist.add_entry(res)
                    # update search UI
                    if self.gui and self.searching and res["match_confidence"] >= 30:
                        if self.gui.active_extension == "smartspeaker":
                            self.gui.display_notification(f"Found some results for {res['title']}")
                        else:
                            self.gui["footer_text"] = \
                                f"skill - {skill_id}\n" \
                                f"match - {res['title']}\n" \
                                f"confidence - {res['match_confidence']} "

            # remove filtered results
            message.data["results"] = [r for r in results if r is not None]
            self.query_replies.append(message.data)

            # abort searching if we gathered enough results
            # TODO ensure we have a decent confidence match, if all matches
            #  are < 50% conf extend timeout instead
            if time.time() - self.search_start > self.query_timeouts:
                if self.searching:
                    self.searching = False
                    LOG.debug("common play query timeout, parsing results")
                    if self.gui:
                        if self.gui.active_extension == "smartspeaker":
                            self.gui.display_notification("Parsing your results")
                        else:
                            self.gui["footer_text"] = "Timeout!\n " \
                                "selecting best result\n" \
                                " "

            elif self.searching:
                for res in message.data.get("results", []):
                    if res.get("match_confidence", 0) >= \
                            self.settings.early_stop_thresh:
                        # got a really good match, dont search further
                        LOG.info(
                            "Receiving very high confidence match, stopping "
                            "search early")
                        if self.gui:
                            if self.gui.active_extension == "smartspeaker":
                                self.gui.display_notification("Found a great match, stopping search")
                            else:
                                self.gui["footer_text"] = \
                                    f"High confidence match!\n " \
                                    f"skill - {skill_id}\n" \
                                    f"match - {res['title']}\n" \
                                    f"confidence - {res['match_confidence']} "
                        # allow other skills to "just miss"
                        if self.settings.early_stop_grace_period:
                            LOG.debug(
                                f"  - grace period: {self.settings.early_stop_grace_period} seconds")
                            time.sleep(self.settings.early_stop_grace_period)
                        self.searching = False
                        return

    def handle_skill_search_end(self, message):
        skill_id = message.data["skill_id"]
        LOG.debug(f"{message.data['skill_id']} finished search")
        if skill_id in self.active_skills:
            self.active_skills.remove(skill_id)

        # if this was the last skill end searching period
        time.sleep(0.5)
        # TODO this sleep is hacky, but avoids a race condition in
        # case some skill just decides to respond before the others even
        # acknowledge search is starting, this gives more than enough time
        # for self.active_seaching to be populated, a better approach should
        # be employed but this works fine for now
        if not self.active_skills and self.searching:
            LOG.info("Received search responses from all skills!")
            if self.gui:
                if self.gui.active_extension == "smartspeaker":
                    self.gui.display_notification("Selecting best result")
                else:
                    self.gui["footer_text"] = "Received search responses from all " \
                        "skills!\nselecting best result"

            self.searching = False
        if self.gui:
            self.gui.update_search_results()


class OCPSearch(OCPAbstractComponent):
    def __init__(self, player=None):
        super(OCPSearch, self).__init__(player)
        self.search_playlist = Playlist()
        self.old_cps = None
        self.ocp_skills = {}
        self.featured_skills = {}
        if player:
            self.bind(player)

    def bind(self, player):
        self._player = player
        self.old_cps = MycroftCommonPlayInterface() if \
            self.settings.backwards_compatibility else None
        if self.old_cps:
            self.old_cps.bind(player)
        self.add_event("ovos.common_play.skills.detach",
                       self.handle_ocp_skill_detach)
        self.add_event("ovos.common_play.announce",
                       self.handle_skill_announce)

    def shutdown(self):
        self.remove_event("ovos.common_play.announce")
        self.remove_event("ovos.common_play.skills.detach")

    def handle_skill_announce(self, message):
        skill_id = message.data.get("skill_id")
        skill_name = message.data.get("skill_name") or skill_id
        img = message.data.get("thumbnail")
        has_featured = bool(message.data.get("featured_tracks"))
        media_type = message.data.get("media_type") or [MediaType.GENERIC]

        if skill_id not in self.ocp_skills:
            self.ocp_skills[skill_id] = []

        if has_featured:
            LOG.debug(f"Found skill with featured media: {skill_id}")
            self.featured_skills[skill_id] = {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "thumbnail": img,
                "media_type": media_type
            }

    def handle_ocp_skill_detach(self, message):
        skill_id = message.data["skill_id"]
        if skill_id in self.ocp_skills:
            self.ocp_skills.pop(skill_id)
        if skill_id in self.featured_skills:
            self.featured_skills.pop(skill_id)

    def get_featured_skills(self, adult=False):
        # trigger a presence announcement from all loaded ocp skills
        self.bus.emit(Message("ovos.common_play.skills.get"))
        time.sleep(0.2)
        skills = list(self.featured_skills.values())
        if adult:
            return skills
        return [s for s in skills
                if MediaType.ADULT not in s["media_type"] and
                MediaType.HENTAI not in s["media_type"]]

    def search(self, phrase, media_type=MediaType.GENERIC):
        # stop any search still happening
        self.bus.emit(Message("ovos.common_play.search.stop"))
        if self.gui:
            if self.gui.active_extension == "smartspeaker":
                self.gui.display_notification("Searching...Your query is being processed")
            else:
                if self.gui.persist_home_display:
                    self.gui.show_search_spinner(persist_home=True)
                else:
                    self.gui.show_search_spinner(persist_home=False)
        self.clear()

        query = OCPQuery(query=phrase, media_type=media_type, ocp_search=self)
        query.send()

        # old common play will send the messages expected by the official
        # mycroft stack, but skills are known to over match, dont support
        # match type, and the GUI can be different for every skill, it may also
        # cause issues with status tracking and mess up playlists. An
        # imperfect compatibility layer has been implemented at skill and
        # audioservice level
        if self.old_cps:
            self.old_cps.send_query(phrase, media_type)

        query.wait()

        # fallback to generic search type
        if not query.results and \
                self.settings.search_fallback and \
                media_type != MediaType.GENERIC:
            LOG.debug("OVOSCommonPlay falling back to MediaType.GENERIC")
            query.media_type = MediaType.GENERIC
            query.reset()
            query.send()
            query.wait()

        if self.gui:
            self.gui.update_search_results()
        return query.results

    def search_skill(self, skill_id, phrase,
                     media_type=MediaType.GENERIC):
        res = [r for r in self.search(phrase, media_type)
               if r["skill_id"] == skill_id]
        if not len(res):
            return None
        return res[0]

    def select_best(self, results):
        # Look at any replies that arrived before the timeout
        # Find response(s) with the highest confidence
        best = None
        ties = []

        for res in results:
            if not best or res['match_confidence'] > best['match_confidence']:
                best = res
                ties = [best]
            elif res['match_confidence'] == best['match_confidence']:
                ties.append(res)

        if ties:
            # select randomly
            selected = random.choice(ties)

            if self.settings.video_only:
                # select only from VIDEO results if preference is set
                gui_results = [r for r in ties if r["playback"] ==
                               PlaybackType.VIDEO]
                if len(gui_results):
                    selected = random.choice(gui_results)
                else:
                    return None
            elif self.settings.audio_only:
                # select only from AUDIO results if preference is set
                audio_results = [r for r in ties if r["playback"] !=
                                 PlaybackType.VIDEO]
                if len(audio_results):
                    selected = random.choice(audio_results)
                else:
                    return None

            # TODO: Ask user to pick between ties or do it automagically
        else:
            selected = best
        LOG.debug(
            f"OVOSCommonPlay selected: {selected['skill_id']} - {selected['match_confidence']}")
        return selected

    def clear(self):
        self.search_playlist.clear()
        if self.gui:
            self.gui.update_search_results()

    def replace(self, playlist):
        self.search_playlist.clear()
        self.search_playlist.replace(playlist)
        if self.gui:
            self.gui.update_search_results()

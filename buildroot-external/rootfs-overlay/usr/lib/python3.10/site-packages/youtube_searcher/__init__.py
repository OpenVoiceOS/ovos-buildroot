import bs4
from youtube_searcher.session import session
from youtube_searcher.parse import extract_videos, \
    extract_videos_from_playlists, extract_playlists, _extract_json_blob


def search_youtube(query, location_code="US",
                   user_agent='Mozilla/5.0 (X11; Linux x86_64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.110 '
                              'Safari/537.36'):
    base_url = "https://www.youtube.com"
    headers = {
        'User-Agent': user_agent
    }
    params = {"search_query": query,
              "gl": location_code}

    # TODO dont cache if no results found
    html = session.get(base_url + "/results",
                       cookies={'CONSENT': 'PENDING+999'},
                       headers=headers, params=params).text

    soup = bs4.BeautifulSoup(html, 'html.parser')

    results = _extract_json_blob(soup)

    data = {"query": query, "corrected_query": query}

    videos = []
    playlists = []
    related_to_search = []
    related_queries = []
    radio = []
    movies = []
    promoted = []

    contents = results['contents']['twoColumnSearchResultsRenderer']
    primary_contents_list = contents["primaryContents"]["sectionListRenderer"]["contents"]
    # primary = primary_contents_list[0]['itemSectionRenderer']['contents']

    featured_channel = {"videos": [], "playlists": []}

    for section in primary_contents_list:
        if not section.get('itemSectionRenderer'):
            continue
        primary = section['itemSectionRenderer']['contents']
        # because order is not assured we need to make 2 passes over the data
        for vid in primary:
            if 'channelRenderer' in vid:
                vid = vid['channelRenderer']
                user = \
                vid['navigationEndpoint']['commandMetadata']['webCommandMetadata'][
                    'url']
                featured_channel["title"] = vid["title"]["simpleText"]
                if 'descriptionSnippet' in vid:
                    d = [r["text"] for r in vid['descriptionSnippet']["runs"]]
                else:  # ocasionally happens?
                    d = vid["title"]["simpleText"].split(" ")

                featured_channel["description"] = " ".join(d)
                featured_channel["user_url"] = base_url + user
                break

        for vid in primary:
            if 'videoRenderer' in vid:
                vid = vid['videoRenderer']
                thumb = vid["thumbnail"]['thumbnails']
                title = " ".join([r["text"] for r in vid['title']["runs"]])

                if 'descriptionSnippet' in vid:
                    desc = " ".join([
                        r["text"] for r in vid['descriptionSnippet']["runs"]])
                else:  # ocasionally happens
                    desc = title

                length_caption = \
                    vid.get("lengthText", {}).get('accessibility', {}).get("accessibilityData", {}).get("label")
                length_txt = vid.get("lengthText", {}).get('simpleText')
                videoId = vid['videoId']
                url = \
                    vid['navigationEndpoint']['commandMetadata'][
                        'webCommandMetadata'][
                        'url']

                videos.append(
                    {
                        "url": base_url + url,
                        "title": title,
                        "length": length_txt,
                        "length_human": length_caption,
                        "videoId": videoId,
                        "thumbnails": thumb,
                        "description": desc
                    }
                )
            elif 'shelfRenderer' in vid:
                entries = vid['shelfRenderer']
                # most recent from channel {title_from_step_above}
                # related to your search

                category = entries["title"]["simpleText"]
                # TODO category localization
                # this comes in lang from your ip address
                # not good to use as dict keys, can assumptions be made about
                # ordering and num of results? last item always seems to be
                # related artists and first (if any) featured channel
                ch = featured_channel.get("title", "")

                for vid in entries["content"]["verticalListRenderer"]['items']:
                    vid = vid['videoRenderer']
                    thumb = vid["thumbnail"]['thumbnails']
                    d = [r["text"] for r in vid['title']["runs"]]
                    title = " ".join(d)

                    length_caption = \
                        vid.get("lengthText", {}).get('accessibility', {}).get("accessibilityData", {}).get("label")

                    length_txt = vid.get("lengthText", {}).get('simpleText')
                    videoId = vid['videoId']
                    url = vid['navigationEndpoint']['commandMetadata'][
                        'webCommandMetadata']['url']

                    if ch and category.endswith(ch):
                        featured_channel["videos"].append(
                            {
                                "url": base_url + url,
                                "title": title,
                                "length": length_txt,
                                "length_human": length_caption,
                                "videoId": videoId,
                                "thumbnails": thumb
                            }
                        )
                    else:
                        related_to_search.append(
                            {
                                "url": base_url + url,
                                "title": title,
                                "length": length_txt,
                                "length_human": length_caption,
                                "videoId": videoId,
                                "thumbnails": thumb,
                                "reason": category
                            }
                        )
            elif 'playlistRenderer' in vid:
                # playlist
                vid = vid['playlistRenderer']
                playlist = {
                    "title": vid["title"]["simpleText"]
                }
                vid = vid['navigationEndpoint']
                playlist["url"] = \
                    base_url + vid['commandMetadata']['webCommandMetadata']['url']
                playlist["videoId"] = vid['watchEndpoint']['videoId']
                playlist["playlistId"] = vid['watchEndpoint']['playlistId']
                playlists.append(playlist)
            elif 'horizontalCardListRenderer' in vid:
                # alternative search (related artists)
                for vid in vid['horizontalCardListRenderer']['cards']:
                    vid = vid['searchRefinementCardRenderer']
                    url = \
                        vid['searchEndpoint']['commandMetadata'][
                            "webCommandMetadata"][
                            "url"]
                    related_queries.append({
                        "title": vid['searchEndpoint']['searchEndpoint']["query"],
                        "url": base_url + url,
                        "thumbnails": vid["thumbnail"]['thumbnails']
                    })
            elif 'radioRenderer' in vid:
                # playlist data
                vid = vid['radioRenderer']
                title = vid["title"]["simpleText"]
                thumb = vid["thumbnail"]['thumbnails']
                vid = vid['navigationEndpoint']
                url = vid['commandMetadata']['webCommandMetadata']['url']
                videoId = vid['watchEndpoint']['videoId']
                playlistId = vid['watchEndpoint']['playlistId']
                radio.append({
                    "title": title,
                    "thumbnails": thumb,
                    "url": base_url + url,
                    "videoId": videoId,
                    "playlistId": playlistId
                })
            elif 'movieRenderer' in vid:
                # full movies
                vid = vid['movieRenderer']
                title = " ".join([r["text"] for r in vid['title']["runs"]])
                thumb = vid["thumbnail"]['thumbnails']
                videoId = vid['videoId']
                meta = vid['bottomMetadataItems']
                meta = [m["simpleText"] for m in meta]
                desc = " ".join([r["text"] for r in vid['descriptionSnippet']["runs"]])
                url = vid['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']

                movies.append({
                    "title": title,
                    "thumbnails": thumb,
                    "url": base_url + url,
                    "videoId": videoId,
                    "metadata": meta,
                    "description": desc
                })
            elif 'carouselAdRenderer' in vid:
                vid = vid["carouselAdRenderer"]
                # skip ads
            elif 'showingResultsForRenderer' in vid:
                # auto correct for query
                q = vid['showingResultsForRenderer']['correctedQuery']
                data["corrected_query"] = " ".join([r["text"] for r in q["runs"]])
            elif 'searchPyvRenderer' in vid:
                for entry in vid['searchPyvRenderer']['ads']:
                    entry = entry['promotedVideoRenderer']
                    desc = entry["description"]['simpleText']
                    title = entry['longBylineText']['runs'][0]["text"]
                    try:
                        url = base_url + entry['longBylineText']['runs'][0][
                            'navigationEndpoint']['browseEndpoint']['canonicalBaseUrl']
                        promoted.append(
                            {"title": title,
                             "description": desc,
                             "url": url})
                    except Exception as e:
                        print(e)
            elif 'itemSectionRenderer' in vid:
                vid = vid['content']
                thumb = vid["thumbnail"]['thumbnails']
                title = " ".join([r["text"] for r in vid['title']["runs"]])

                if 'descriptionSnippet' in vid:
                    desc = " ".join([
                        r["text"] for r in vid['descriptionSnippet']["runs"]])
                else:  # ocasionally happens
                    desc = title

                length_caption = \
                    vid.get("lengthText", {}).get('accessibility', {}).get("accessibilityData", {}).get("label")
                length_txt = vid.get("lengthText", {}).get('simpleText')
                videoId = vid['videoId']
                url = \
                    vid['navigationEndpoint']['commandMetadata'][
                        'webCommandMetadata'][
                        'url']

                videos.append(
                    {
                        "url": base_url + url,
                        "title": title,
                        "length": length_txt,
                        "length_human": length_caption,
                        "videoId": videoId,
                        "thumbnails": thumb,
                        "description": desc
                    }
                )
            elif 'channelRenderer' in vid:
                continue  # handled in first pass
            else:
                print("If you see this output please open an issue with "
                      "DEBUG CODE: 1, and paste snippet bellow")
                print("/// START DEBUG INFO")
                print(query)
                print("/// END DEBUG INFO")
                continue

    if contents.get("secondaryContents"):
        secondary = \
        contents["secondaryContents"]["secondarySearchContainerRenderer"][
            "contents"][0]["universalWatchCardRenderer"]
        for vid in secondary["sections"]:
            entries = vid['watchCardSectionSequenceRenderer']
            for entry in entries['lists']:
                if 'verticalWatchCardListRenderer' in entry:
                    for vid in entry['verticalWatchCardListRenderer']["items"]:
                        try:
                            vid = vid['watchCardCompactVideoRenderer']
                            thumbs = vid['thumbnail']['thumbnails']

                            d = [r["text"] for r in vid['title']["runs"]]
                            title = " ".join(d)

                            url = vid['navigationEndpoint']['commandMetadata'][
                                'webCommandMetadata']['url']
                            videoId = vid['navigationEndpoint']['watchEndpoint'][
                                'videoId']
                            playlistId = \
                            vid['navigationEndpoint']['watchEndpoint'][
                                'playlistId']
                            length_caption = \
                                vid.get("lengthText", {}).get('accessibility', {}).get("accessibilityData", {}).get("label")
                            length_txt = vid.get("lengthText", {}).get('simpleText')

                            # TODO investigate
                            # These seem to always be from featured channel
                            # playlistId doesnt match any extracted playlist
                            featured_channel["videos"].append(
                                {
                                    "url": base_url + url,
                                    "title": title,
                                    "length": length_txt,
                                    "length_human": length_caption,
                                    "videoId": videoId,
                                    "playlistId": playlistId,
                                    "thumbnails": thumbs
                                }
                            )
                        except Exception as e:
                            print(e)

                elif 'horizontalCardListRenderer' in entry:
                    for vid in entry['horizontalCardListRenderer']['cards']:
                        vid = vid['searchRefinementCardRenderer']
                        playlistId = \
                        vid['searchEndpoint']['watchPlaylistEndpoint'][
                            'playlistId']
                        thumbs = vid['thumbnail']['thumbnails']
                        url = vid['searchEndpoint']['commandMetadata'][
                            'webCommandMetadata']['url']
                        d = [r["text"] for r in vid['query']["runs"]]
                        title = " ".join(d)
                        featured_channel["playlists"].append({
                            "url": base_url + url,
                            "title": title,
                            "thumbnails": thumbs,
                            "playlistId": playlistId
                        })
                else:
                    # Debug, never reached this point
                    print("If you see this output please open an issue with "
                          "DEBUG CODE: 2, and paste snippet bellow")
                    print("/// START DEBUG INFO")
                    print(query)
                    print(entry)
                    print("/// END DEBUG INFO")
                    continue

    data["videos"] = videos
    data["playlists"] = playlists
    data["featured_channel"] = featured_channel
    data["related_videos"] = related_to_search
    data["related_queries"] = related_queries
    data["full_movies"] = movies
    data["promoted"] = promoted
    return data

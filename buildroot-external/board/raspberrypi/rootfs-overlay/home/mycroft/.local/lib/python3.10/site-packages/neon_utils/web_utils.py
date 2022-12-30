# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from abc import ABC
from html.parser import HTMLParser


from neon_utils.logger import LOG

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.exceptions import ConnectTimeout
except ImportError:
    raise ImportError("requests or bs4 not available,"
                      " pip install neon-utils[network]")


def strip_tags(html):  # TODO: Document this! DM
    class MLStripper(HTMLParser, ABC):
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

    s = MLStripper()
    s.feed(html)
    return s.get_data()


def chunks(l, n):  # TODO: Document this! DM
    return [l[i:i + n] for i in range(0, len(l), n)]


def scrape_page_for_links(url: str) -> dict:
    """
    Scrapes the passed url for any links and returns a dictionary of link labels to URLs
    :param url: Web page to scrape
    :return: Lowercase names to links on page
    """
    import unicodedata
    available_links = {}
    retry_count = 0

    def _get_links(url):
        LOG.debug(url)
        try:
            html = requests.get(url, timeout=2.0).text
        except ConnectTimeout as e:
            raise e
        except Exception as e:
            LOG.warning(e)
            html = None
        if not str(url).startswith("http") and not html:
            request_url = f"https://{url}"
            try:
                html = requests.get(request_url, timeout=2.0).text
            except ConnectTimeout as e:
                raise e
            except Exception as e:
                LOG.warning(e)
                html = None
            if not html:
                try:
                    request_url = f"http://{url}"
                    html = requests.get(request_url, timeout=2.0).text
                except ConnectTimeout as e:
                    raise e
                except Exception as e:
                    LOG.warning(e)
                    html = None
            url = request_url

        LOG.debug(url)
        soup = BeautifulSoup(html, 'lxml')
        # LOG.debug(html)
        # LOG.debug(soup)

        # Look through the page and find all anchor tags
        for i in soup.find_all("a", href=True):
            # LOG.debug(f"DM: found link: {i.text.rstrip()}")
            # LOG.debug(f"DM: found href: {i['href']}")

            if '://' not in i['href']:
                # Assume this is a relative address
                href = url + i['href'].lower()
            elif url.split('://')[1] in i['href']:
                href = i['href'].lower()
            else:
                href = None

            if href:
                available_links[unicodedata.normalize('NFKD', i.text.rstrip()
                                                      .replace(u'\u2013', '')
                                                      .replace(u'\u201d', '')
                                                      .replace(u'\u201c', '')
                                                      .replace('"', "")
                                                      .replace("'", "")
                                                      .replace("&apos;", "")
                                                      .lower())] = href
                LOG.debug("found link: " + unicodedata.normalize("NFKD", i.text.rstrip().replace(u"\u2013", "")
                                                                 .replace(u"\u201d", "").replace(u"\u201c", "")
                                                                 .replace('"', "").replace("'", "")
                                                                 .replace("&apos;", "").replace("\n", "").lower()))
                LOG.debug("found href: " + href)

        LOG.debug(available_links)

    try:
        _get_links(url)
    except ConnectTimeout:
        retry_count += 1
        if retry_count < 8:
            _get_links(url)
        else:
            raise ConnectTimeout
    except Exception as x:
        LOG.error(x)
        LOG.debug(available_links)
        raise ReferenceError
    return available_links

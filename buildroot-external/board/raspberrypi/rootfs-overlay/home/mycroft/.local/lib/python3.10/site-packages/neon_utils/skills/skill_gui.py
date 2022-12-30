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

from os.path import join
from neon_utils.logger import LOG
from neon_utils.file_utils import resolve_neon_resource_file
from mycroft.enclosure.gui import SkillGUI as _SkillGUI


class SkillGUI(_SkillGUI):
    def __init__(self, skill):
        super().__init__(skill)
        self.serving_http = skill.config_core["skills"].get(
            "run_gui_file_server", False)

    def _pages2uri(self, page_names):
        # Convert pages to full reference
        page_urls = []
        for name in page_names:
            if name.startswith("SYSTEM"):
                if self.serving_http:
                    page = f"{self.remote_url}/system/ui/{name}"
                else:
                    page = resolve_neon_resource_file(join('ui', name))
            else:
                page = self.skill.find_resource(name, 'ui')
                if self.serving_http:
                    parts = page.split('/')
                    LOG.debug(parts)
                    path_suffix = join(*parts[(parts.index('ui') - 1):])
                    LOG.debug(path_suffix)
                    page = join(self.remote_url, "skills", path_suffix)
                    LOG.debug(page)
            if page:
                if self.remote_url and not self.serving_http:
                    page_urls.append(self.remote_url + "/" + page)
                elif "://" in page:
                    page_urls.append(page)
                else:
                    page_urls.append("file://" + page)
            else:
                # Unresolved files, try base implementation
                return super()._pages2uri(page_names)
        return page_urls

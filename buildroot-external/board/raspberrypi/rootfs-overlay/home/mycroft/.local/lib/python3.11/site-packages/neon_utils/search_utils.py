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

from neon_utils.logger import LOG


def search_convo_dict(id_to_keywords: dict, search_term: str,
                      max_matches_to_return: int = 5, handle_typos: bool = True) -> list:
    """
    Searches the passed id_to_keywords dict for id's matching the search_term
    :param id_to_keywords: dict of id to list of keywords to match
    :param search_term: string search term to locate
    :param max_matches_to_return: max number of sorted results to return
    :param handle_typos: boolean to allow inexact string matches
    :return: list of matched IDs
    """
    def _return_close_values(source_dict, to_find, num_of_return, typo_check=True) -> list:
        import difflib
        allow_diffs = 1  # if len(to_find) < 4 else 2

        perfect_match = [i for i, v in source_dict.items() if (isinstance(v, str) and to_find == v)
                         or (isinstance(v, list) and [x for x in v if to_find == x])]
        contains_in = [k for k, i in source_dict.items() if to_find in i or (isinstance(i, str) and i in to_find)
                       or (isinstance(i, list) and [x for x in i if x in to_find or to_find in x])]
        close_match = list(set(k for c in difflib.get_close_matches(to_find, source_dict.values())
                               for k, v in source_dict.items() if v == c))

        def check_diffs(i, k):
            len_i = len(i)
            len_tf = len(to_find)
            if abs(len_i - len_tf) > allow_diffs:
                return
            counter_i, counter_tf = 0, 0
            diff_count = 0
            while counter_i < len_i and counter_tf < len_tf:
                if to_find[counter_tf] != i[counter_i]:
                    diff_count += 1
                    if diff_count > allow_diffs:
                        break
                    if len_tf > len_i:
                        counter_tf += 1
                    elif len_i > len_tf:
                        counter_i += 1
                    else:
                        counter_i += 1
                        counter_tf += 1
                else:
                    counter_i += 1
                    counter_tf += 1

            if diff_count <= allow_diffs:
                typos_check.append(k)

        typos_check = []
        if typo_check:
            for k, i in source_dict.items():
                if isinstance(i, str):
                    check_diffs(i, k)
                elif isinstance(i, list):
                    for x in i:
                        if k not in typos_check:
                            check_diffs(x, k)

        LOG.debug(f"perfect match - {perfect_match}")
        LOG.debug(f'contains part - {contains_in}')
        LOG.debug(f"close_match - {close_match}")
        if typo_check:
            LOG.debug(f"typo check {allow_diffs} characters diff - {typos_check}")

        if not close_match and not contains_in and not perfect_match and not typos_check:
            return []
        try:
            res_tmp = typos_check
            res_tmp.extend([i for i in close_match if i not in typos_check])
            res_tmp.extend([i for i in contains_in if i not in close_match])
            LOG.debug(f'res_tmp is {res_tmp}')
        except Exception as x:
            LOG.debug(x)
            res_tmp = []

        if perfect_match:
            if len(perfect_match) == num_of_return:
                return perfect_match
            else:
                need_add = num_of_return - len(perfect_match)
                LOG.debug(len(perfect_match))
                LOG.debug(need_add)
                if need_add < 0:
                    return perfect_match[:num_of_return]

                res = perfect_match
                if res_tmp:
                    res.extend([i for i in res_tmp if i not in perfect_match])
                    LOG.debug(res)
        else:
            res = res_tmp

        if not res:
            raise ValueError("No results matched!")
        return res[:num_of_return]

    fin_res = []
    from collections import Counter
    import operator
    if not search_term:
        return []
    if " " in search_term:
        for i in search_term.split(" "):
            fin_res.extend(_return_close_values(id_to_keywords, i, max_matches_to_return, handle_typos))
        LOG.debug(fin_res)
        tmp_f = Counter(fin_res)
        LOG.debug(tmp_f)
        tmp = sorted(tmp_f.items(), key=operator.itemgetter(1), reverse=True)
        LOG.debug(tmp)
        return [i for i, m in tmp][:max_matches_to_return]
    return _return_close_values(id_to_keywords, search_term, max_matches_to_return, handle_typos)

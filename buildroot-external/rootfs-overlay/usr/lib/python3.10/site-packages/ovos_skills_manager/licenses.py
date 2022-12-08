LICENSE_MATCHERS = {
    "agpl-1.0": "AFFERO GENERAL PUBLIC LICENSE Version 1",
    "agpl-2.0": "GNU AFFERO GENERAL PUBLIC LICENSE Version 2",
    "agpl-3.0": "GNU AFFERO GENERAL PUBLIC LICENSE Version 3",
    "lgpl-2.0": "GNU LESSER GENERAL PUBLIC LICENSE Version 2",
    "lgpl-2.1": "GNU LESSER GENERAL PUBLIC LICENSE Version 2.1",
    "lgpl-3.0": "GNU LESSER GENERAL PUBLIC LICENSE Version 3",
    "gpl-1.0": "GNU GENERAL PUBLIC LICENSE Version 1",
    "gpl-2.0": "GNU GENERAL PUBLIC LICENSE Version 2",
    "gpl-3.0": "GNU GENERAL PUBLIC LICENSE Version 3",
    "cpl-1.0": "PROVIDED UNDER THE TERMS OF THIS COMMON PUBLIC LICENSE",
    "apache-1.0": "1995-1999 The Apache Group",
    "apache-1.1": "The Apache Software License, Version 1.1",
    "apache-2.0": "Apache License Version 2.0",
    "unlicense": "unlicense.org",
    "mit": "MIT License",
    "mpl-1.0": "Mozilla Public License Version 1.0",
    "mpl-1.1": "Mozilla Public License Version 1.1",
    "mpl-2.0": "Mozilla Public License Version 2.0",
    "bsl-1.0": "Boost Software License - Version 1.0",
    "zlib": "zlib License",
    "afl-3.0": 'Academic Free License ("AFL") v. 3.0',
    "artistic-2.0": "The Artistic License 2.0",
    "bsd-2-clause": "BSD 2-Clause License",
    "bsd-3-clause-clear": "The Clear BSD License",
    "bsd-3-clause": "BSD 3-Clause License",
    "bsd-4-clause": "BSD 4-Clause License",
    "cc-by-4.0": "Creative Commons Attribution 4.0",
    "cc-by-sa-4.0": "Attribution-ShareAlike 4.0 International",
    "cc0-1.0": "CC0 1.0 Universal",
    "cecill-2.1": "CONTRAT DE LICENCE DE LOGICIEL LIBRE CeCILL",
    "ecl-2.0": "Educational Community License",
    "epl-1.0": "Eclipse Public License - v 1.0",
    "epl-2.0": "Eclipse Public License - v 2.0",
    "eupl-1.2": "EUROPEAN UNION PUBLIC LICENCE v. 1.2",
    "eupl-1.1": "Licensed under the EUPL V.1.1",
    "isc": "ISC License",
    "lppl-1.3c": "LPPL Version 1.3c",
    "ms-pl": "Microsoft Public License (Ms-PL)",
    "ms-rl": "Microsoft Reciprocal License (Ms-RL)",
    "ncsa": "University of Illinois/NCSA Open Source License",
    "odbl-1.0": "ODC Open Database License (ODbL)",
    "osl-3.0": 'Open Software License ("OSL") v. 3.0',
    "postgresql": "PostgreSQL License",
    "upl-1.0": "The Universal Permissive License (UPL), Version 1.0",
    "vim": "VIM LICENSE",
    "wtfpl": "DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE",
    "rpsl-1.0": "RealNetworks Public Source License Version 1.0",
    "apsl-2.0": "APPLE PUBLIC SOURCE LICENSE Version 2.0",
    "neongecko": "Friendly Licensing: No charge, open source royalty free use of the Neon AI software source"
}


def is_permissive(license_type: str):
    if license_type in ["mit", "apache-2.0", "unlicense", "0bsd", "isc"]:
        return True
    return False


def is_viral(license_type: str):
    # GPL
    # With a strict view on the OpenSource definition, the GPL would be a non-free license.
    # In GPL section 8, it is permitted to add a clause that could restrict the GPL to give it's permission only to specific groups, but this would be in conflict with section 5 of the OpenSource definition.
    # Fortunately, there is no actual software that makes use of GPL section 8, so all currently existing GPLd software is compliant to the OpenSource definition.
    # The GPL prevents code flow from code under GPL into other works being under different even OSI compliant licenses.
    # Note that the GPL still permits collective works and thus allows linking against other independent works as long as this may be achieved by linking unmodified works or only slightly modified works.
    # As the GPL impairs collaboration and as the GPL, does not contain a method to defend against patent suing, the OSSCC does not recommend to use the GPL for new projects.

    # LGPL
    # With a strict view on the OpenSource definition, the LGPL would be a non-free license.
    # In LGPL section 12, it is permitted to add a clause that could restrict the LGPL to give it's permission only to specific groups, but this would be in conflict wth section 5 of the OpenSource definition.
    # Fortunately, there is no actual software that makes use of LGPL section 12, so all currently existing LGPLd software is compliant to the OpenSource definition.

    # The LGPL prevents code flow from code under LGPL into other works being under different OSI compliant licenses.
    # The LGPL however allows to non-LGPL works to link against a LGPL work.
    # As the LGPL does not allow code merging the OSSCC does not recommend to use the LGPL for new projects.

    # GPLv3
    # The GPLv3 has been published in June 2007. The GPLv3 no longer contains claims that are comparable to section 8 of the GPL, so the GPLv3 is a true OSS license.
    # The GPLv3 added claims to defend against patent suing.
    # Unfortunately, the GPLv3 tries to add further restrictions on collective works and as this is done by using an ambiguous wording,
    # it is expected to create a high risk to distributors for being sued by authors or Copyright holders.
    # As the GPLv3 impairs collaboration even more than the GPL, the OSSCC does not recommend to use the GPLv3 for new projects.

    # CPL
    # The CPL permits only contributions and anhancements to the original work but does not allow to use code from a CPL licensed work in another work.
    # So the CPL is even more restrictive than the GPL.
    # For this reason, the OSSCC does not recommend to use the CPL for new projects.

    # EPL
    # The EPL permits only contributions and anhancements to the original work but does not allow to use code from a EPL licensed work in another work.
    # So the EPL is even more restrictive than the GPL.
    # For this reason, the OSSCC does not recommend to use the EPL for new projects.

    if license_type in ["agpl-1.0", "agpl-2.0", "agpl-3.0", "lgpl-2.0",
                        "lgpl-2.1", "lgpl-3.0", "gpl-1.0", "gpl-2.0",
                        "gpl-3.0", "epl-1.0", "epl-2.0", "cpl-1.0"]:
        return True
    return False


def _check_template(lic: str, template: str) -> bool:
    lines = [l for l in lic.lower().split("\n") if l.strip()]
    lic = ''.join(filter(str.isalpha, lic)).lower()
    t = ''.join(filter(str.isalpha, template)).lower()

    if t == lic:
        return True

    # account for copyright in first line
    if "copyright" in lines[0]:
        lic = "\n".join(lines[1:])
        return _check_template(lic, template)
    return False


def _is_0bsd(lic: str):
    template = """
    Permission to use, copy, modify, and distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
    """
    return _check_template(lic, template)


def _is_isc(lic: str):
    template = """
    Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
    """
    return _check_template(lic, template)


def _is_mit(lic: str):
    template = """
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """
    return _check_template(lic, template)


def parse_license_type(lic: str) -> str:
    # assumptions
    # - license header is somewhere in the first 10 lines
    # - license list is ordered in a way that first match NEEDS to override others

    # quick and dirty
    header = "\n".join(lic.split("\n")[:30]).lower() \
        .replace(" ", "").replace("\n", "").replace("\r", "") \
        .replace("\t", "").replace(",", "")

    for k, v in LICENSE_MATCHERS.items():
        if v.lower().replace(" ", "").replace(",", "") in header:
            return k

    if _is_isc(lic):
        return "isc"

    if _is_0bsd(lic):
        return "0bsd"

    if _is_mit(lic):
        return "mit"

    return lic.strip().split("\n")[0]

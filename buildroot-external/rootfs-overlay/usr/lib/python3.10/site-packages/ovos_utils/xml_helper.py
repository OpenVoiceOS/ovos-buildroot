from collections import defaultdict
from xml.etree import cElementTree as ET


def etree2dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree2dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update((k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['text'] = text
        else:
            d[t.tag] = text
    return d


def xml2dict(xml_string):
    try:
        xml_string = xml_string.replace('xmlns="http://www.w3.org/1999/xhtml"',
                                        "")
        e = ET.XML(xml_string)
        d = etree2dict(e)
        return d
    except:
        return {}


def load_xml2dict(xml_path):
    tree = ET.parse(xml_path)
    d = etree2dict(tree.getroot())
    return d["xml"]


def dict2xml(d, root="xml"):
    xml = "<" + root
    # props
    for k in d:
        if isinstance(d[k], str):
            if k == "text":
                pass
            else:
                xml += " " + k + ' ="' + d[k] + '"'

    xml += ">"
    # insides
    for k in d:
        if isinstance(d[k], dict):
            xml += dict2xml(d[k], k)
        if isinstance(d[k], list):
            for e in d[k]:
                if isinstance(e, dict):
                    xml += dict2xml(e, k)
        if isinstance(d[k], str):
            if k == "text":
                xml += d[k]

    xml += "</" + root + ">"
    return xml

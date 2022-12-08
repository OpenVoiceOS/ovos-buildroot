from dateutil.tz import gettz, tzlocal
import ovos_config

# lingua_franca is optional and might not be installed
# exceptions should only be raised in the parse and format utils


try:
    import lingua_franca as LF
except ImportError:
    LF = None

_lang = None
_default_tz = None


def get_primary_lang_code(config=None):
    global _lang
    if LF:
        return LF.get_primary_lang_code()
    if not _lang:
        config = config or ovos_config.Configuration()
        _lang = config.get("lang", "en-us")
    return _lang.split("-")[0]


def get_default_lang(config=None):
    """
    Get the default localized language code (i.e. `en-us`)
    @param config: Configuration (default is Configuration())
    @return: lowercase BCP-47 language code
    """
    global _lang
    if LF and LF.get_default_loc():
        return LF.get_default_loc()
    if not _lang:
        config = config or ovos_config.Configuration()
        _lang = config.get("lang", "en-us")
    return _lang


def set_default_lang(lang):
    global _lang
    _lang = lang
    if LF:
        LF.set_default_lang(lang)


def get_config_tz():
    code = ovos_config.Configuration()["location"]["timezone"]["code"]
    return gettz(code)


def get_default_tz():
    # if default was set at runtime use it else use the timezone from .conf
    return _default_tz or get_config_tz()


def set_default_tz(tz=None):
    """ configure LF """
    global _default_tz
    tz = tz or get_config_tz() or tzlocal()
    _default_tz = tz
    if LF:
        # tz added in recently, depends on version
        try:
            LF.time.set_default_tz(tz)
        except:
            pass


def load_languages(langs):
    if LF:
        LF.load_languages(langs)


def load_language(lang):
    if LF:
        LF.load_language(lang)


def setup_locale(lang=None, tz=None):
    lang_code = lang or ovos_config.Configuration().get("lang", "en-us")
    # Load language resources, currently en-us must also be loaded at all times
    load_languages([lang_code, "en-us"])
    # Set the active lang to match the configured one
    set_default_lang(lang_code)
    # Set the default timezone to match the configured one
    set_default_tz(tz)


# mycroft-core backwards compat LF only interface
def set_default_lf_lang(lang_code="en-us"):
    """Set the default language of Lingua Franca for parsing and formatting.

    Note: this is a temporary method until a global set_default_lang() method
    can be implemented that updates all Mycroft systems eg STT and TTS.
    It will be deprecated at the earliest possible point.

    Args:
        lang (str): BCP-47 language code, e.g. "en-us" or "es-mx"
    """
    return set_default_lang(lang_code)

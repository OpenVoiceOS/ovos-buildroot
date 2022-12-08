from ovos_utils.system import search_mycroft_core_location, is_running_from_module
from ovos_utils.xdg_utils import (
    xdg_config_home,
    xdg_config_dirs,
    xdg_data_home,
    xdg_data_dirs,
    xdg_cache_home
)
from ovos_utils.log import LOG

from ovos_config.locations import (
    get_xdg_config_dirs,
    get_xdg_data_dirs,
    get_xdg_data_save_path,
    get_xdg_config_save_path,
    get_xdg_cache_save_path,
    find_default_config,
    find_user_config,
    get_config_locations,
    get_webcache_location,
    get_xdg_config_locations
)

from ovos_config.locale import get_default_lang
from ovos_config.meta import (
    get_ovos_config,
    get_ovos_default_config_paths,
    is_using_xdg,
    get_xdg_base,
    set_xdg_base,
    set_config_filename,
    set_default_config,
    get_config_filename
)

from ovos_config.config import (
    read_mycroft_config,
    update_mycroft_config
)

from ovos_config.models import (
    LocalConf,
    ReadOnlyConfig,
    MycroftUserConfig,
    MycroftDefaultConfig,
    MycroftSystemConfig,
    MycroftXDGConfig
)

from ovos_config.meta import save_ovos_config as save_ovos_core_config

LOG.warning("configuration moved to the `ovos_config` package. This submodule "
            "will be removed in ovos_utils 0.1.0")


def set_config_name(name, core_folder=None):
    # TODO deprecate, was only out in a couple versions
    LOG.warning("This reference is deprecated, use "
                "`ovos_config.meta.set_config_filename`")
    # renamed to match HolmesV
    set_config_filename(name, core_folder)

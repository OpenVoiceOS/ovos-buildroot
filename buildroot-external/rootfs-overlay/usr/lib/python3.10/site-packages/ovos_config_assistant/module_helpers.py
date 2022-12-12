from importlib.util import find_spec

from ovos_config import get_ovos_config


def get_module_path(module_name):
    spec = find_spec(module_name)
    if spec:
        if spec.submodule_search_locations:
            return spec.submodule_search_locations[0]
        if spec.origin:
            return spec.origin


def pprint_core_module_info():
    config = get_ovos_config()
    spec = get_module_path("mycroft")
    print("\n## Mycroft module info")
    print("     can import mycroft     :", spec is not None)
    print("     is ovos-core           :", "/ovos-core/mycroft" in spec)
    print("     mycroft module location:", spec)

    cores = config.get("module_overrides") or {}
    if cores:
        print("\n## Downstream ovos.conf overrides")
        for k, v in cores.items():
            spec = get_module_path(k)
            print("Module:", k)
            print(f"     can import {k}     :", spec is not None)
            print(f"     {k} module location:", spec)

            module_conf = {**config, **v}
            print("     xdg compliance            :", module_conf["xdg"])
            print("     base xdg folder           :", module_conf["base_folder"])
            print("     mycroft config filename   :", module_conf["config_filename"])
            print("     default mycroft.conf path :")
            print("         ", module_conf["default_config_path"])

        subcores = config.get("submodule_mappings") or {}
        if subcores:
            print("\n## Downstream module overrides:")
            for k, v in subcores.items():
                spec = get_module_path(k)
                print("Module:", k)
                print("     uses config from   :", v)
                print(f"     can import {k}     :", spec is not None)
                print(f"     {k} module location:", spec)


if __name__ == "__main__":
    pprint_core_module_info()
    """
    ## Mycroft module info
         can import mycroft     : True
         mycroft module location: /home/user/ovos-core/mycroft/__init__.py

    ## Downstream ovos.conf overrides
    Module: neon_core
         can import neon_core     : False
         neon_core module location: None
    Module: hivemind
         can import hivemind     : False
         hivemind module location: None

    ## Downstream module overrides:
    Module: neon_speech
         uses config from   : neon_core
         can import neon_speech     : False
         neon_speech module location: None
    Module: neon_audio
         uses config from   : neon_core
         can import neon_audio     : False
         neon_audio module location: None
    Module: neon_enclosure
         uses config from   : neon_core
         can import neon_enclosure     : False
         neon_enclosure module location: None
    Module: hivemind_voice_satellite
         uses config from   : hivemind
         can import hivemind_voice_satellite     : True
         hivemind_voice_satellite module location: /home/user/HiveMind-voice-sat/hivemind_voice_satellite
    """

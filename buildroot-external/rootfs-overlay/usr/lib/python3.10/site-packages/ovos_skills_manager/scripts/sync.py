import click
from ovos_skills_manager import OVOSSkillsManager


APPSTORE_OPTIONS = ["ovos", "mycroft", "pling", "andlo", "neon", "default", "all"]


def sync(appstore: str, rebuild: bool, merge: bool, github: bool):
    osm = OVOSSkillsManager()
    if github:
        click.echo("WARNING: parsing github can be VERY SLOW!")
        click.confirm('Are you sure you want to parse github?', abort=True)
        for k, s in list(osm.config["appstores"].items()):
            osm.config["appstores"][k]["parse_github"] = True

    if appstore == "all":
        for s in APPSTORE_OPTIONS:
            if s != "all" and s != "default":
                osm.enable_appstore(s)
    elif appstore != "default":
        for s in APPSTORE_OPTIONS:
            if s != appstore and s != "default" and s != "all":
                osm.disable_appstore(s)
        osm.enable_appstore(appstore)

    click.echo("Active appstores: " + ", ".join(osm.get_active_appstores()))
    osm.sync_appstores(new_only=not rebuild, merge=merge)


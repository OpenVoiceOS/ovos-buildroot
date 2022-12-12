import click
from ovos_skills_manager import OVOSSkillsManager

APPSTORE_OPTIONS = ["ovos", "mycroft", "pling", "andlo", "neon", "all"]


def disable(appstore: str):
    osm = OVOSSkillsManager()
    original = osm.get_active_appstores()
    click.echo("Currently active appstores: " + ", ".join(original))
    if appstore == "all":
        click.echo("You will only be able to install skills by url")
        click.confirm('Do you want to disable all appstores?', abort=True)
        for s in APPSTORE_OPTIONS:
            if s != "all":
                osm.disable_appstore(s)
    else:
        click.confirm('Do you want to disable {s}?'.format(s=appstore),
                      abort=True)
        osm.disable_appstore(appstore)

    osm.config.store()
    click.echo("Active appstores: " + ", ".join(osm.get_active_appstores()))


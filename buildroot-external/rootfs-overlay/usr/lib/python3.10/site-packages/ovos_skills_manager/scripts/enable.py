import click
from ovos_skills_manager import OVOSSkillsManager

APPSTORE_OPTIONS = ["ovos", "mycroft", "pling", "andlo", "neon", "all"]


def enable(appstore: str):
    osm = OVOSSkillsManager()
    original = osm.get_active_appstores()
    click.echo("Currently active appstores: " + ", ".join(original))
    if appstore == "all":
        for s in APPSTORE_OPTIONS:
            if s != "all":
                osm.enable_appstore(s)
    else:
        osm.enable_appstore(appstore)

    new = osm.get_active_appstores()

    activated = [s for s in new if s not in original]
    if len(activated):
        click.confirm('Do you want to enable {s} ?'.format(s=", ".join(activated)),
                      abort=True)
        click.echo("New active appstores: " + ", ".join(new))

        osm.config.store()
    else:
        click.echo("No new appstores to enable")


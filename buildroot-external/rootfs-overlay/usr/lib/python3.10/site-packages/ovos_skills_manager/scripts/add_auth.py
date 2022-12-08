import click
from ovos_skills_manager import OVOSSkillsManager

APPSTORE_OPTIONS = ["neon"]

def add_auth(appstore: str, token: str):
    osm = OVOSSkillsManager()
    osm.set_appstore_auth_token(appstore, token)
    prompt = f"Appstore token:\n{token}"
    click.echo(prompt)
    click.confirm('Save changes?', abort=True)
    osm.config.store()
    click.echo("changes saved!")


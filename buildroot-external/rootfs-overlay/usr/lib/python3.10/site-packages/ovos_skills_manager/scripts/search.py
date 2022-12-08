import click
from ovos_skills_manager import OVOSSkillsManager
from ovos_skills_manager.session import set_github_token

SEARCH_OPTIONS = ['all', 'name', 'url', 'category', 'author', 'tag',
                  'description']
APPSTORE_OPTIONS = ["ovos", "mycroft", "pling", "andlo", "neon", "default", "all"]


def search_skill(method: str, query: str, fuzzy: bool, no_ignore_case: bool, thresh: float, appstore: str):
    osm = OVOSSkillsManager()
    token = osm.config["appstores"].get(appstore, {}).get("auth_token")
    if token:
        set_github_token(token)

    ignore_case = not no_ignore_case
    thresh = thresh / 100

    if appstore == "all":
        for s in APPSTORE_OPTIONS:
            if s != "all" and s != "default":
                osm.enable_appstore(s)
    elif appstore != "default":
        for s in APPSTORE_OPTIONS:
            if s != appstore and s != "default" and s != "all":
                osm.disable_appstore(s)
        osm.enable_appstore(appstore)

    if method == "name":
        skills = [s for s in osm.search_skills_by_name(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]
    elif method == "url":
        skills = [s for s in osm.search_skills_by_url(query)]
    elif method == "category":
        skills = [s for s in osm.search_skills_by_category(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]
    elif method == "author":
        skills = [s for s in osm.search_skills_by_author(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]
    elif method == "tag":
        skills = [s for s in osm.search_skills_by_tag(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]
    elif method == "description":
        skills = [s for s in osm.search_skills_by_description(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]
    else:
        skills = [s for s in osm.search_skills(
            query, fuzzy=fuzzy, ignore_case=ignore_case, thresh=thresh)]

    return skills


def search(method: str, query: str, fuzzy: bool, no_ignore_case: bool, thresh: float, appstore: str):
    skills = search_skill(method, query, fuzzy, no_ignore_case,
                          thresh, appstore)

    if not len(skills):
        click.echo("NO RESULTS")
    else:
        for s in skills:
            click.echo(s)

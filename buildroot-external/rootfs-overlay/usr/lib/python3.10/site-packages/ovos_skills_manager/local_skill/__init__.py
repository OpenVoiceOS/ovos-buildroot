import json

from os import walk
from os.path import join, isfile

from ovos_utils.json_helper import merge_dict

from ovos_skills_manager.licenses import parse_license_type
from ovos_skills_manager.requirements import validate_manifest
from ovos_skills_manager.github.utils import (
    GITHUB_README_FILES,
    GITHUB_JSON_FILES,
    GITHUB_DESKTOP_FILES,
    GITHUB_ICON_FILES,
    GITHUB_LICENSE_FILES,
    GITHUB_LOGO_FILES,
    GITHUB_REQUIREMENTS_FILES,
    GITHUB_SKILL_REQUIREMENTS_FILES,
    GITHUB_MANIFEST_FILES, author_repo_from_github_url
)
from ovos_skills_manager.utils import readme_to_json


def get_skill_data_from_directory(skill_dir: str):
    """
    Parse the specified skill directory and return a dict representation of a
    SkillEntry.
    @param skill_dir: path to skill directory
    @return: dict parsed skill data
    """
    skills, fold = skill_dir.rsplit('/', 1)
    skill_data = {
        "appstore": "InstalledSkills",
        "appstore_url": skills,
        "skill_id": fold,
        "requirements": {"python": [], "system": {}, "skill": []}
    }

    # if installed by msm/osm will obey this convention
    if "." in fold:
        try:
            repo, author = fold.split(".")
            skill_data["skillname"] = repo
            skill_data["authorname"] = author
            skill_data["url"] = f'https://github.com/{author}/{repo}'
        except:  # TODO replace with some clever check ?
            pass

    # parse git info
    gitinfo = join(skill_dir, ".git/config")
    if isfile(gitinfo):
        with open(gitinfo) as f:
            for l in f.readlines():
                if l.strip().startswith("url ="):
                    skill_data["url"] = l.split("url =")[-1].strip()
                    skill_data["authorname"], skill_data["skillname"] = \
                        author_repo_from_github_url(skill_data["url"])
                if l.strip().startswith("[branch "):
                    skill_data["branch"] = l.split("branch")[-1] \
                        .replace('"', "").strip()

    # parse skill files
    for root_dir, _, files in walk(skill_dir):
        for f in files:
            if f in GITHUB_JSON_FILES:  # skill.json
                with open(join(root_dir, f)) as fi:
                    skill_meta = json.load(fi)
                skill_data = merge_dict(skill_data, skill_meta,
                                        merge_lists=True)
            elif f in GITHUB_README_FILES:
                with open(join(root_dir, f)) as fi:
                    readme = readme_to_json(fi.read())
                skill_data = merge_dict(skill_data, readme,
                                        new_only=True, merge_lists=True)
            elif f in GITHUB_DESKTOP_FILES:
                skill_data['desktopFile'] = True
            elif f in GITHUB_ICON_FILES:
                skill_data["icon"] = join(root_dir, f)
            elif f in GITHUB_LICENSE_FILES:
                with open(join(root_dir, f)) as fi:
                    lic = fi.read()
                skill_data["license"] = parse_license_type(lic)
            elif f in GITHUB_LOGO_FILES:
                skill_data["logo"] = join(root_dir, f)
            elif f in GITHUB_MANIFEST_FILES:
                with open(join(root_dir, f)) as fi:
                    manifest = validate_manifest(fi.read()).get("dependencies", {})
                skill_data["requirements"]["python"] += \
                    manifest.get("python") or []
                skill_data["requirements"]["system"] = \
                    merge_dict(skill_data["requirements"]["system"],
                               manifest.get("system") or {}, merge_lists=True)

                skill_data["requirements"]["skill"] += \
                    manifest.get("skill") or []
            elif f in GITHUB_REQUIREMENTS_FILES:
                with open(join(root_dir, f)) as fi:
                    reqs = [r for r in fi.read().split("\n") if r.strip()
                            and not r.strip().startswith("#")]
                skill_data["requirements"]["python"] += reqs
            elif f in GITHUB_SKILL_REQUIREMENTS_FILES:
                with open(join(root_dir, f)) as fi:
                    reqs = [r for r in fi.read().split("\n") if r.strip()
                            and not r.strip().startswith("#")]
                skill_data["requirements"]["skill"] += reqs
    # de-dupe requirements
    skill_data["requirements"]["python"] = \
        list(set(skill_data["requirements"]["python"]))
    skill_data["requirements"]["skill"] = \
        list(set(skill_data["requirements"]["skill"]))
    skill_data['foldername'] = fold  # Override what the config specifies
    skill_data['authorname'] = skill_data.get('authorname') or "local"
    return skill_data

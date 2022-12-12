from ovos_skills_manager.skill_entry import SkillEntry
from ovos_skills_manager.appstores.andlo import AndloSkillList
from ovos_skills_manager.appstores.mycroft_marketplace import MycroftMarketplace
from ovos_skills_manager.appstores.pling import Pling
from ovos_skills_manager.appstores.ovos import OVOSstore
from ovos_skills_manager.appstores.neon import NeonSkills
from ovos_skills_manager.appstores.local import InstalledSkills
from ovos_skills_manager.osm import OVOSSkillsManager
from ovos_skills_manager.upgrade_osm import do_launch_version_checks
from ovos_utils.log import LOG

LOG.set_level("INFO")
do_launch_version_checks()

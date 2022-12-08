import click
from click_default_group import DefaultGroup

''' 
    Regions are used not only for convenience while editing, but because complex Click
    definitions in a monolithic file are sometimes difficult to navigate. However, they
    are easier to set up than the alternative.
'''

#region IMPORT SCRIPTS
#not the greatest import snippet you've ever seen, but it made for an easy refactor!
from ovos_skills_manager.scripts import \
    add_auth as _add_auth, \
    config_print as _config_print, \
    disable as _disable, \
    enable as _enable, \
    install as _install, \
    priority as _priority, \
    search as _search, \
    sync as _sync, \
    version as _version
#endregion


#region COMMAND DEFINITIONS

@click.group(name='osm', cls=DefaultGroup, default='\0',
    help="See also: osm COMMAND --help",
    no_args_is_help=True, invoke_without_command=True)
@click.option('--version', help='Print current OSM version and exit.', is_flag=True, required=False)
def osm_commands(version:bool=False):
    if version:
        _version.echo_version()

#region add-auth
@osm_commands.command(help='Add an auth token')
@click.option('--appstore', prompt='select appstore',
              type=click.Choice(_add_auth.APPSTORE_OPTIONS),
              help='add auth token for a specific appstore')
@click.option('--token', type=str,
              prompt='Auth Token',
              help='GitHub Personal Access Token')
def add_auth(appstore, token):
    _add_auth.add_auth(appstore, token)
#endregion add-auth

#region config
@osm_commands.command(help="Print an appstore's config")
@click.option('--appstore', default="all",
              type=click.Choice(_config_print.APPSTORE_OPTIONS),
              help='print config of a specific appstore')
def print_config(appstore):
    _config_print.print_config(appstore)
#endregion config

#region disable
@osm_commands.command(help='Disable an appstore')
@click.argument('appstore', required=False)
def disable(appstore):
    if appstore is None:
        appstore = click.prompt('select appstore to enable',
                    type=click.Choice(_enable.APPSTORE_OPTIONS))
    _disable.disable(appstore)
#endregion disable

#region enable
@osm_commands.command(help='Enable an appstore')
@click.argument('appstore', required=False)
def enable(appstore):
    if appstore is None:
        appstore = click.prompt('select appstore to enable',
                    type=click.Choice(_enable.APPSTORE_OPTIONS))
    _enable.enable(appstore)
#endregion enable

#region install
@osm_commands.command(help='Install a Skill')
@click.argument('skill', required=False)
@click.option('--branch', type=str,
              help='select skill github branch to use')
@click.option('--folder', type=str, default=None,
              help='path where skill will be installed, default from assistant config')
@click.option('--search', default=False, is_flag=True,
              help="search appstores, otherwise assume it's a github url")
@click.option('--appstore', default="default",
              type=click.Choice(_install.APPSTORE_OPTIONS),
              help='search a specific appstore, default search '
                   'appstores enabled in config file')
@click.option('--method', default="all",
              type=click.Choice(_install.SEARCH_OPTIONS),
              help='match this metadata field when searching')
@click.option('--fuzzy/--exact', default=True,
              help='exact or fuzzy matching, default fuzzy')
@click.option('--thresh', type=click.IntRange(0, 100, clamp=True), default=80,
              help='fuzzy matching threshold from 0 (everything is a match) '
                   'to 100 (exact match),  default 80')
@click.option('--no-ignore-case', default=False, is_flag=True,
              help='ignore upper/lower case, default ignore')
@click.option('--non-interactive', default=False, is_flag=True,
              help='install single skill non-interactive from url and branch')
def install(method, skill, fuzzy, no_ignore_case, thresh, appstore, search,
            branch, folder, non_interactive):
    if skill is None:
        skill = click.prompt('Skill to install (url or search term)')
    _install.install(method, skill, fuzzy, no_ignore_case, thresh, appstore, search,
            branch, folder, non_interactive)
#endregion install

#region priority
@osm_commands.command(help="Set an appstore's priority")
@click.option('--appstore', prompt='select appstore',
              type=click.Choice(_priority.APPSTORE_OPTIONS),
              help='change priority of a specific appstore')
@click.option('--priority', type=click.IntRange(0, 100, clamp=True),
              prompt='new appstore priority',
              help='appstore priority, from 0 (highest) to 100 (lowest)')
def priority(appstore, priority):
    _priority.priority(appstore, priority)
#endregion priority

#region search
@osm_commands.command(help='Search for Skills')
@click.argument('query', required=False)
@click.option('--method', default="all",
              type=click.Choice(_search.SEARCH_OPTIONS),
              help='match this metadata field when searching')
@click.option('--appstore', default="default",
              type=click.Choice(_search.APPSTORE_OPTIONS),
              help='search a specific appstore, by default searches '
                   'appstores enabled in config file')
@click.option('--fuzzy/--exact', default=True, help='exact or fuzzy matching')
@click.option('--thresh', type=click.IntRange(0, 100, clamp=True), default=80,
              help='fuzzy matching threshold from 0 (everything is a match) '
                   'to 100 (exact match)')
@click.option('--no-ignore-case', default=False, is_flag=True,
              help='ignore upper/lower case')
def search(method, query, fuzzy, no_ignore_case, thresh, appstore):
    if query is None:
        query = click.prompt('Search term')
    _search.search(method, query, fuzzy, no_ignore_case, thresh, appstore)
#endregion search

#region sync
@osm_commands.command(help="Sync Skill catalogs")
@click.option('--appstore', default="default",
              type=click.Choice(_sync.APPSTORE_OPTIONS),
              help='sync a specific appstore, default syncs'
                   ' appstores enabled in config file')
@click.option('--rebuild', default=True, is_flag=True,
              help='rebuild skill database, if not set only sync data for new '
                   'skills')
@click.option('--merge', default=False, is_flag=True,
              help='merge skill data, if not set replaces skill entries')
@click.option('--github', default=False, is_flag=True,
              help='augment skill data from github, by default only saves '
                   'data provided directly by the appstore')
def sync(appstore, rebuild, merge, github):
    _sync.sync(appstore, rebuild, merge, github)
#endregion sync

#endregion COMMAND DEFINITIONS
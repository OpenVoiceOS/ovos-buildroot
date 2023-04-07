# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import click

from click_default_group import DefaultGroup


@click.group("sj201", cls=DefaultGroup,
             no_args_is_help=True, invoke_without_command=True,
             help="SJ201 Commands\n\n"
                  "See also: sj201 COMMAND --help")
@click.option("--version", "-v", is_flag=True, required=False,
              help="Print the current version")
def sj201_cli(version: bool = False):
    if version:
        from sj201_interface.version import __version__
        click.echo(f"Neon version {__version__}")


@sj201_cli.command(help="Initialize TAS5806")
def init_ti_amp():
    from sj201_interface.util.tas5806 import init_tas5806
    init_tas5806()
    click.echo("TI Amp Initialized")


@sj201_cli.command(help="LED Reset Animation")
@click.argument('color')
def reset_led(color=None):
    from sj201_interface.led import Palette, reset_led_animation
    color = color or "green"
    for col in Palette:
        if col.name.lower() == color.lower():
            color = col
            break
    if not isinstance(color, Palette):
        color = None
    reset_led_animation(color)


@sj201_cli.command(help="Set Fan Speed Percent")
@click.argument("speed")
def set_fan_speed(speed=100):
    speed = int(round(float(speed)))
    from sj201_interface.fan import get_fan
    from sj201_interface.revisions import detect_sj201_revision, SJ201
    rev = detect_sj201_revision()
    if rev == SJ201.r10 and speed == 0:
        click.echo("Turning off R10 Fan")
        get_fan(rev).shutdown()
        exit(0)
    get_fan(rev).set_fan_speed(speed)
    click.echo(f"Set fan speed to {speed}")


@sj201_cli.command(help="Patch config.txt for SJ201R10")
def patch_config_txt():
    from sj201_interface.revisions import detect_sj201_revision, SJ201
    from sj201_interface.util.patches import patch_r10_config_txt
    if detect_sj201_revision() == SJ201.r10:
        click.echo("Patching config.txt for SJ201r10")
        patch_r10_config_txt()


@sj201_cli.command(help="Get a string representation of the detected board")
def get_revision():
    from sj201_interface.revisions import detect_sj201_revision
    version = detect_sj201_revision()
    version = version.value if version else '0'
    click.echo(version)
    exit(version)

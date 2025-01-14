# coding:utf-8

from typing import Optional
from typing import Sequence

from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from .attribute import __project__
from .attribute import __urlhome__
from .attribute import __version__
from .sitepage import page


@add_command("download", help="Download webpage")
def add_cmd_download(_arg: argp):
    _arg.add_argument(dest="url", type=str, nargs=1, metavar="URL",
                      help="uniform resource locator")


@run_command(add_cmd_download)
def run_cmd_download(cmds: commands) -> int:
    url: str = cmds.args.url[0]
    cmds.stdout(page(url).fetch())
    return 0


@add_command(__project__)
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_download)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="Get webpage. Generate response.",
        epilog=f"For more, please visit {__urlhome__}.")

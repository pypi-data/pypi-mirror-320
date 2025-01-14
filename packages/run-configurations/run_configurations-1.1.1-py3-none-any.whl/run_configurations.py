#!/usr/bin/env python3

import logging
import os
import stat
import subprocess
import sys
from glob import glob
from pathlib import Path
from shutil import which
from typing import Any, List, Tuple

import click
from Levenshtein import distance as levenshtein_distance

RUN_CONFIGS_DIR: str = ".run_configs"
LEVENSHTEIN_MAX_DISTANCE: int = 1000


PathNotFoundError = Exception


def get_help_text(run_config: Path) -> str:
    # TODO: stub
    return str(run_config.absolute())


def get_base_dir() -> Path:
    cwd = Path(os.getcwd())
    try:
        rc_path = next(cwd.glob(RUN_CONFIGS_DIR))
        if rc_path.is_dir():
            return cwd
    except StopIteration:
        ...
    for path in cwd.parents:
        try:
            rc_path = next(path.glob(RUN_CONFIGS_DIR))
            if rc_path.is_dir():
                return path
        except StopIteration:
            ...
    raise click.UsageError(
        f"No {RUN_CONFIGS_DIR} found in current path or its parents."
    )


def get_rc_dir(base_dir: Path) -> Path:
    return base_dir / RUN_CONFIGS_DIR


def get_run_configs(base_dir: Path, incomplete: str = "") -> List[Path]:
    run_configs = filter(
        lambda p: p.is_file() and os.access(str(p.absolute()), os.X_OK),
        map(Path, glob(f"{get_rc_dir(base_dir).absolute()}/**/*", recursive=True)),
        # pathlibs glob doesn't support following symlinks prior to python 3.13.
        # See https://github.com/python/cpython/issues/77609#issuecomment-1567306837
    )
    if incomplete != "":
        pairs = map(
            lambda p: (
                p,
                levenshtein_distance(
                    incomplete,
                    str(p.relative_to(base_dir)),
                    weights=(
                        1,
                        LEVENSHTEIN_MAX_DISTANCE,
                        LEVENSHTEIN_MAX_DISTANCE,
                    ),  # only allow insertions
                    score_cutoff=LEVENSHTEIN_MAX_DISTANCE,
                ),
            ),
            run_configs,
        )
        run_configs = map(
            lambda pd: pd[0],
            sorted(
                filter(lambda pd: pd[1] < LEVENSHTEIN_MAX_DISTANCE, pairs),
                key=lambda pd: pd[1],
            ),
        )
    return list(run_configs)


class RunConfigType(click.ParamType):
    name = "run_config"

    def shell_complete(self, ctx, param, incomplete):
        try:
            base_dir = _get_param(ctx, "base_dir")
        except click.UsageError:
            _, exc_value, _ = sys.exc_info()
            logging.warning(exc_value)
            return []
        # return [click.shell_completion.CompletionItem(" ", help=exc_value)]
        return [
            click.shell_completion.CompletionItem(
                str(p.relative_to(get_rc_dir(base_dir))), help=get_help_text(p)
            )
            for p in get_run_configs(base_dir, incomplete)
        ]


def _get_param(ctx: click.Context, param: str) -> click.Parameter:
    if param in ctx.params:
        return ctx.params[param]
    if ctx.default_map is not None and param in ctx.default_map:
        return ctx.default_map[param]
    if (default_param := ctx.lookup_default(param)) is not None:
        return default_param
    for p in ctx.command.params:
        if p.name == param:
            return p.get_default(ctx)
    raise Exception(f"Could not find parameter {param}.")


def list_rc(ctx, _, value) -> None:
    if not value or ctx.resilient_parsing:
        return
    logging.debug("Listing run configs.")
    logging.debug(f"Parameter: {ctx.params}")
    base_dir = _get_param(ctx, "base_dir")
    commands = []
    help_texts = []
    for rc in get_run_configs(base_dir):
        commands.append(str(rc.relative_to(get_rc_dir(base_dir))))
        help_texts.append(get_help_text(rc))
    if not commands:
        logging.warning("No run configs found.")
        ctx.exit(0)
    longest_command = max(len(c) for c in commands)
    for command, help_text in zip(commands, help_texts):
        click.echo(f"{command.ljust(longest_command)}\t{help_text}")
    ctx.exit(0)


def print_zsh_completion(ctx, _, value) -> None:
    if not value or ctx.resilient_parsing:
        return
    logging.debug("Printing zsh completion.")
    logging.debug(f"Parameter: {ctx.params}")
    print('eval "$(_RC_COMPLETE=zsh_source rc)"')
    ctx.exit(0)


def print_base_dir(ctx, _, value) -> None:
    if not value or ctx.resilient_parsing:
        return
    logging.debug("Printing base dir.")
    logging.debug(f"Parameter: {ctx.params}")
    base_dir = _get_param(ctx, "base_dir")
    print(Path(base_dir).absolute())
    ctx.exit(0)


def print_rc_dir(ctx, _, value) -> None:
    if not value or ctx.resilient_parsing:
        return
    logging.debug("Printing run config dir.")
    logging.debug(f"Parameter: {ctx.params}")
    base_dir = _get_param(ctx, "base_dir")
    print(get_rc_dir(base_dir).absolute())
    ctx.exit(0)


def set_log_level(ctx, _, value) -> None:
    if not value or ctx.resilient_parsing:
        return
    logging.basicConfig(
        level=value, format="%(asctime)s │ %(levelname)-8s │ %(message)s"
    )
    logging.debug(f"Setting log level to {value}.")
    return


@click.command(context_settings={"allow_interspersed_args": False})
@click.argument("run_config", type=RunConfigType())
@click.argument("args", nargs=-1)
@click.option(
    "--fork",
    "-f",
    is_flag=True,
    help="Fork process and return immediately. If -s is also supplied the screen session will start detached.",
)
@click.option(
    "--null-pipe",
    "-n",
    is_flag=True,
    help="Use a null pipe instead of a PTY. Is ignored if -s is supplied",
)
@click.option(
    "--screen",
    "-s",
    is_flag=True,
    help="Run in a screen session.",
)
@click.option(
    "--edit",
    "-e",
    is_flag=True,
    help="Edit run config instead of running.",
)
@click.option(
    "--list",
    "-l",
    "list_configs",
    is_flag=True,
    help="List available run configs.",
    callback=list_rc,
    expose_value=False,
    is_eager=True,
)
@click.option(
    "--make-executable",
    "-x",
    is_flag=True,
    help="Make run config executable if it isn't already.",
)
@click.option(
    "--base-dir",
    type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path),
    default=get_base_dir,
    is_eager=True,
    help=(
        "Base directory to run from. Defaults to the first directory containing a .run_configs directory."
        " Should contain a .run_configs directory with executable run configs."
    ),
)
@click.option(
    "--get-base-dir",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    help="Print base directory.",
    callback=print_base_dir,
)
@click.option(
    "--get-rc-dir",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    help="Print run configuration directory.",
    callback=print_rc_dir,
)
@click.option(
    "--zsh-completion",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    help="Print zsh completion script.",
    callback=print_zsh_completion,
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Log level.",
    is_eager=True,
    expose_value=False,
    callback=set_log_level,
)
@click.version_option()
@click.pass_context
def cli(
    ctx: click.Context,
    run_config: str,
    args: Tuple[str],
    base_dir: Path,
    make_executable: bool = False,
    edit: bool = False,
    fork: bool = False,
    null_pipe: bool = False,
    screen: bool = False,
) -> None:
    """Run a run config

    A run config can be any executable file in the .run_configs directory.
    """
    if null_pipe and screen:
        logging.warning("Ignoring null pipe because screen is enabled.")
    if screen and which("screen") is None:
        logging.error("screen not found. Please install screen.")
        ctx.exit(1)
    logging.debug(f"Parameter: {ctx.params}")
    rc_dir = get_rc_dir(base_dir)
    logging.debug(f"Base dir: {base_dir}")
    rc = rc_dir / run_config
    logging.debug(f"Run config: {rc}")
    if edit:
        editor = os.getenv("EDITOR", "vim")
        logging.debug(f"Editor: {editor}")
        logging.info(f"Editing {rc} with {editor}")
        if not rc.exists() and click.confirm(
            "Run config does not exist. Create?", default=True
        ):
            logging.debug(f"Creating {rc}")
            rc.touch()
            logging.debug(f"Making {rc} executable")
            os.chmod(
                str(rc.absolute()), os.stat(str(rc.absolute())).st_mode | stat.S_IEXEC
            )
        if not os.access(str(rc.absolute()), os.X_OK) and click.confirm(
            "Make executable?", default=True
        ):
            logging.debug(f"Making {rc} executable")
            os.chmod(
                str(rc.absolute()), os.stat(str(rc.absolute())).st_mode | stat.S_IEXEC
            )
        logging.debug(f"Opening {rc} with {editor}")
        os.execvp(editor, [editor, str(rc.absolute())])
    if not rc.exists():
        logging.error(f"Run config {run_config} does not exist in {rc_dir}.")
        raise click.UsageError(f"Run config {run_config} does not exist in {rc_dir}.")
    if not os.access(str(rc.absolute()), os.X_OK):
        if make_executable or click.confirm(
            "Run config not executable. Change permissions?", abort=True
        ):
            logging.debug(f"Making {rc} executable")
            os.chmod(
                str(rc.absolute()), os.stat(str(rc.absolute())).st_mode | stat.S_IEXEC
            )
    logging.debug(f"Changing directory to {base_dir}")
    prog_args = list(args) if len(args) > 0 else []
    logging.debug(f"Executing {rc} with args {prog_args}")
    prog = str(rc.absolute())
    prog_args.insert(0, prog)
    if screen:
        prog_args.insert(0, "screen")
        prog_args.insert(1, "-S")
        prog_args.insert(2, f"rc {rc.name}")
        if fork:
            prog_args.insert(3, "-d")
            prog_args.insert(4, "-m")
    logging.debug(f"Executing {prog_args}")

    process_args: dict[str, Any] = dict(cwd=base_dir, env=os.environ)
    if null_pipe and not screen:
        process_args["stdout"] = subprocess.DEVNULL
        process_args["stderr"] = subprocess.DEVNULL
    try:
        proc = subprocess.Popen(
            prog_args, start_new_session=fork and not screen, **process_args
        )
        if not fork:
            proc.wait()
    except OSError as e:
        logging.error(f"Error executing {rc}: {e}")
        raise click.FileError(rc, f"{e}")


if __name__ == "__main__":
    cli()

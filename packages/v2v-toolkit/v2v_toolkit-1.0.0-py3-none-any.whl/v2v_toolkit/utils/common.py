import platform
import subprocess
from multiprocessing import cpu_count
from v2v_toolkit.exceptions import V2VError


def cpu_ct() -> int:
    """Get number of CPUs available.

    Clip the number of CPUs to 1 if it is less than 1.

    Returns:
        int - number of CPUs
    """
    try:
        return max(1, cpu_count())
    except NotImplementedError:
        return 1


def get_current_os() -> str:
    """Get OS info.

    Check the current OS used by the caller.

    Returns:
        str - the current OS

    Raises:
        V2VError - on unknown OS
    """
    if platform.system() == "Darwin":
        return "macos"
    elif platform.system() == "Windows":
        return "windows"
    elif platform.system() == "Linux":
        return "linux"
    raise V2VError(f"Unknown OS: {platform.system()}")


def linux_os() -> bool:
    """Evaluates if the OS is Linux based or not.

    Returns:
        bool - True if Linux, otherwise False
    """
    return (
        platform.platform().find("Linux") != -1
        or platform.platform().find("Darwin") != -1
    )


def git_hash() -> str | None:
    """Get the git hash of the current repository.

    Returns:
        str | None - git hash if available, otherwise None
    """
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


def git_tag() -> str | None:
    """Get the git tag of the current repository.

    Returns:
        str | None - git tag if available, otherwise None
    """
    try:
        return (
            subprocess.check_output(
                ["git", "describe", "--tags"], stderr=subprocess.DEVNULL
            )
            .decode("ascii")
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


def get_current_version() -> str:
    """Produce a version string.

    Returns:
        str - the current version of the system.
    """
    tag = git_tag()
    if tag:
        return tag
    base = f"1.0.0-alpha"
    sha = git_hash()
    if sha:
        return f"{base}-{sha}"
    return base

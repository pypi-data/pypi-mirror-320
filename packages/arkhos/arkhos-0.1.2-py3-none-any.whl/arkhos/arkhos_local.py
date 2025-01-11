import datetime, dbm, os, logging, subprocess, sys
from rich import print
from rich.panel import Panel

logger = logging.getLogger(__name__)

_global = {
    "ARKHOS_GLOBAL_DOMAIN": os.environ.get("ARKHOS_GLOBAL_DOMAIN"),
    "APP_NAME": os.environ.get("APP_NAME", "local-test"),
    "APP_API_KEY": os.environ.get("APP_API_KEY"),
}


def set_up_local():
    project_root_dir = subprocess.getoutput("git rev-parse --show-toplevel")
    arkhos_dir = os.path.join(project_root_dir, ".arkhos")

    # initialize .arkhos folder
    if not os.path.isdir(arkhos_dir):
        os.mkdir(arkhos_dir)

    arkhos_dbm_path = arkhos_dir + "/arkhos"
    _global["dbm"] = dbm.open(arkhos_dbm_path, "c")


def get(key, default_value=None):
    raw_result = _global["dbm"].get(key)
    if not raw_result:
        return default_value

    raw_value, inferred_type = raw_result.decode().split("|arkhos|")
    if inferred_type == "int":
        return int(raw_value)
    elif inferred_type == "float":
        return float(raw_value)
    elif inferred_type == "bool":
        return bool(raw_value)
    elif inferred_type == "datetime":
        return datetime.datetime.fromisoformat(raw_value)
    elif inferred_type == "NoneType":
        return None
    else:  # str
        return raw_value


def set(key, value):
    inferred_type = type(value).__name__
    if inferred_type not in ("str", "int", "float", "bool", "NoneType", "datetime"):
        logger.warn(
            f"Arkhos KeyValue: Value {value} is of type {inferred_type}. Values must be string, int, float, or boolean."
        )
        inferred_type = "str"

    # we use ISO for datetime, sorry about the timezone
    if inferred_type == "datetime":
        value = value.isoformat()

    _global["dbm"][key] = f"{value}|arkhos|{inferred_type}"
    return value


def sms(to_number, message):
    if not sys.stdout.isatty():
        print(f"Arkhos SMS to {to_number}: {message}")
    else:
        print(
            Panel(
                message,
                title=f"[bright_magenta]SMS to [green]{to_number}",
                title_align="left",
                subtitle="[purple]Arkhos",
                subtitle_align="right",
            )
        )


def email(to_email, subject, message):
    app_name = _global["APP_NAME"]
    subject = f"[Arkhos {app_name}] {subject}"
    if not sys.stdout.isatty():
        print(
            f"Arkhos email from {app_name}@arkhoapp.com to {to_email}: {subject} \n\n {message}"
        )
    else:
        message = f"\nSubject:{subject}\n\n{message}\n"
        print(
            Panel(
                message,
                # title=f"[bright_magenta]Email from {app_name}@arkhosapp.com to [green]{to_email}: [blue]{subject}",
                title=f"[bright_magenta]Email from {app_name}@arkhosapp.com to [green]{to_email}",
                title_align="left",
                subtitle="[purple]Arkhos",
                subtitle_align="right",
            )
        )

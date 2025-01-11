import datetime, os
import requests
from requests.auth import HTTPBasicAuth

_global = {
    "ARKHOS_GLOBAL_DOMAIN": os.environ.get("ARKHOS_GLOBAL_DOMAIN"),
    "APP_NAME": os.environ.get("APP_NAME"),
    "APP_API_KEY": os.environ.get("APP_API_KEY"),
}

ARKHOS_KV_URL = f"{_global['ARKHOS_GLOBAL_DOMAIN']}/global/{_global['APP_NAME']}"

ARKHOS_NOTIFY_URL = f"{_global['ARKHOS_GLOBAL_DOMAIN']}/notify/{_global['APP_NAME']}"


def get(key, default_value=None):
    response = requests.get(
        f"{ARKHOS_KV_URL}/{key}/",
        auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"]),
    )

    if response.status_code == 200:
        result = response.json()
        # If the key isn't set, we'll get value:null in the response
        raw_value = result.get("value")
        if not raw_value:
            return default_value

        inferred_type = result.get("inferred_type")
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

    # error_message = "Error connecting to Arkhos Global"
    # if r.json.get("error", False):
    # error_message = r.json.get("error")
    # raise Error(error_message)


def set(key, value):
    raw_value = value
    inferred_type = type(value).__name__
    if inferred_type not in ("str", "int", "float", "bool", "NoneType", "datetime"):
        logger.warn(
            f"Arkhos KeyValue: Value {value} is of type {inferred_type}. Values must be string, int, float, or boolean."
        )
        inferred_type = "str"

    # we use ISO for datetime, sorry about the timezone
    if inferred_type == "datetime":
        value = value.isoformat()

    try:
        value = str(value)
    except (ValueError, TypeError):
        logger.exception(
            f"Arkhos KeyValue: Value {inferred_type}:{value} could be not converted to a string"
        )
        raise TypeError(
            f"Arkhos KeyValue: Value {value} could be not converted to a string"
        )
    response = requests.post(
        f"{ARKHOS_KV_URL}/{key}/",
        json={"value": value, "inferred_type": inferred_type},
        auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"]),
    )
    if response.status_code == 200:
        # return response.json()
        return raw_value


def sms(to_number, message):
    response = requests.post(
        f"{ARKHOS_NOTIFY_URL}/sms",
        auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"]),
        json={"to_number": to_number, "message": message},
    )
    return response.status_code == 200


def email(to_email, subject, message):
    response = requests.post(
        f"{ARKHOS_NOTIFY_URL}/email",
        auth=HTTPBasicAuth(_global["APP_NAME"], _global["APP_API_KEY"]),
        json={
            "to_email": to_email,
            "subject": subject,
            "message": message,
        },
    )
    return response.status_code == 200

from collections import defaultdict
import datetime, logging, os, sys, time

from arkhos import _global
from arkhos.http import HttpResponse, JsonResponse, render, render_static, Request
from arkhos.flask_handler import create_flask_request_handler


def base_handler(event, context=""):
    start_time = time.time()

    request = Request(event)
    response = {}

    try:
        if request.path.startswith("/static/"):
            response = render_static(request.path)
        else:
            user_handler = get_user_handler()
            response = user_handler(request)

        if isinstance(response, (HttpResponse, JsonResponse)):
            response = response.serialize()
        else:
            response = JsonResponse(
                {
                    "error": f"Server Error - arkhos_handler returned an invalid response, returned {type(response).__name__} "
                },
                status=500,
            ).serialize()
    except:
        logging.exception("User handler error")
        response = JsonResponse({"error": "500 Server Error"}, status=500).serialize()

    finally:
        end_time = time.time()
        duration = end_time - start_time
        response["arkhos_duration"] = {
            "started_at": start_time,
            "finished_at": end_time,
            "duration": duration,
        }

    return response


def get_user_handler():
    """This returns the user's handler"""

    # Determine if this is running locally or on lambda
    if __name__ == "__main__":  # this is a python script - ie running in lambda
        pass

    else:  # this is a python module - ie running locally
        sys.path.append(os.getcwd())

    # Determine if the user has an arkhos app or flask app
    if os.path.isfile("main.py"):  # arkhos app
        from main import arkhos_handler

    elif os.path.isfile("app.py"):  # flask app
        from app import app

        arkhos_handler = create_flask_request_handler(app)

    return arkhos_handler

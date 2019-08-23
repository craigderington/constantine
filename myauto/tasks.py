from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger
from requests.auth import HTTPBasicAuth
import random
import requests
import config

# create the celery app
app = Celery(__name__, broker=config.CELERY_BROKER_URL, backend="rpc://")

# logger utility
logger = get_task_logger(__name__)

# setup the periodic tasks
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, log.s(datetime.now().strftime("%c")), name="Log Message Every 10 seconds.")
    sender.add_periodic_task(30.0, get_randoms, name="Get Random Users")
    sender.add_periodic_task(
        crontab(),   # every minute - day_of_week, day_of_month, minute=0, hour="*/3"
        log.s("Today is: {}".format(datetime.now().strftime("%c"))),
    )

# sample task, log message
@app.task(queue="newusers", max_retries=3)
def log(msg):
    logger.info(msg)


@app.task(queue="newusers", max_retries=3)
def get_randoms():
    """ Get a list of random users """
    url = "https://randomuser.me/api/?nat=us&results=5000"
    api_method = "GET"
    hdr = {"content-type": "application/json", "user-agent": "SimplePythonFoo()"}
    user = dict()

    try:
        r = requests.request(api_method, url, headers=hdr)
        if r.status_code == 200:
            resp = r.json()

            for obj in resp["results"]:
                user["title"] = obj["name"]["title"]
                user["fname"] = obj["name"]["first"]
                user["lname"] = obj["name"]["last"]
                user.update()
                show_user.delay(user)
                logger.info("Sending User to Task Queue {} {} {}".format(
                    user["title"], user["fname"], user["lname"]
                ))
        else:
            logger.info("")
    except requests.HTTPError as http_err:
        logger.info("RandomUser website returned HTTP Error: {}".format(str(http_err)))


@app.task(queue="showusers", max_retries=3)
def show_user(user):
    """ Show our new random user """
    GREETINGS = ["Halo", "Hello", "Hallo", "Guten Morgen", "Good Day", "Yo!"]

    if not isinstance(user, dict):
        user = dict(user)

    person = "{} {} {}".format(user["title"], user["fname"], user["lname"])
    logger.info(random.choice(GREETINGS) + " " + person)
    return str(person)

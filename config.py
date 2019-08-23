import os
from kombu import Queue, Exchange

# config settings

DEBUG = False
SECRET_KEY = os.urandom(32)
RANDOM_USER_URL = "https://randomuser.me/api/?nat=us&results=500" 

# celery config
CELERY_TIMEZONE = "US/Eastern"
CELERY_BROKER_URL = "amqp://localhost/"
CELERY_DOCKER_BROKER = "amqp://172.17.0.2/"
CELERY_RESULT_BACKEND = "rpc://"

# tasks queues
CELERY_QUEUES = (        
    Queue("newusers", Exchange("users"), routing_key="users.new"),
    Queue("showusers", Exchange("users"), routing_key="users.show"),       
)

# task routes
CELERY_ROUTES = {        
    "new_users": {"queue": "newusers", "routing_key": "users.new"},
    "show_users": {"queue": "showusers", "routing_key": "users.show"},      
}
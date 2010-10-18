from datetime import timedelta, datetime
from time import time

from celery.task import Task
from celery.registry import tasks

from eventtracker.conf import settings
from eventtracker import models 


def track(event, params):
    """
    Dispatch a track event request into the queue.

    If the Publisher object hasn't been intialized yet, do so. If any error
    occurs during sending of the message, close the Publisher so it will be
    open automatically the next time somedy tracks an event. This will prevent
    a short-term network failure to disable one thread from commucating with
    the queue at the cost of retrying the connection every time.
    """
   
    ProcessEventTask.delay((event, time(), params))


def collect_event(message):
    """
    Collect all events waiting in the queue and store them in the database.
    """
    collection = None
    try:
        collection = models.get_mongo_collection()
        e, t, p = message
        models.save_event(collection, e, t, p)
	print e,": ", datetime.now()

    finally:
        if collection:
            try:
                collection.connection.close()
            except:
                pass

class ProcessEventTask(Task):
    "Celery task that collect event from queue."
    name="eventtrackerrt.tasks.ProcessEventTask"

    def run(self, message):
	collect_event(message=message)
	

tasks.register(ProcessEventTask)


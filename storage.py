#!/usr/bin/python2.7

__author__ = 'michael.g.parker@gmail.com (Michael Parker)'

from google.appengine.api import users
from google.appengine.ext import db


class Task(db.Model):
  """A saved task."""
  creator = db.UserProperty()
  summary = db.StringProperty()
  body = db.TextProperty()
  reminder = db.DateTimeProperty()


def new_task(user, summary, body, reminder=None):
  """Creates a new task.

  Arguments:
    user: The user who is creating the task.
    summary: A summary of the task.
    body: The full description of the task.
    reminder: The date and time to remind the user of the task.
  Returns:
    The unique identifier string of the created task.
  """
  task = Task()
  task.creator = user
  task.summary = summary
  task.body = body
  if reminder is not None:
    task.reminder = reminder
  task.put()
  return str(task.key())


def delete_tasks(user, task_ids):
  """Deletes the tasks with the given identifiers.

  Arguments:
    user: The user who is deleting the tasks.
    task_ids: A list of identifiers of tasks to delete.
  """
  keys = [db.Key(task_id) for task_id in task_ids]
  tasks = db.get(keys)
  # Ensure that the tasks to delete actually belong to the user.
  user_keys = []
  for task in tasks:
    if (task is not None) and (task.creator == user):
      user_keys.append(task.key())
  db.delete(user_keys)


def get_tasks(user):
  """Returns all tasks created by the given user.

  Arguments:
    The user to return tasks for.
  Returns:
    A list of tasks created by the given user.
  """
  query = db.Query(Task)
  query.filter('creator =', user)
  tasks = query.fetch(1000)
  for task in tasks:
    task.id = str(task.key())
  return tasks


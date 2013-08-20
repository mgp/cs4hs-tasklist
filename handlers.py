#!/usr/bin/python2.7

__author__ = 'michael.g.parker@gmail.com (Michael Parker)'

import os

from google.appengine import dist  # pylint: disable-msg=C6203
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util as webapp_util

import tasks

_DEBUG = True

_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates/index.html')


def _write_html(response, template_values={}):
  user = users.GetCurrentUser()
  template_values['user'] = user
  template_values['tasks'] = tasks.get_tasks(user)
  rendered_page = template.render(_TEMPLATE_PATH, template_values)
  response.out.write(rendered_page)


class GetTasksHandler(webapp.RequestHandler):
  """Displays all tasks for the user, and a form to enter a new task."""

  def get(self):
    if users.GetCurrentUser() is None:
      login_url = users.CreateLoginURL(self.request.uri)
      self.redirect(login_url)
    else:
      _write_html(self.response)


class NewTaskHandler(webapp.RequestHandler):
  """Handler that creates a new task."""

  def get(self):
    self.redirect('/')

  def post(self):
    user = users.GetCurrentUser()
    summary = self.request.get('summary', False)
    body = self.request.get('body', False)
    if not summary or not body:
      self.handle_error(summary, body)
      return

    tasks.new_task(user, summary, body)
    self.redirect('/')

  def handle_error(self, summary, body):
    new_task_template_values = {}
    if summary:
      new_task_template_values['summary'] = summary
    if body:
      new_task_template_values['body'] = body
    new_task_template_values['has_error'] = True
    template_values = {
      'new': new_task_template_values,
    }
    _write_html(self.response, template_values)


class DeleteTaskHandler(webapp.RequestHandler):
  """Handler that deletes a given task."""

  def get(self):
    self.redirect('/')

  def post(self):
    user = users.GetCurrentUser()
    task_ids = self.request.get_all('task_id')
    tasks.delete_tasks(user, task_ids)
    self.redirect('/')


def main():
  application = webapp.WSGIApplication([
    ('/', GetTasksHandler),
    ('/new', NewTaskHandler),
    ('/delete', DeleteTaskHandler),
  ], debug=_DEBUG)
  webapp_util.run_wsgi_app(application)

if __name__ == '__main__':
  main()


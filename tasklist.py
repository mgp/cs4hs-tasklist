#!/usr/bin/python2.7

__author__ = 'michael.g.parker@gmail.com (Michael Parker)'

import os

from google.appengine.api import users
import jinja2
import webapp2

import storage


_JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
_TEMPLATE = _JINJA_ENVIRONMENT.get_template('templates/index.html')
_DEBUG = True

def _write_html(response, template_values=None):
  if template_values is None:
    template_values = {}
  template_values.setdefault('new', {})
  user = users.GetCurrentUser()
  template_values['user'] = user
  template_values['tasks'] = storage.get_tasks(user)

  rendered_page = _TEMPLATE.render(template_values)
  response.write(rendered_page)


class GetTasksHandler(webapp2.RequestHandler):
  """Displays all tasks for the user, and a form to enter a new task."""

  def get(self):
    if users.GetCurrentUser() is None:
      login_url = users.CreateLoginURL(self.request.uri)
      self.redirect(login_url)
    else:
      _write_html(self.response)


class NewTaskHandler(webapp2.RequestHandler):
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

    storage.new_task(user, summary, body)
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


class DeleteTaskHandler(webapp2.RequestHandler):
  """Handler that deletes a given task."""

  def get(self):
    self.redirect('/')

  def post(self):
    user = users.GetCurrentUser()
    task_ids = self.request.get_all('task_id')
    storage.delete_tasks(user, task_ids)
    self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', GetTasksHandler),
    ('/new', NewTaskHandler),
    ('/delete', DeleteTaskHandler),
], debug=_DEBUG)


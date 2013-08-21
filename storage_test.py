#!/usr/bin/python2.7

__author__ = 'michael.g.parker@gmail.com (Michael Parker)'

import os
import time

from google3.tasklist import fix_test_imports

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import user_service_stub
from google.appengine.api import users

from google3.tasklist import tasks

from google3.testing.pybase import googletest


class TaskTest(googletest.TestCase):
  """Unit test for the Task model."""

  def setUp(self):
    """Setup for an appengine test."""
    os.environ["TZ"] = "UTC"
    time.tzset()

    os.environ['USER_ID'] = '1111'

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

    # Use stubs for the Prometheus datastore and the users module.
    apiproxy_stub_map.apiproxy.RegisterStub(
        "datastore",
        datastore_file_stub.DatastoreFileStub('cs4hs-tasklist-test', None, None))
    apiproxy_stub_map.apiproxy.RegisterStub(
        "user", user_service_stub.UserServiceStub())

    apiproxy_stub_map.apiproxy.GetStub("datastore").Clear()

    os.environ['APPLICATION_ID'] = 'cs4hs-tasklist-test'

  def assert_task(self, task, creator, summary, body, reminder):
    """Asserts that the Task instance has the given values."""
    self.assertEqual(creator, task.creator)
    self.assertEqual(summary, task.summary)
    self.assertEqual(body, task.body)
    self.assertEqual(reminder, task.reminder)

  def test_create_and_get_tasks(self):
    user = users.User("user@domain.com")

    # Add the first task without a reminder.
    summary1 = "summary1"
    body1 = "body1"
    tasks.new_task(user, summary1, body1)
    user_tasks = tasks.get_tasks(user)
    self.assertEquals(1, len(user_tasks))
    self.assert_task(user_tasks[0], user, summary1, body1, None)

    # Add the second task with a reminder.
    summary2 = "summary2"
    body2 = "body2"
    reminder2 = ""
    tasks.new_task(user, summary2, body2, None)
    user_tasks = tasks.get_tasks(user)
    self.assertEqual(2, len(user_tasks))
    self.assert_task(user_tasks[1], user, summary2, body2, None)

  def test_get_user_tasks(self):
    # Add the task for the first user.
    user1 = users.User("user1@domain1.com")
    summary1 = "summary1"
    body1 = "body1"
    tasks.new_task(user1, summary1, body1)
    # Add the task for the second user.
    user2 = users.User("user2@domain2.com")
    summary2 = "summary2"
    body2 = "body2"
    tasks.new_task(user2, summary2, body2)

    # Assert that the tasks belonging to the users are kept separate.
    user_tasks = tasks.get_tasks(user1)
    self.assertEqual(1, len(user_tasks))
    self.assert_task(user_tasks[0], user1, summary1, body1, None)
    user_tasks = tasks.get_tasks(user2)
    self.assertEqual(1, len(user_tasks))
    self.assert_task(user_tasks[0], user2, summary2, body2, None)

  def test_delete_tasks(self):
    user = users.User("user@domain.com")
    summary = "summary"
    body = "body"
    task_id = tasks.new_task(user, summary, body)
    user_tasks = tasks.get_tasks(user)
    self.assertEqual(1, len(user_tasks))

    tasks.delete_tasks(user, [task_id])
    user_tasks = tasks.get_tasks(user)
    self.assertEqual(0, len(user_tasks))

  def test_delete_other_tasks_fails(self):
    # Add the task for the first user.
    user1 = users.User("user1@domain1.com")
    summary1 = "summary1"
    body1 = "body1"
    task_id1 = tasks.new_task(user1, summary1, body1)
    # Add the task for the second user.
    user2 = users.User("user2@domain2.com")
    summary2 = "summary2"
    body2 = "body2"
    task_id2 = tasks.new_task(user2, summary2, body2)

    # The first user tries to delete the tasks for both users.
    tasks.delete_tasks(user1, [task_id1, task_id2])
    user_tasks = tasks.get_tasks(user1)
    self.assertEqual(0, len(user_tasks))
    # Assert that the tasks for the second user were not deleted.
    user_tasks = tasks.get_tasks(user2)
    self.assertEqual(1, len(user_tasks))
    self.assert_task(user_tasks[0], user2, summary2, body2, None)


if __name__ == '__main__':
  googletest.main()


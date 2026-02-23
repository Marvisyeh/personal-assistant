import os
from todoist_api_python.api import TodoistAPI

class TodoistTool:
  """
  Todoist tool for interacting with Todoist API.
  """
  TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
  TODOIST_PROJECT_KEY = os.getenv("TODOIST_PROJECT_KEY")
  TODOIST_BASE_URL = os.getenv("TODOIST_BASE_URL", "https://api.todoist.com/rest/v2")

  def __init__(self):
    self.todoist = TodoistClient(api_token=self.TODOIST_API_TOKEN)

  def get_tasks(self, project_key: str):
    return self.todoist.get_tasks(project_key)
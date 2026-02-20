import os
from jira import JiraClient, HTTPBasicAuth


class JiraTool:
  """
  Jira tool for interacting with Jira API.
  """
  JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
  PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
  BASE_URL = os.getenv("JIRA_BASE_URL", "https://jira.example.com")

  def __init__(self):
    self.jira = JiraClient(
      url=self.BASE_URL,
      auth=HTTPBasicAuth(self.JIRA_API_TOKEN, self.PROJECT_KEY)
    )

  def get_issues(self, project_key: str):
    return self.jira.get_issues(project_key)

  def create_issue(self, issue: dict):
    return self.jira.create_issue(issue)

  def update_issue(self, issue_key: str, issue: dict):
    return self.jira.update_issue(issue_key, issue)

  def delete_issue(self, issue_key: str):
    return self.jira.delete_issue(issue_key)

  def get_issue(self, issue_key: str):
    return self.jira.get_issue(issue_key)
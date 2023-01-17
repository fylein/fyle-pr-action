import sys
import os
from functools import cached_property

import github
import yaml
import json

import re

"""
This script is used as a github action to check if the PR meets certain criteria.

It will automatically create a comment on the PR with the results of the checks.

It will also assign reviewers based on the files changed in the PR.

To configure this action, you need to create a file called .github/pr_checks_config.yml in your repo.
"""


class PRChecks:

    def __init__(self, config_path, github_token, event_file, event_name, github_url, *kwargs):
        self.config = yaml.load(open(config_path), Loader=yaml.FullLoader)
        self.github = github.Github(base_url=github_url, login_or_token=github_token)
        self.event = json.load(open(event_file))
        self.event_name = event_name
        self.repository = self.github.get_repo(self.event["repository"]["full_name"], lazy=True)

    @cached_property
    def pr(self):
        return self.repository.get_pull(self.event["number"])

    def run(self):
        print("===========DEBUG===============")
        print(self.event)
        print(self.pr)
        print("----------DEBUG----END-----")
        user = self.github.get_user()

        if self.event_name != "pull_request":
            print(f"Event {self.event_name} not supported, this action only supports pull_request events")
            sys.exit(1)

        print(f"Running PR checks for PR #{self.pr.number} ({self.pr.title})")
        self.run_title_checks()
        self.run_description_checks()
        self.run_files_changed_checks()
        success = self.pr.update()
        if success:
            print("PR checked and updated successfully")
            return True
        else:
            print("PR update failed")
            return False

    def run_title_checks(self):
        title = self.pr.title
        for check in self.config["pr_checks"]["title"]:
            if re.match(check["regex"], title):
                self.pr.create_issue_comment(check["message_if_matching"])
            else:
                self.pr.create_issue_comment(check["message_if_not_matching"])

    def run_description_checks(self):
        description = self.pr.body
        for check in self.config["pr_checks"]["description"]:
            if re.match(check["regex"], description):
                self.pr.create_issue_comment(check["message_if_matching"])
            else:
                self.pr.create_issue_comment(check["message_if_not_matching"])

    def run_files_changed_checks(self):
        files_changed = self.pr.get_files()
        for check in self.config["pr_checks"]["file_path"]:
            for file in files_changed:
                if re.match(check["regex"], file.filename):
                    self.pr.create_review_request(check["reviewers"])


if __name__ == "__main__":

    config_path = os.environ.get("INPUT_CONFIG_FILE")
    github_token = os.environ.get("GITHUB_TOKEN")
    github_url = os.environ.get("GITHUB_API_URL")
    event_file = os.environ.get("GITHUB_EVENT_PATH")
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    workspace = os.environ.get("GITHUB_WORKSPACE")

    GITHUB_ENV = os.environ.get("GITHUB_ENV")

    print(os.environ)

    pr_checks = PRChecks(
        config_path=config_path,
        github_token=github_token,
        event_file=event_file,
        event_name=event_name,
        github_url=github_url,
    )
    success = pr_checks.run()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

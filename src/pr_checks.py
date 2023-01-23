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
        self.github = github.Github(base_url=github_url, login_or_token=github_token)
        self.event_name = event_name
        self.event = self.load_event(event_file)
        self.repository = self.load_repository()

        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        try:
            config = yaml.load(self.repository.get_contents(config_path, self.pr.head.sha).decoded_content,
                               Loader=yaml.FullLoader)
        except github.GithubException as e:
            print(f"Configuration file not found at {config_path}: {e}.")
            raise e
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            raise e
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            raise e
        else:
            return config

    @staticmethod
    def load_event(event_file):
        try:
            event = json.load(open(event_file))
        except FileNotFoundError:
            print(f"Event file not found at {event_file}.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading event file: {e}")
            sys.exit(1)
        else:
            return event

    def load_repository(self):
        try:
            repository = self.github.get_repo(self.event["repository"]["full_name"])
        except github.GithubException as e:
            print(f"Github error loading repository: {e}. Check configuration file and repository permissions.")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading repository: {e}")
            sys.exit(1)
        else:
            return repository

    @cached_property
    def pr(self):
        return self.repository.get_pull(self.event["number"])

    def create_comment_conditionally(self, comment):
        if comment:
            self.pr.create_issue_comment(comment)

    def run(self):
        if self.event_name != "pull_request":
            print(f"Event {self.event_name} not supported, this action only supports pull_request events")
            return False
        try:
            self._run_checks()
            self.pr.update()
        except github.GithubException as e:
            print(f"Github API error running checks: {e}. Check your configuration file and repository permissions.")
        except Exception as e:
            print(f"Error running checks: {e}")
            raise e
        else:
            print("PR checks completed successfully")
            return True

    def _run_checks(self):
        print(f"Running PR checks for PR #{self.pr.number} ({self.pr.title})")
        self.run_title_checks()
        self.run_description_checks()
        self.run_files_changed_checks()

    def run_title_checks(self):
        title = self.pr.title
        for check in self.config["pr_checks"].get("title", []):
            if re.match(check["regex"], title):
                self.create_comment_conditionally(check.get("message_if_matching"))
            else:
                self.create_comment_conditionally(check.get("message_if_not_matching"))

    def run_description_checks(self):
        description = self.pr.body or ""  # body can be None, using empty string for regex matching
        for check in self.config["pr_checks"].get("description", []):
            if re.match(check["regex"], description):
                self.create_comment_conditionally(check.get("message_if_matching"))
            else:
                self.create_comment_conditionally(check.get("message_if_not_matching"))

    def run_files_changed_checks(self):
        files_changed = self.pr.get_files()
        reviewers_to_assign = set()
        for check in self.config["pr_checks"].get("file_path", []):
            for file in files_changed:
                if re.match(check["regex"], file.filename):
                    reviewers = check.get("reviewers")
                    reviewers_to_assign.update(reviewers)
        if reviewers_to_assign:
            self.pr.create_review_request(reviewers=list(reviewers_to_assign))


if __name__ == "__main__":

    pr_checks = PRChecks(
        config_path=os.environ.get("INPUT_CONFIG-FILE"),
        github_token=os.environ.get("INPUT_GITHUB-TOKEN"),
        event_file=os.environ.get("GITHUB_EVENT_PATH"),
        event_name=os.environ.get("GITHUB_EVENT_NAME"),
        github_url=os.environ.get("GITHUB_API_URL"),
    )

    success = pr_checks.run()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

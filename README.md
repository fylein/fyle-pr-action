# fyle-pr-action

This action allows you to perform automated checks on your pull requests.

## Usage

This action works best as a separate workflow file.
For example, create a file called `.github/workflows/fyle-pr-action.yml` with the following contents:

```yaml
name: Pull request checks
run-name: PR checks
on:
  pull_request:
    types: [opened, synchronize, edited]
permissions: 
  pull-requests: write
  contents: read
  
jobs:
  pr_checks:
    runs-on: ubuntu-latest
    steps:
      - name: run pr checks
        uses: fylein/fyle-pr-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config-file: .github/pr_checks_config.yaml
```
*Important*: The `github-token` input is required for this action to work. It should be set to `${{ secrets.GITHUB_TOKEN }}`.
This will pass an ephemeral token to the action which will be used to access the pull request.

The config file is optional and defaults to `.github/pr_checks_config.yaml`.

It's also important to run this action only on the `pull_request` event, and to specify the types - otherwise 
the action will not be able to run on editing the pull request.

The action needs `write` permissions to the pull request to create comments, and `read
permissions to contents in order to read the config file, so make sure to specify that in the permissions section.

## Configuration

For the action to work, you need to create a configuration file.
The configuration file is a YAML file that contains the checks that you want to run.
Here's an example configuration file:

```yaml
pr_checks:
  title:
    - name: 'prefix_check'
      regex: '^(fix|feat)'
      message_if_not_matching: 'PR title must start with "fix" or "feat"' # optional
      message_if_matching: 'PR title starts with "fix" or "feat"' # optional - provide at least one of these
    - name: 'issue_check'
      regex: 'JIRA-[0-9]+'
      message_if_not_matching: 'PR title must contain a JIRA issue'
      message_if_matching: 'PR title contains a JIRA issue'

  description:
    - name: 'docs_check'
      regex: 'https://docs\.example\.com' # Matching anywhere in the description
      message_if_not_matching: 'PR description must contain a link to the docs'
      message_if_matching: 'PR description contains a link to the docs'

  file_path:
    - name: 'core_platform'
      regex: '^/core/platform/*' # Regex for matching file path, relative to the root of the repository
      reviewers:
        - 'franciszekzak' # Use GitHub usernames
        - 'example'
    - name: 'core_ui'
      regex: '^/core/ui/*'
      reviewers:
        - 'fyler'
```

Three types of checks are supported: title, description and file path.

### Title checks

Title checks are used to check if the title of the pull request matches a given regex. A comment will be added to the pull request,
depending on whether the regex matches or not. Both the `message_if_not_matching` and `message_if_matching` fields are optional,
but at least one of them must be provided.

### Description checks

Those work exactly the same as title checks, but check the description of the pull request instead.

### File path checks

File path checks are used to check if the pull request contains any files that match a given regex. If there are any matches,
a review request will be sent to the specified reviewers.


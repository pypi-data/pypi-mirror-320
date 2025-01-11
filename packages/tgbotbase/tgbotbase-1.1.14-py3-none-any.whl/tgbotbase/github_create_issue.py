"""
Based on https://github.com/nvtkaszpir/python-github-create-issue/blob/master/github_create_issue.py
"""
#!/usr/bin/env python
import json
import requests
import os

USAGE = """Github create issue.
This script allows to create issue in github for given project.

Usage:

# export env vars
export GITHUB_USER=nvtkaszpir
export GITHUB_PASS=<token>
export REPO_OWNER=nvtkaszpir
export REPO_NAME=vagrant-killingfloorstats

# set title, body and two labels
./create_issue.py --title="Test" --body="Hello And Die" -l bug -l jenkins

Based on https://gist.github.com/JeffPaine/3145490 with tweaks

"""


# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
GITHUB_USER = os.environ.get('GITHUB_USER')
GITHUB_PASS = os.environ.get('GITHUB_PASS')

# The repository to add this issue to
REPO_OWNER = os.environ.get('REPO_OWNER')
REPO_NAME = os.environ.get('REPO_NAME')

# Create an authenticated session to create the issue
session = requests.Session()
session.auth = (GITHUB_USER, GITHUB_PASS)

def check_env_vars():
    """Check env vars"""
    if not GITHUB_USER:
        print ('Missing GITHUB_USER env var')
        return 1
    if not GITHUB_PASS:
        print ('Missing GITHUB_PASS env var')
        return 1
    if not REPO_OWNER:
        print ('Missing REPO_OWNER env var')
        return 1
    if not REPO_NAME:
        print ('Missing REPO_NAME env var')
        return 1

    return 0


def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None, dry=None):
    '''Create an issue on github.com using the given parameters.'''

    if check_env_vars():
        print ('Missing env vars, aborting')
        return 1

    if labels is None:
        labels = []
    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': labels
    }

    if dry:
        print ('Would send to github:')
        print ("REPO_OWNER: %s" % REPO_OWNER)
        print ("REPO_NAME: %s" % REPO_NAME)
        print ("GITHUB_USER: %s" % GITHUB_USER)
        print ("GITHUB_PASS: %s" % "***masked***")
        print ("title: %s" % title)
        print ("body: %s" % body)
        print ("assignee: %s" % assignee)
        print ("milestone: %s" % milestone)
        print ("labels: %s" % labels)
        print ("issue: %s" % issue)
        return 0

    # Our url to create issues via POST
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'

    # Add the issue to our repository
    response = session.post(url, json.dumps(issue))
    if response.status_code == 201:
        print ('Successfully created Issue "%s"' % title)
        resp_obj = response.json()
        print ('Response: ', resp_obj['url'])
        return resp_obj["number"]
    else:
        print ('Could not create Issue "%s"' % title)
        print ('Response: ', response.content)
        return 1

# make_github_issue('Issue Title', 'Body text', 'assigned_user', 3, ['bug'])

def edit_github_issue(issue_id, title=None, body=None, assignee=None, milestone=None, labels=None, dry=None):

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_id}'    
    payload = {
        "title": title, 
        "body": body, 
        "assignee": assignee, 
        "milestone": milestone, 
        "labels": labels
    }

    if dry:
        print ('Would send to github:')
        print ("REPO_OWNER: %s" % REPO_OWNER)
        print ("REPO_NAME: %s" % REPO_NAME)
        print ("GITHUB_USER: %s" % GITHUB_USER)
        print ("GITHUB_PASS: %s" % "***masked***")
        print ("title: %s" % title)
        print ("body: %s" % body)
        print ("assignee: %s" % assignee)
        print ("milestone: %s" % milestone)
        print ("labels: %s" % labels)
        print ("payload: %s" % payload)
        return 0

    response = session.patch(url, json=payload, headers={})

    if response.status_code == 200:
        print ('Successfully edited Issue "%s"' % title)
        resp_obj = response.json()
        print ('Response: ', resp_obj['url'])
        return issue_id
    else:
        print ('Could not edit Issue "%s"' % title)
        print ('Response: ', response.content)
        return 1

def get_issue(issue_id):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_id}'
    response = session.get(url).json()
    return response

if __name__ == '__main__':
    #print(get_issue(1))
    make_github_issue('Issue Title', 'Body text', 'makarworld', labels = ['bug'])

    #parser = argparse.ArgumentParser(description=USAGE, formatter_class=RawTextHelpFormatter)
    #parser.add_argument("-t", "--title", help="github issue title")
    #parser.add_argument("-b", "--body", help="github issue body text")
    #parser.add_argument("-a", "--assignee", help="assignee for github issue (optional)", default=None)
    #parser.add_argument("-m", "--milestone", help="milestone, optional", default=None)
    #parser.add_argument("-l", "--labels", action="append", help="optional labels to assign")
    #parser.add_argument("-d", "--dry", action='store_true', help="do not send to github")
    #args = parser.parse_args()
    #result = make_github_issue(
    #    title=args.title,
    #    body=args.body,
    #    assignee=args.assignee,
    #    milestone=args.milestone,
    #    labels=args.labels
    #    )
    #sys.exit(result)
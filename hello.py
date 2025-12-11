import json
import os
from github import Github
import openai
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
g = Github(GITHUB_TOKEN)
openai.api_key = OPENAI_API_KEY
def lambda_handler(event, context):
    print(":mag: Received event from SNS:", json.dumps(event))
    try:
        sns_message = event['Records'][0]['Sns']['Message']
        payload = json.loads(sns_message)
        print(":package: Parsed GitHub payload:", json.dumps(payload))
        if payload.get("action") not in ["opened", "synchronize", "reopened"]:
            print(":information_source: Ignored action:", payload.get("action"))
            return {"statusCode": 200, "body": "No action taken"}
        repo_name = payload['repository']['full_name']
        pr_number = payload['number']
        print(f":pushpin: Repo: {repo_name}, PR: {pr_number}")
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        for file in files:
            if file.filename in ["requirements.txt", "pyproject.toml", "package.json"]:
                print(f":memo: Reviewing file: {file.filename}")
                patch = file.patch
                if patch:
                    prompt = f"Review `{file.filename}` for vulnerabilities:\n\n{patch}"
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    review = response.choices[0].message.content
                    pr.create_issue_comment(f":closed_lock_with_key: AI Review for `{file.filename}`:\n\n{review}")
                    print(":white_check_mark: Review posted to PR")
        return {"statusCode": 200, "body": "Review complete"}
    except Exception as e:
        print(":x: Error:", str(e))
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


def add:
    return x+y


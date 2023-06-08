import os

from github import Github
from src.review.review import review


def main():
    pat = os.getenv("PERSONAL_ACCESS_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    issue_number = os.getenv("GITHUB_ISSUE_NUMBER")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    github_client = Github(pat)
    repo = github_client.get_repo(repo_name)
    issue = repo.get_issue(number=int(issue_number))

    comments = issue.get_comments()

    prompt = prompt_template.format(
        issue_title=issue.title, comments_section=comments_section
    )

		# Truncate prompt to 4000 characters because 4000 token is the limit.
    prompt = prompt[:4000]
    print(prompt)
    review_text = review(prompt, openai_api_key)

    issue.create_comment(f"\n{review_text}")


if __name__ == "__main__":
    main()
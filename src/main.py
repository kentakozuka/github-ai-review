import os

from github import Github
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
)

CHAR_SOFT_LIMIT = 9000
FILE_SYSTEM_JP = 'あなたは経験豊富なソフトウェア開発者です。"{}"というタイトルのGitHub Pull Requestのレビュアーをしてもらいます。'
FILE_QUESTION_JP = "以下はGitHubのパッチです。主要な変更点をまとめ、潜在的な問題点を特定してください。最も重要な発見から始めてください。\n\n"
SUMMARY_SYSTEM_JP = "ここでは、ソフトウェアのソースコードパッチに関する要約を紹介します。それぞれの要約は、------の行で始まります。個々の要約をすべて考慮した全体的な要約を作成してください。潜在的な問題やエラーを最初に提示し、次に最も重要な発見を要約してください。\n\n{}"


def main():
    pat = os.getenv("PERSONAL_ACCESS_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    issue_number = os.getenv("GITHUB_ISSUE_NUMBER")
    model_name = os.getenv("MODEL_NAME")

    github_client = Github(pat)
    repo = github_client.get_repo(repo_name)
    issue = repo.get_issue(int(issue_number))

    if not issue.pull_request:
        return

    openai.api_key = os.getenv("OPENAI_API_KEY")
    chat = ChatOpenAI(
        temperature=0.5, model_name=model_name or "gpt-3.5-turbo", request_timeout=600
    )
    system = FILE_SYSTEM_JP.format(issue.title)

    # Iterate all patches.
    reviews_summary = ""
    review_details = ""
    files = issue.as_pull_request().get_files()
    for file in files:
        question = FILE_QUESTION_JP + file.patch[:CHAR_SOFT_LIMIT]
        print(question)

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=question),
        ]
        ai_message = chat(messages)
        # For summary.
        if len(reviews_summary) < CHAR_SOFT_LIMIT:
            reviews_summary += "------\n"
            reviews_summary += ai_message.content
            reviews_summary += "\n"
        # For details.
        review_details += "\n---\n\n**{}**\n".format(file.filename)
        review_details += "{}\n".format(ai_message.content)

    # Summarize all patches.
    question = SUMMARY_SYSTEM_JP.format(reviews_summary)
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=question),
    ]
    print(question)

    ai_message = chat(messages)
    resp = ai_message.content
    resp += "\n\n## Details\n\n"
    resp += review_details

    issue.create_comment(resp)


if __name__ == "__main__":
    main()

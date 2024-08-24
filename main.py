import os

from dotenv import load_dotenv
from requests import Request, Session

GITHUB_BASE_URL = "https://api.github.com"


session = Session()


def call_github(token: str, method: str, parts: list[str]):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    path = "/".join(parts)
    req = Request(method, url=f"{GITHUB_BASE_URL}/{path}", headers=headers)

    prepared = session.prepare_request(req)

    resp = session.send(prepared)
    if resp.status_code != 200:
        print(resp)

    return resp.json()


def main():
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("OWNER")
    repository = os.getenv("REPOSITORY")

    workflows = call_github(
        token,
        "GET",
        ["repos", owner, repository, "actions", "runs?status=queued&per_page=100"],
    )
    total_count = workflows["total_count"]
    workflows_to_kill = workflows["workflow_runs"]

    print(f"Total count: {total_count}")

    for workflow in workflows_to_kill:
        run_id = workflow["id"]

        call_github(
            token,
            "POST",
            ["repos", owner, repository, "actions", "runs", str(run_id), "cancel"],
        )


if __name__ == "__main__":
    main()

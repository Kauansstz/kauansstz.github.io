import json
import os
from datetime import datetime, timezone

import requests

USERNAME = "kauansstz"

API_URL = f"https://api.github.com/users/{USERNAME}/repos"

OUTPUT_FILE = "data/repositories.json"


def get_headers():
    token = os.getenv("GITHUB_TOKEN")

    headers = {"Accept": "application/vnd.github+json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_repositories():

    response = requests.get(
        API_URL,
        headers=get_headers(),
        params={"per_page": 100, "sort": "updated"},
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def has_readme(repository_name):

    url = f"https://api.github.com/repos/" f"{USERNAME}/{repository_name}/readme"

    response = requests.get(url, headers=get_headers(), timeout=15)

    return response.status_code == 200


def build_data(repositories):

    result = []

    for index, repository in enumerate(repositories, start=1):

        name = repository["name"]

        result.append(
            {
                "id": index,
                "name": name,
                "language": repository["language"] or "Unknown",
                "description": repository["description"],
                "url": repository["html_url"],
                "readme_url": f"https://github.com/" f"{USERNAME}/{name}#readme",
                "has_readme": has_readme(name),
                "stars": repository["stargazers_count"],
                "forks": repository["forks_count"],
                "updated_at": repository["updated_at"],
            }
        )

    return result


def save_data(repositories):

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    data = {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repositories": repositories,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(data, file, indent=4, ensure_ascii=False)


def main():

    print("Fetching repositories...")

    repositories = get_repositories()

    print(f"{len(repositories)} repositories found.")

    data = build_data(repositories)

    save_data(data)

    print("repositories.json updated successfully.")


if __name__ == "__main__":
    main()

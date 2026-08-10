import json
import os

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

    print("Fetching repositories...")

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print()
        print("[WARN] GITHUB_TOKEN não encontrado.")
        print("[WARN] Usando GitHub API sem autenticação.")
        print()

    response = requests.get(
        API_URL,
        headers=get_headers(),
        params={"per_page": 100, "sort": "updated"},
        timeout=15,
    )

    if response.status_code == 403:

        raise RuntimeError("GitHub API rate limit exceeded. " "Configure GITHUB_TOKEN.")

    response.raise_for_status()

    return response.json()


def has_readme(repository_name):

    url = f"https://api.github.com/repos/" f"{USERNAME}/{repository_name}/readme"

    response = requests.get(url, headers=get_headers(), timeout=15)

    return response.status_code == 200


def build_repositories(repositories):

    result = []

    for index, repository in enumerate(repositories, start=1):

        name = repository["name"]

        print(f"Checking README: {name}")

        readme_exists = has_readme(name)

        result.append(
            {
                "id": index,
                "name": name,
                "language": repository["language"] or "Unknown",
                "description": repository["description"] or "No description available.",
                "url": repository["html_url"],
                "readme_url": (
                    f"https://github.com/" f"{USERNAME}/" f"{name}" f"#readme"
                ),
                "has_readme": readme_exists,
                "stars": repository["stargazers_count"],
                "forks": repository["forks_count"],
                "updated_at": repository["updated_at"],
            }
        )

    return result


def save_repositories(repositories):

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(repositories, file, indent=4, ensure_ascii=False)


def main():

    repositories = get_repositories()

    print(f"{len(repositories)} repositories found.")

    repositories = build_repositories(repositories)

    save_repositories(repositories)

    print()
    print("repositories.json updated successfully.")


if __name__ == "__main__":
    main()

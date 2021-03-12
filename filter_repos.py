import os
import json
import requests
import subprocess


def get_top_repos(page = 1):
    public_repos = requests.get('https://api.github.com/search/repositories?page=' + str(page) + '&q=language:C&sort=stars&order=desc').json()['items']
    repo_details = {}
    for repo in public_repos:
        repo_name = repo['name']
        repo_link = repo['url']
        # repo_stars = repo['stargazers_count']
        # print(repo_name, repo_link, repo_stars)
        repo_details[repo_name] = repo_link

    return repo_details


def clone_repos(filename="repos.json", repoStartIndex=0, repoEndIndex=9):
    with open(filename, "r") as f:
        repo_list = json.load(f)
        repoCount = 0

        for repo_name, repo_link in repo_list.items():
            if repoCount < repoStartIndex:
                repoCount += 1
                continue
            if repoCount > repoEndIndex:
                break

            in_path = os.path.join("Dataset", repo_name)
            p = subprocess.Popen("git clone --depth=1 --progress -v " + repo_link + ' ' + in_path, stdout=subprocess.PIPE)
            p.wait()

            repoCount += 1


if __name__ == '__main__':
    # print(get_top_repos(2))
    clone_repos("repos.json", repoStartIndex=10, repoEndIndex=19)
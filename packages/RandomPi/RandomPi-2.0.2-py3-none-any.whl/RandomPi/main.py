import requests
import random
from bs4 import BeautifulSoup


def get_random_pi():
    url = "https://pypi.org/simple/"
    headers = {"Accept": "application/vnd.pypi.simple.v1+html"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        projects = response.text

        soup = BeautifulSoup(projects, "html.parser")
        project_links = soup.find_all("a")
        project_names = [link.text for link in project_links]

        if project_names:
            random_project = random.choice(project_names)
            print(f"pypi.org/project/{random_project}/")
        else:
            print("No projects found.")
    else:
        print("Failed to fetch projects:", response.status_code, response.text)


def get_random_info():
    url1 = "https://pypi.org/simple/"
    headers1 = {"Accept": "application/vnd.pypi.simple.v1+html"}

    response1 = requests.get(url1, headers=headers1)

    if response1.status_code == 200:
        projects = response1.text

        soup = BeautifulSoup(projects, "html.parser")
        project_links = soup.find_all("a")
        project_names = [link.text for link in project_links]
        project = random.choice(project_names)

    url = f"https://pypi.org/pypi/{project}/json"
    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code == 200:

        data = response.json()

        project_name = data.get("info", {}).get("name", "Unknown")
        version = data.get("info", {}).get("version", "Unknown")
        author = data.get("info", {}).get("author", "Unknown")
        summary = data.get("info", {}).get("summary", "No summary available")

        print(f"Project Name: {project_name}")
        print(f"URL: pypi.org/project/{project_name}/")
        print(f"Latest Version: {version}")
        print(f"Author: {author}")
        print(f"Summary: {summary}")
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")


def get_project_info():
    project = input("Project Name:\n")

    url = f"https://pypi.org/pypi/{project}/json"
    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code == 200:

        data = response.json()

        project_name = data.get("info", {}).get("name", "Unknown")
        version = data.get("info", {}).get("version", "Unknown")
        author = data.get("info", {}).get("author", "Unknown")
        summary = data.get("info", {}).get("summary", "No summary available")

        print(f"Project Name: {project_name}")
        print(f"URL: pypi.org/project/{project_name}/")
        print(f"Latest Version: {version}")
        print(f"Author: {author}")
        print(f"Summary: {summary}")
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
import requests

def fetch_maven_artifact_details(query):
    url = f"https://search.maven.org/solrsearch/select?q={query}&rows=10&wt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for doc in data['response']['docs']:
            # print(doc)
            print(f"GroupId: {doc['g']}")
            print(f"ArtifactId: {doc['a']}")
            print(f"Version: {doc['latestVersion']}")
            print("---")
    else:
        print("Failed to fetch data")
def fetch_most_popular_artifact(query):
    url = f"https://search.maven.org/solrsearch/select?q={query}&rows=20&wt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Sort documents by the number of extension components
        artifacts = sorted(
            data['response']['docs'],
            key=lambda x: len(x['ec']),  # Sorting by the number of extensions
            reverse=True
        )
        if artifacts:
            most_popular = artifacts[0]  # Get the artifact with the most extensions
            print("Most Popular Artifact:")
            print(f"GroupId: {most_popular['g']}")
            print(f"ArtifactId: {most_popular['a']}")
            print(f"Latest Version: {most_popular['latestVersion']}")
            print(f"Extensions Count: {len(most_popular['ec'])}")
            print("Extensions:", ", ".join(most_popular['ec']))
            print("---")
        else:
            print("No artifacts found")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    # Replace 'junit' with your search term
    # fetch_maven_artifact_details('junit')
    fetch_most_popular_artifact('gson')
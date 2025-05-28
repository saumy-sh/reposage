import requests
import streamlit as st


GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

def get_issue_data(owner, repo, issue_number):
    """
    Fetch issue data from GitHub using GraphQL API.
    Returns issue data or None if failed.
    """
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN not found in environment variables")
        return None
    
    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          title
          body
          number
          url
          state
          author {
            login
          }
          createdAt
          updatedAt
        }
      }
    }
    """
    
    variables = {
        "owner": owner,
        "repo": repo,
        "issueNumber": int(issue_number),
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            GITHUB_API_URL, 
            json={"query": query, "variables": variables}, 
            headers=headers,
            timeout=30
        )
        
        # Print response for debugging
        print(f"GitHub API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"GitHub API Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            print("GraphQL Errors:")
            for error in data["errors"]:
                print(f"  - {error.get('message', 'Unknown error')}")
            return None
        
        # Check if data exists
        if "data" not in data:
            print("No 'data' field in response")
            print(f"Full response: {data}")
            return None
        
        # Check if repository exists
        if not data["data"]["repository"]:
            print(f"Repository {owner}/{repo} not found or not accessible")
            return None
        
        # Check if issue exists
        if not data["data"]["repository"]["issue"]:
            print(f"Issue #{issue_number} not found in {owner}/{repo}")
            return None
        
        return data["data"]["repository"]["issue"]
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def test_github_token():
    """Test if GitHub token is valid."""
    if not GITHUB_TOKEN:
        return False, "GitHub token not found in environment"
    
    query = """
    query {
      viewer {
        login
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    
    try:
        response = requests.post(
            GITHUB_API_URL,
            json={"query": query},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "viewer" in data["data"]:
                username = data["data"]["viewer"]["login"]
                return True, f"Token valid for user: {username}"
            else:
                return False, "Invalid token response"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Error testing token: {e}"

import re

def parse_github_url(url):
    """
    Given a URL like:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    return ('owner', 'repo')
    """
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(\.git)?/?$", url)
    if match:
        return match.group(1), match.group(2)
    return None, None


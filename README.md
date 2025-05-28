# RepoSage - GitHub Issue Helper with Repository Analysis

An intelligent tool that helps resolve GitHub issues by analyzing the complete repository codebase using Perplexity's Sonar API.

## Features

- Fetch GitHub issues using GraphQL API
- Crawl and analyze entire repository codebases
- AI-powered issue analysis with repository context
- Smart file filtering and prioritization
- Repository statistics and insights
- Automatic cleanup of temporary files

## Setup Instructions

### 1. Install Dependencies

bash
pip install -r requirements.txt


### 2. Environment Configuration

Create a .env file in the project root with your API keys:

```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
GITHUB_TOKEN=your_github_token_here
```



*Getting API Keys:*

- *Perplexity API Key*: Sign up at [Perplexity AI](https://www.perplexity.ai/) and get your API key
- *GitHub Token*: Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token (classic). Select repo scope for public repositories.

### 3. Run the Application
Go to the webpage url link below 
```bash

```

## Usage

1. *Enter Repository URL*: Provide a public GitHub repository URL (e.g., https://github.com/owner/repo)
2. *Specify Issue Number*: Enter the issue number you want to analyze
3. *Configure Advanced Options* (optional):
   - Branch name (default: main)
   - Maximum files to analyze (default: 20)
   - File extensions to crawl (default: .py,.js,.java,.ts,.go,.cpp,.c,.rb,.php)
4. *Click "Crawl Repository & Analyze Issue"*: The tool will:
   - Fetch the issue details from GitHub
   - Download and analyze the repository codebase
   - Send the context to Perplexity Sonar for intelligent analysis
   - Provide detailed solutions and recommendations

## Project Structure

```bash
├── main.py                 # Main Streamlit application
├── github_api.py          # GitHub GraphQL API integration
├── sonar_api.py           # Perplexity Sonar API integration (enhanced)
├── repo_crawler.py        # Repository crawling and analysis
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── README.md             # This file
```

## File Descriptions

- *main.py*: Enhanced Streamlit interface with repository crawling integration
- *repo_crawler.py*: NEW - Handles repository downloading, extraction, and code analysis
- *sonar_api.py*: Enhanced with repository context support for better issue analysis
- *github_api.py*: GitHub GraphQL API client (unchanged)
- *utils.py*: URL parsing utilities (unchanged)

## Features in Detail

### Repository Crawling
- Downloads repositories as ZIP files
- Extracts and processes multiple file types
- Smart filtering to skip irrelevant directories (node_modules, .git, etc.)
- File prioritization (main files, configs get higher priority)
- Handles large files by truncating content appropriately

### AI Analysis
- Sends issue details along with relevant codebase context
- Smart context construction to stay within API limits
- Relevance scoring to prioritize most important files
- Detailed analysis including root cause, solutions, and implementation steps

### Safety Features
- Automatic cleanup of temporary files
- Error handling for network issues and API limits
- Rate limiting awareness
- File size and content limits to prevent abuse

## Important Notes

*API Limits*: Both Perplexity and GitHub APIs have usage limits. Use responsibly.

*Security*: Keep your API keys secure. Never commit the .env file to version control.

*Cleanup*: Use the "Clean Temporary Files" button to remove downloaded repositories and free up disk space.

## Future Enhancements

- **Knowledge Graph-based Code Indexing**: Implement a semantic indexing system to represent code relationships and dependencies for more precise context generation.
- **Local Repo Crawler**: Develop a local crawler that deeply analyzes repositories and builds a structured knowledge base for enhanced reasoning.
- **Multi-turn Conversation Support**: Enable persistent, contextual dialogue with the Perplexity API to simulate ongoing developer-assistant interactions across sessions.
- **Related Issue Mining**: Automatically analyze related issues and their discussions to provide richer context and reference past resolutions.
- **Improved UI/UX**: Enhance the Streamlit interface with features like code highlighting, response history, and inline citation previews.


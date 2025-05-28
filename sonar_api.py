from openai import OpenAI
import os
from typing import List, Dict
import streamlit as st
API_KEY = st.secrets["PERPLEXITY_API_KEY"]

client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

def ask_sonar(issue_title: str, issue_body: str) -> str:
    """Original function for simple issue analysis without repository context."""
    system_msg = {
        "role": "system",
        "content": "You are a helpful AI assistant analyzing GitHub issues and providing solutions.",
    }
    user_msg = {
        "role": "user",
        "content": f"Issue Title: {issue_title}\n\nIssue Description: {issue_body}\n\nWhat might be causing this issue and how can it be resolved?",
    }

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[system_msg, user_msg],
    )
    return response.choices[0].message.content

def ask_sonar_with_context(issue_title: str, issue_body: str, code_chunks: List[Dict[str, str]]) -> str:
    """Enhanced function that includes repository context for better issue analysis."""
    
    # Construct context from code chunks
    context_text = construct_code_context(code_chunks)
    
    system_msg = {
        "role": "system",
        "content": """You are an expert software engineer and debugging assistant. You have been given access to a GitHub repository's codebase along with a specific issue that needs to be resolved.

Your task is to:
1. Analyze the issue in the context of the provided codebase
2. Identify the root cause of the problem
3. Suggest specific code changes or solutions
4. Provide step-by-step instructions for implementing the fix
5. Consider potential side effects and edge cases

Be specific and reference actual files and code sections when possible. If you need more information to provide a complete solution, mention what additional details would be helpful."""
    }
    
    user_msg = {
        "role": "user",
        "content": f"""I need help resolving this GitHub issue:

**Issue Title:** {issue_title}

**Issue Description:**
{issue_body or 'No description provided.'}

**Repository Context:**
{context_text}

Please analyze this issue in the context of the codebase and provide:
1. Root cause analysis
2. Specific solution with code examples
3. Implementation steps
4. Potential risks or considerations
"""
    }

    try:
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[system_msg, user_msg],
            max_tokens=4000,  # Allow for detailed responses
        )
        print(response)
        return response
    except Exception as e:
        return f"Error getting response from Sonar API: {str(e)}"

def construct_code_context(code_chunks: List[Dict[str, str]], max_context_length: int = 15000) -> str:
    """Construct a context string from code chunks, prioritizing important files."""
    
    if not code_chunks:
        return "No code files were found in the repository."
    
    context_parts = []
    current_length = 0
    
    # Add repository summary
    file_count = len(code_chunks)
    file_types = {}
    for chunk in code_chunks:
        ext = os.path.splitext(chunk['filename'])[1]
        file_types[ext] = file_types.get(ext, 0) + 1
    
    summary = f"Repository contains {file_count} files of types: {', '.join(file_types.keys())}\n\n"
    context_parts.append(summary)
    current_length += len(summary)
    
    # Add code files with smart truncation
    for i, chunk in enumerate(code_chunks):
        if current_length > max_context_length:
            context_parts.append(f"\n... [Additional {len(code_chunks) - i} files omitted due to length constraints]")
            break
        
        file_header = f"=== FILE: {chunk['filename']} ===\n"
        file_content = chunk['content']
        
        # Estimate space needed
        estimated_length = len(file_header) + len(file_content) + 100  # buffer
        
        if current_length + estimated_length > max_context_length:
            # Truncate this file's content
            available_space = max_context_length - current_length - len(file_header) - 100
            if available_space > 200:  # Only include if we have reasonable space
                truncated_content = file_content[:available_space] + "\n... [File truncated]"
                context_parts.append(file_header + truncated_content + "\n\n")
            break
        else:
            context_parts.append(file_header + file_content + "\n\n")
            current_length += estimated_length
    
    return "".join(context_parts)

def analyze_issue_relevance(issue_title: str, issue_body: str, code_chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Score and sort code chunks by relevance to the issue (simple keyword matching)."""
    issue_text = (issue_title + " " + (issue_body or "")).lower()
    
    # Extract keywords from issue
    keywords = set()
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cannot', 'not', 'no', 'yes', 'this', 'that', 'these', 'those', 'a', 'an'}
    
    for word in issue_text.split():
        clean_word = ''.join(c for c in word if c.isalnum()).lower()
        if len(clean_word) > 2 and clean_word not in common_words:
            keywords.add(clean_word)
    
    # Score each code chunk
    scored_chunks = []
    for chunk in code_chunks:
        score = 0
        content_lower = chunk['content'].lower()
        filename_lower = chunk['filename'].lower()
        
        for keyword in keywords:
            # Higher weight for filename matches
            score += filename_lower.count(keyword) * 3
            # Regular weight for content matches
            score += content_lower.count(keyword)
        
        scored_chunks.append({
            **chunk,
            'relevance_score': score
        })
    
    # Sort by relevance score (descending) and return
    return sorted(scored_chunks, key=lambda x: x['relevance_score'], reverse=True)

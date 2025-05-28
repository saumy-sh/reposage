import streamlit as st
from github_api import get_issue_data
from sonar_api import ask_sonar_with_context
from utils import parse_github_url
from repo_crawler import crawl_and_analyze_repo
import os

st.set_page_config(page_title="GitHub Issue Helper", layout="wide")
st.title("🧠 GitHub Issue Helper with Repository Analysis- RepoSage")

st.markdown("""
This tool fetches GitHub issues and analyzes them with the complete repository context using Perplexity Sonar API.
""")

repo_url = st.text_input("Enter public GitHub repository URL (e.g., https://github.com/owner/repo):")
issue_number = st.text_input("Enter issue number (e.g., 42):")

# Advanced options
with st.expander("Advanced Options"):
    branch = st.text_input("Branch name (default: main)", value="main")
    max_files = st.number_input("Maximum files to analyze", min_value=1, max_value=50, value=20)
    file_extensions = st.text_input("File extensions to crawl (comma-separated)", value=".py,.js,.java,.ts,.go,.cpp,.c,.rb,.php")

if repo_url and issue_number:
    owner, repo = parse_github_url(repo_url)
    if not owner:
        st.error("Invalid GitHub URL format.")
    else:
        # Convert file extensions string to tuple
        allowed_exts = tuple(ext.strip() for ext in file_extensions.split(','))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Issue Information")
            with st.spinner("Fetching issue from GitHub..."):
                issue = get_issue_data(owner, repo, issue_number)

            if issue:
                st.success("✅ Issue fetched successfully")
                st.markdown(f"**Issue #{issue['number']}:** {issue['title']}")
                st.markdown(f"[View on GitHub]({issue['url']})")
                
                with st.expander("Issue Description"):
                    st.markdown(issue['body'] or "No description provided.")
            else:
                st.error("❌ Issue not found or GitHub API error.")
        
        with col2:
            st.subheader("🔍 Repository Analysis")
            if issue and st.button("🚀 Crawl Repository & Analyze Issue", type="primary"):
                with st.spinner("Crawling repository and extracting code..."):
                    try:
                        # Crawl repository
                        code_chunks = crawl_and_analyze_repo(
                            owner, repo, branch, allowed_exts, max_files
                        )
                        
                        if code_chunks:
                            st.success(f"✅ Extracted {len(code_chunks)} code files")
                            
                            # Show some stats
                            total_lines = sum(chunk['content'].count('\n') for chunk in code_chunks)
                            st.info(f"📊 Total lines of code analyzed: {total_lines}")
                            
                            # Show file list
                            with st.expander("📁 Files Analyzed"):
                                for chunk in code_chunks[:10]:  # Show first 10
                                    st.code(chunk['filename'], language="text")
                                if len(code_chunks) > 10:
                                    st.write(f"... and {len(code_chunks) - 10} more files")
                        else:
                            st.warning("⚠️ No code files found in the repository")
                            code_chunks = []
                        
                    except Exception as e:
                        st.error(f"❌ Error crawling repository: {str(e)}")
                        code_chunks = []
                
                # Analyze with Sonar
                if 'code_chunks' in locals():
                    st.subheader("🤖 AI Analysis")
                    with st.spinner("Analyzing issue with repository context..."):
                        try:
                            # Get the full response object instead of just content
                            response_obj = ask_sonar_with_context(
                                issue['title'], 
                                issue['body'], 
                                code_chunks
                            )
                            
                            # Check if response_obj is a string (old format) or response object (new format)
                            if isinstance(response_obj, str):
                                # Old format - just the content
                                response_content = response_obj
                                citations = []
                            else:
                                # New format - extract content and citations
                                if hasattr(response_obj, 'choices') and len(response_obj.choices) > 0:
                                    response_content = response_obj.choices[0].message.content
                                    # Extract citations from the response object
                                    citations = getattr(response_obj, 'citations', [])
                                else:
                                    response_content = str(response_obj)
                                    citations = []
                            
                            st.success("✅ Analysis complete")
                            st.markdown("### 🎯 Sonar's Detailed Analysis")
                            st.markdown(response_content)
                            
                            # Display citations if available
                            if citations:
                                st.markdown("---")
                                st.markdown("### 📚 Sources & Citations")
                                st.markdown("*The analysis above was informed by the following sources:*")
                                
                                for i, citation in enumerate(citations, 1):
                                    # Create clickable links for citations
                                    st.markdown(f"{i}. [{citation}]({citation})")
                            
                        except Exception as e:
                            st.error(f"❌ Error analyzing with Sonar: {str(e)}")

# Cleanup section
if st.button("🧹 Clean Temporary Files"):
    try:
        import shutil
        if os.path.exists("./repos"):
            shutil.rmtree("./repos")
        if os.path.exists("temp_downloads"):
            shutil.rmtree("temp_downloads")
        st.success("✅ Temporary files cleaned")
    except Exception as e:
        st.error(f"❌ Error cleaning files: {str(e)}")

st.markdown("---")
st.markdown("💡 **Tip:** This tool works best with repositories that have clear documentation and well-structured code.")

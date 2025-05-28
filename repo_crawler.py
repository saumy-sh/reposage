import requests
import zipfile
import os
import shutil
from typing import List, Dict, Tuple

def crawl_and_analyze_repo(owner: str, repo: str, branch: str = "main", 
                          allowed_exts: Tuple[str, ...] = (".py", ".js", ".java", ".ts", ".go"),
                          max_files: int = 20) -> List[Dict[str, str]]:
    """
    Download and analyze a GitHub repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch to download (default: main)
        allowed_exts: Tuple of allowed file extensions
        max_files: Maximum number of files to process
    
    Returns:
        List of dictionaries containing filename and content
    """
    # Create directories
    temp_dir = "temp_downloads"
    repos_dir = "./repos"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(repos_dir, exist_ok=True)
    
    try:
        # Download repository
        zip_path = download_repo(owner, repo, branch, temp_dir)
        
        # Extract repository
        extract_path = extract_repo(zip_path, repo, repos_dir)
        
        # Extract code chunks
        code_chunks = extract_code_files(extract_path, allowed_exts, max_files)
        
        return code_chunks
        
    except Exception as e:
        raise Exception(f"Failed to crawl repository: {str(e)}")
    
    finally:
        # Cleanup temporary files
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except:
            pass

def download_repo(owner: str, repo: str, branch: str, temp_dir: str) -> str:
    """Download repository as ZIP file."""
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        # Try 'master' branch if 'main' fails
        if branch == "main":
            url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
            response = requests.get(url, timeout=30)
            
        if response.status_code != 200:
            raise Exception(f"Could not download repository. HTTP {response.status_code}")
    
    zip_path = os.path.join(temp_dir, f"{repo}.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)
    
    return zip_path

def extract_repo(zip_path: str, repo: str, repos_dir: str) -> str:
    """Extract repository ZIP file."""
    extract_path = os.path.join(repos_dir, repo)
    
    # Remove existing directory if it exists
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    return extract_path

def extract_code_files(extract_path: str, allowed_exts: Tuple[str, ...], max_files: int) -> List[Dict[str, str]]:
    """Extract and process code files from the repository."""
    code_chunks = []
    files_processed = 0
    
    # Skip common directories that usually don't contain relevant code
    skip_dirs = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
        'build', 'dist', 'target', '.pytest_cache', '.mypy_cache',
        'coverage', '.coverage', 'htmlcov', '.tox', '.nox'
    }
    
    for root, dirs, files in os.walk(extract_path):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
        
        # Prioritize certain files (like main files, configs, etc.)
        priority_files = []
        regular_files = []
        
        for fname in files:
            if fname.endswith(allowed_exts):
                if any(keyword in fname.lower() for keyword in ['main', 'index', 'app', 'server', 'config']):
                    priority_files.append(fname)
                else:
                    regular_files.append(fname)
        
        # Process priority files first
        for fname in priority_files + regular_files:
            if files_processed >= max_files:
                break
                
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, extract_path)
            
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Skip very large files or empty files
                    if len(content) > 10000:  # Truncate very large files
                        content = content[:10000] + "\n\n... [File truncated due to size]"
                    elif len(content.strip()) == 0:
                        continue
                    
                    code_chunks.append({
                        "filename": rel_path,
                        "content": content,
                        "size": len(content),
                        "lines": content.count('\n') + 1
                    })
                    
                    files_processed += 1
                    
            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                # Skip files that can't be read
                continue
        
        if files_processed >= max_files:
            break
    
    # Sort by importance (main files first, then by size)
    def sort_key(chunk):
        filename = chunk['filename'].lower()
        # Give higher priority to important files
        if any(keyword in filename for keyword in ['main', 'index', 'app', 'server']):
            return (0, -chunk['size'])
        elif any(keyword in filename for keyword in ['config', 'setting', 'const']):
            return (1, -chunk['size'])
        else:
            return (2, -chunk['size'])
    
    code_chunks.sort(key=sort_key)
    
    return code_chunks

def get_repo_summary(code_chunks: List[Dict[str, str]]) -> Dict[str, any]:
    """Generate a summary of the repository."""
    if not code_chunks:
        return {}
    
    # File type analysis
    file_types = {}
    total_lines = 0
    total_size = 0
    
    for chunk in code_chunks:
        ext = os.path.splitext(chunk['filename'])[1]
        file_types[ext] = file_types.get(ext, 0) + 1
        total_lines += chunk['lines']
        total_size += chunk['size']
    
    return {
        'total_files': len(code_chunks),
        'total_lines': total_lines,
        'total_size': total_size,
        'file_types': file_types,
        'main_language': max(file_types.items(), key=lambda x: x[1])[0] if file_types else None
    }

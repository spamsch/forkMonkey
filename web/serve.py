#!/usr/bin/env python3
"""
Extended HTTP server for ForkMonkey web interface
Handles API requests for fork data
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json
import threading
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

# Add parent directory to path to allow importing src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import PyGithub, but don't fail if not present
try:
    from github import Github, GithubException
    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False
    print("Warning: PyGithub not installed. Community features will be limited.")

PORT = 8000

# Cache for fork data to avoid hitting rate limits
# Structure: { 'repo_name': { 'data': ..., 'timestamp': ... } }
FORK_CACHE = {}
CACHE_DURATION = timedelta(minutes=15)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Parse URL
        parsed_url = urlparse(self.path)
        
        # Handle API endpoints
        if parsed_url.path == '/api/forks':
            self.handle_forks_request()
            return
            
        # Default behavior (serve files)
        super().do_GET()

    def handle_forks_request(self):
        """Handle request for all monkey forks"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if not HAS_GITHUB:
            response = {"error": "GitHub integration unavailable", "forks": []}
            self.wfile.write(json.dumps(response).encode())
            return

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            # Fallback for local testing without token - return dummy data
            response = {
                "warning": "No GITHUB_TOKEN set",
                "forks": self._get_dummy_forks()
            }
            self.wfile.write(json.dumps(response).encode())
            return

        try:
            # Fetch real data (threaded/cached)
            forks_data = self._fetch_forks_data(token)
            response = {"forks": forks_data}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling forks request: {e}")
            response = {"error": str(e), "forks": []}
            self.wfile.write(json.dumps(response).encode())

    def _get_dummy_forks(self):
        """Return dummy data for testing without API access"""
        return [
            {
                "owner": "test-user",
                "repo": "forkMonkey-test",
                "url": "#",
                "monkey_stats": {
                    "generation": 5, 
                    "rarity_score": 85.5,
                    "age_days": 12,
                    "traits": {
                        "Mood": {"value": "Super Happy", "rarity": "Legendary"}
                    }
                },
                "monkey_svg":  None # Client will handle missing SVG
            }
        ]

    def _fetch_forks_data(self, token):
        """Fetch data from GitHub with caching"""
        global FORK_CACHE
        
        # Check cache validity
        now = datetime.now()
        cache_key = "all_forks"
        
        if cache_key in FORK_CACHE:
            cached = FORK_CACHE[cache_key]
            if now - cached['timestamp'] < CACHE_DURATION:
                print("Using cached fork data")
                return cached['data']
        
        # Determine root repo
        g = Github(token)
        repo_name = os.getenv("GITHUB_REPOSITORY")
        
        if not repo_name:
            # If running locally and not set, try to guess or use default
            # This is a bit tricky locally, let's assume we want to see forks of THIS repo
            # or if we are a fork, the parent's forks.
            # providing a reasonable default for testing:
            repo_name = "forkZoo/forkMonkey" 

        try:
            repo = g.get_repo(repo_name)
            
            # If we are a fork, find the parent to get siblings
            if repo.fork and repo.parent:
                root_repo = repo.parent
            else:
                root_repo = repo
                
            print(f"Fetching forks for {root_repo.full_name}...")
            forks = root_repo.get_forks()
            
            results = []
            
            # Add root repo itself
            root_data = self._fetch_single_repo_data(root_repo)
            if root_data:
                root_data['is_root'] = True
                results.append(root_data)
            
            # Add forks (limit to 15 most recent to avoid timeouts)
            count = 0
            for fork in forks.get_page(0): # Process first page only for speed
                if count >= 15: break
                
                # Skip if it's the root (already added)
                if fork.full_name == root_repo.full_name: continue
                
                data = self._fetch_single_repo_data(fork)
                if data:
                    results.append(data)
                    count += 1
            
            # Update cache
            FORK_CACHE[cache_key] = {
                'data': results,
                'timestamp': now
            }
            
            return results
            
        except Exception as e:
            print(f"Error fetching from GitHub: {e}")
            return []

    def _fetch_single_repo_data(self, repo):
        """Fetch monkey data from a single repo"""
        try:
            # Try to get stats.json
            try:
                stats_content = repo.get_contents("monkey_data/stats.json")
                stats = json.loads(stats_content.decoded_content.decode())
            except:
                return None # No stats means probably not initialized or not a proper forkMonkey
            
            # Try to get SVG
            try:
                svg_content = repo.get_contents("monkey_data/monkey.svg")
                svg = svg_content.decoded_content.decode()
            except:
                svg = None
                
            return {
                "owner": repo.owner.login,
                "repo": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "monkey_stats": stats,
                "monkey_svg": svg,
                "last_updated": repo.updated_at.isoformat()
            }
            
        except Exception as e:
            print(f"Error processing {repo.full_name}: {e}")
            return None

def main():
    # Change to project root directory (parent of web/)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"Serving from: {project_root}")
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"""
╔═══════════════════════════════════════════╗
║     🐵 ForkMonkey Web Interface 🐵       ║
║        Community Edition v2.0           ║
╚═══════════════════════════════════════════╝

Server running at: http://localhost:{PORT}

PRO_TIP: Set GITHUB_TOKEN environment variable 
         to see real community forks!

Press Ctrl+C to stop the server
        """)
        
        # Open browser to web/index.html
        # Check if running in a container or headless env to avoid errors, 
        # but for this user (Mac) it's fine.
        try:
            webbrowser.open(f'http://localhost:{PORT}/web/index.html')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()

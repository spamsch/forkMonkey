#!/usr/bin/env python3
"""
ForkMonkey Community Scanner

Scans all forks of the repository to aggregate monkey data.
Generates web/community_data.json for the static web app.
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from github import Github, GithubException

def scan_community():
    print("🌍 Starting ForkMonkey Community Scan...")
    
    # Initialize GitHub
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️  No GITHUB_TOKEN found. API limits will be strict.")
    
    g = Github(token)
    
    # Determine repo to scan
    repo_name = os.getenv("GITHUB_REPOSITORY")
    if not repo_name:
        print("⚠️  GITHUB_REPOSITORY not set. Using default 'forkZoo/forkMonkey'")
        repo_name = "forkZoo/forkMonkey"
        
    try:
        repo = g.get_repo(repo_name)
        
        # If we are a fork, scan the parent's forks instead
        if repo.fork and repo.parent:
            print(f"🍴 Detected fork of {repo.parent.full_name}. Scanning parent's network...")
            target_repo = repo.parent
        else:
            target_repo = repo
            
        print(f"📡 Scanning forks of {target_repo.full_name}...")
        
        forks = target_repo.get_forks()
        community_data = {
            "last_updated": datetime.now().isoformat(),
            "source_repo": target_repo.full_name,
            "forks": []
        }
        
        # List of repos to scan: [root] + [forks]
        repos_to_scan = [target_repo]
        
        # Get up to 50 most recent forks
        for fork in forks.get_page(0):
            repos_to_scan.append(fork)
        for fork in forks.get_page(1): # Get another page just in case
            if len(repos_to_scan) >= 50: break
            repos_to_scan.append(fork)
            
        print(f"🎯 Found {len(repos_to_scan)} potential habitats.")
        
        for r in repos_to_scan:
            try:
                # Calculate simple age from creation if stats missing
                age = (datetime.now() - r.created_at).days
                
                monkey_data = {
                    "owner": r.owner.login,
                    "repo": r.name,
                    "url": r.html_url,
                    "is_root": r.full_name == target_repo.full_name,
                    "monkey_stats": None,
                    "monkey_svg": None
                }
                
                # Fetch stats.json
                try:
                    contents = r.get_contents("monkey_data/stats.json")
                    stats = json.loads(contents.decoded_content.decode())
                    monkey_data["monkey_stats"] = stats
                except:
                    # Skip if no stats (probably not initialized)
                    pass
                
                # Fetch monkey.svg
                try:
                    contents = r.get_contents("monkey_data/monkey.svg")
                    svg = contents.decoded_content.decode()
                    monkey_data["monkey_svg"] = svg
                except:
                    pass
                
                # Only add if we found at least stats or SVG
                if monkey_data["monkey_stats"] or monkey_data["monkey_svg"]:
                    # Ensure basic stats if missing
                    if not monkey_data["monkey_stats"]:
                        monkey_data["monkey_stats"] = {
                            "generation": "?",
                            "rarity_score": 0,
                            "age_days": age
                        }
                        
                    community_data["forks"].append(monkey_data)
                    print(f"✅ Found monkey in {r.full_name}")
                else:
                    # print(f"⚪ Empty habitat: {r.full_name}")
                    pass
                    
            except Exception as e:
                print(f"❌ Error scanning {r.full_name}: {e}")
                
        # Save to file
        output_file = Path("web/community_data.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(community_data, f, indent=2)
            
        print(f"\n✨ Scan complete! Discovered {len(community_data['forks'])} monkeys.")
        print(f"💾 Saved to {output_file}")
        
    except Exception as e:
        print(f"🔥 Critical error during scan: {e}")
        exit(1)

if __name__ == "__main__":
    scan_community()

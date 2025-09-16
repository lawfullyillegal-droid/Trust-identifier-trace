#!/usr/bin/env python3
"""
GitHub Analytics Data Collector for Trust Identifier Trace Repository
Collects learning analytics and repository statistics for dashboard visualization.
"""

import json
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import os

class GitHubAnalytics:
    def __init__(self, owner="lawfullyillegal-droid", repo="Trust-identifier-trace"):
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        # Set up date ranges for this month (September 2025)
        self.current_month = datetime.now(timezone.utc)
        self.month_start = self.current_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.month_end = self.current_month
        
        # Previous month for comparison
        if self.month_start.month == 1:
            self.prev_month_start = self.month_start.replace(year=self.month_start.year-1, month=12)
        else:
            self.prev_month_start = self.month_start.replace(month=self.month_start.month-1)
        
        self.prev_month_end = self.month_start - timedelta(seconds=1)

    def make_request(self, endpoint, params=None):
        """Make GitHub API request with error handling"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ API request failed: {response.status_code} - {endpoint}")
                return None
        except requests.RequestException as e:
            print(f"⚠️ Network error for {endpoint}: {e}")
            return None

    def get_commits_data(self):
        """Fetch commit data for analytics"""
        print("📊 Collecting commit analytics...")
        
        # Get commits for current month
        current_commits = self.make_request("commits", {
            "since": self.month_start.isoformat(),
            "until": self.month_end.isoformat(),
            "per_page": 100
        })
        
        # Get commits for previous month  
        prev_commits = self.make_request("commits", {
            "since": self.prev_month_start.isoformat(),
            "until": self.prev_month_end.isoformat(),
            "per_page": 100
        })
        
        # Process commit data
        current_month_stats = self.process_commits(current_commits or [])
        prev_month_stats = self.process_commits(prev_commits or [])
        
        return {
            "current_month": current_month_stats,
            "previous_month": prev_month_stats,
            "month_over_month_change": self.calculate_change(
                current_month_stats["total_commits"], 
                prev_month_stats["total_commits"]
            )
        }

    def process_commits(self, commits):
        """Process commit data for analytics"""
        if not commits:
            return {
                "total_commits": 0,
                "unique_contributors": 0,
                "daily_activity": {},
                "contributor_activity": {},
                "commit_times": {},
                "average_commits_per_day": 0
            }
        
        daily_activity = defaultdict(int)
        contributor_activity = defaultdict(int)
        commit_times = defaultdict(int)
        contributors = set()
        
        for commit in commits:
            # Extract date and contributor info
            commit_date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00"))
            date_key = commit_date.strftime("%Y-%m-%d")
            hour_key = commit_date.strftime("%H:00")
            
            author = commit.get("author", {})
            contributor = author.get("login", "unknown") if author else "unknown"
            
            # Count daily activity
            daily_activity[date_key] += 1
            
            # Count contributor activity
            contributor_activity[contributor] += 1
            contributors.add(contributor)
            
            # Count commit times
            commit_times[hour_key] += 1
        
        # Calculate averages
        days_in_period = len(daily_activity) if daily_activity else 1
        avg_commits_per_day = len(commits) / days_in_period
        
        return {
            "total_commits": len(commits),
            "unique_contributors": len(contributors),
            "daily_activity": dict(daily_activity),
            "contributor_activity": dict(contributor_activity),
            "commit_times": dict(commit_times),
            "average_commits_per_day": round(avg_commits_per_day, 2)
        }

    def get_pulls_data(self):
        """Fetch pull request data for analytics"""
        print("📊 Collecting pull request analytics...")
        
        # Get all PRs (we'll filter by date)
        all_pulls = self.make_request("pulls", {"state": "all", "per_page": 100})
        
        if not all_pulls:
            return self.empty_pulls_stats()
        
        current_month_prs = []
        prev_month_prs = []
        
        for pr in all_pulls:
            created_date = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            
            if self.month_start <= created_date <= self.month_end:
                current_month_prs.append(pr)
            elif self.prev_month_start <= created_date <= self.prev_month_end:
                prev_month_prs.append(pr)
        
        return {
            "current_month": self.process_pulls(current_month_prs),
            "previous_month": self.process_pulls(prev_month_prs),
        }

    def process_pulls(self, pulls):
        """Process pull request data"""
        if not pulls:
            return self.empty_pulls_stats()["current_month"]
        
        total_prs = len(pulls)
        open_prs = len([pr for pr in pulls if pr["state"] == "open"])
        closed_prs = len([pr for pr in pulls if pr["state"] == "closed"])
        merged_prs = len([pr for pr in pulls if pr.get("merged_at")])
        draft_prs = len([pr for pr in pulls if pr.get("draft", False)])
        
        # Calculate average time to close/merge (for closed PRs)
        closed_pr_times = []
        for pr in pulls:
            if pr["state"] == "closed" and pr.get("closed_at"):
                created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                closed = datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00"))
                time_diff = (closed - created).total_seconds() / 3600  # hours
                closed_pr_times.append(time_diff)
        
        avg_time_to_close = round(sum(closed_pr_times) / len(closed_pr_times), 2) if closed_pr_times else 0
        
        return {
            "total_prs": total_prs,
            "open_prs": open_prs,
            "closed_prs": closed_prs,
            "merged_prs": merged_prs,
            "draft_prs": draft_prs,
            "merge_rate": round((merged_prs / closed_prs * 100), 2) if closed_prs > 0 else 0,
            "average_time_to_close_hours": avg_time_to_close
        }

    def empty_pulls_stats(self):
        """Return empty PR stats structure"""
        empty_stats = {
            "total_prs": 0,
            "open_prs": 0,
            "closed_prs": 0,
            "merged_prs": 0,
            "draft_prs": 0,
            "merge_rate": 0,
            "average_time_to_close_hours": 0
        }
        return {
            "current_month": empty_stats,
            "previous_month": empty_stats
        }

    def get_issues_data(self):
        """Fetch issues data for analytics"""
        print("📊 Collecting issues analytics...")
        
        # Get all issues
        all_issues = self.make_request("issues", {"state": "all", "per_page": 100})
        
        if not all_issues:
            return {"current_month": {"total_issues": 0, "open_issues": 0, "closed_issues": 0}}
        
        # Filter out PRs (GitHub API includes PRs in issues)
        issues_only = [issue for issue in all_issues if "pull_request" not in issue]
        
        current_month_issues = []
        for issue in issues_only:
            created_date = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            if self.month_start <= created_date <= self.month_end:
                current_month_issues.append(issue)
        
        total_issues = len(current_month_issues)
        open_issues = len([issue for issue in current_month_issues if issue["state"] == "open"])
        closed_issues = len([issue for issue in current_month_issues if issue["state"] == "closed"])
        
        return {
            "current_month": {
                "total_issues": total_issues,
                "open_issues": open_issues,
                "closed_issues": closed_issues
            }
        }

    def get_repository_stats(self):
        """Get overall repository statistics"""
        print("📊 Collecting repository statistics...")
        
        repo_data = self.make_request("")
        
        if not repo_data:
            return {"error": "Could not fetch repository data"}
        
        return {
            "name": repo_data.get("name", ""),
            "description": repo_data.get("description", ""),
            "language": repo_data.get("language", ""),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "watchers": repo_data.get("watchers_count", 0),
            "open_issues": repo_data.get("open_issues_count", 0),
            "size": repo_data.get("size", 0),
            "created_at": repo_data.get("created_at", ""),
            "updated_at": repo_data.get("updated_at", ""),
            "has_pages": repo_data.get("has_pages", False),
            "has_wiki": repo_data.get("has_wiki", False)
        }

    def get_learning_metrics(self):
        """Calculate learning and development metrics"""
        print("📊 Calculating learning metrics...")
        
        # These metrics help understand development patterns and learning
        commits_data = self.get_commits_data()
        pulls_data = self.get_pulls_data()
        
        current_commits = commits_data["current_month"]
        current_pulls = pulls_data["current_month"]
        
        # Learning indicators
        collaboration_score = len(current_commits["contributor_activity"]) * 10  # More contributors = better collaboration
        activity_consistency = len(current_commits["daily_activity"])  # Days with activity
        
        # Development velocity
        development_velocity = current_commits["total_commits"] + current_pulls["total_prs"]
        
        # Quality indicators
        pr_to_commit_ratio = (current_pulls["total_prs"] / current_commits["total_commits"]) if current_commits["total_commits"] > 0 else 0
        merge_success_rate = current_pulls["merge_rate"]
        
        return {
            "collaboration_score": collaboration_score,
            "activity_consistency_days": activity_consistency,
            "development_velocity": development_velocity,
            "pr_to_commit_ratio": round(pr_to_commit_ratio, 2),
            "merge_success_rate": merge_success_rate,
            "learning_trend": "increasing" if commits_data["month_over_month_change"] > 0 else "stable"
        }

    def calculate_change(self, current, previous):
        """Calculate percentage change between current and previous values"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 2)

    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        print("🚀 Generating GitHub Analytics Report...")
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {
                "current_month": {
                    "start": self.month_start.isoformat(),
                    "end": self.month_end.isoformat(),
                    "name": self.month_start.strftime("%B %Y")
                },
                "previous_month": {
                    "start": self.prev_month_start.isoformat(),
                    "end": self.prev_month_end.isoformat(),
                    "name": self.prev_month_start.strftime("%B %Y")
                }
            },
            "repository": self.get_repository_stats(),
            "commits": self.get_commits_data(),
            "pull_requests": self.get_pulls_data(),
            "issues": self.get_issues_data(),
            "learning_metrics": self.get_learning_metrics()
        }
        
        return report

    def save_analytics_data(self, output_dir="output"):
        """Save analytics data to JSON file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        report = self.generate_analytics_report()
        
        # Save main analytics file
        analytics_file = output_path / "github_analytics.json"
        with open(analytics_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Save timestamped backup
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = output_path / f"github_analytics_{timestamp}.json"
        with open(backup_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Analytics saved to {analytics_file}")
        print(f"✅ Backup saved to {backup_file}")
        
        return report

def main():
    """Main execution function"""
    analytics = GitHubAnalytics()
    report = analytics.save_analytics_data()
    
    # Print summary
    print("\n📈 GitHub Analytics Summary:")
    print(f"Repository: {report['repository']['name']}")
    print(f"Period: {report['period']['current_month']['name']}")
    print(f"Total Commits: {report['commits']['current_month']['total_commits']}")
    print(f"Pull Requests: {report['pull_requests']['current_month']['total_prs']}")
    print(f"Contributors: {report['commits']['current_month']['unique_contributors']}")
    print(f"Learning Trend: {report['learning_metrics']['learning_trend']}")
    print(f"Development Velocity: {report['learning_metrics']['development_velocity']}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script to identify all failing codes in the Trust-identifier-trace repository.
This script systematically tests all Python files and identifies failing patterns.
"""

import os
import sys
import subprocess
import json
import traceback
from datetime import datetime
from pathlib import Path

# Define output paths
FAILING_CODES_REPORT = Path(__file__).parent / "failing_codes_report.json"
FAILING_CODES_LOG = Path(__file__).parent / "failing_codes_log.txt"

class FailingCodesFinder:
    def __init__(self):
        self.failures = []
        self.successes = []
        self.start_time = datetime.now()
        
    def log(self, message):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(FAILING_CODES_LOG, "a") as f:
            f.write(log_entry + "\n")
    
    def test_python_file(self, filepath):
        """Test a Python file for syntax and runtime errors"""
        file_name = os.path.basename(filepath)
        self.log(f"Testing {file_name}...")
        
        # Test 1: Syntax check
        try:
            result = subprocess.run([
                sys.executable, "-m", "py_compile", filepath
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.failures.append({
                    "file": file_name,
                    "type": "syntax_error",
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                })
                self.log(f"  ❌ SYNTAX ERROR in {file_name}")
                return False
        except Exception as e:
            self.failures.append({
                "file": file_name,
                "type": "compilation_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.log(f"  ❌ COMPILATION ERROR in {file_name}: {e}")
            return False
        
        # Test 2: Import test
        try:
            module_name = file_name[:-3]  # Remove .py extension
            result = subprocess.run([
                sys.executable, "-c", f"import {module_name}; print('Import successful')"
            ], capture_output=True, text=True, timeout=10, cwd=os.path.dirname(filepath))
            
            if result.returncode != 0:
                self.failures.append({
                    "file": file_name,
                    "type": "import_error",
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                })
                self.log(f"  ❌ IMPORT ERROR in {file_name}")
                return False
        except Exception as e:
            self.failures.append({
                "file": file_name,
                "type": "import_test_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
        
        # Test 3: Runtime execution test
        try:
            result = subprocess.run([
                sys.executable, filepath
            ], capture_output=True, text=True, timeout=30, cwd=os.path.dirname(filepath))
            
            if result.returncode != 0:
                self.failures.append({
                    "file": file_name,
                    "type": "runtime_error",
                    "error": result.stderr,
                    "stdout": result.stdout,
                    "exit_code": result.returncode,
                    "timestamp": datetime.now().isoformat()
                })
                self.log(f"  ❌ RUNTIME ERROR in {file_name} (exit code: {result.returncode})")
                return False
            else:
                self.successes.append({
                    "file": file_name,
                    "type": "successful_execution",
                    "stdout": result.stdout,
                    "timestamp": datetime.now().isoformat()
                })
                self.log(f"  ✅ SUCCESS: {file_name}")
                return True
                
        except subprocess.TimeoutExpired:
            self.failures.append({
                "file": file_name,
                "type": "timeout_error",
                "error": "Script execution timed out after 30 seconds",
                "timestamp": datetime.now().isoformat()
            })
            self.log(f"  ⏰ TIMEOUT ERROR in {file_name}")
            return False
        except Exception as e:
            self.failures.append({
                "file": file_name,
                "type": "execution_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self.log(f"  ❌ EXECUTION ERROR in {file_name}: {e}")
            return False
    
    def analyze_specific_failures(self):
        """Analyze specific failure patterns in the repository"""
        self.log("\n🔍 Analyzing specific failure patterns...")
        
        # Analyze network-dependent failures
        network_failures = []
        for failure in self.failures:
            if any(keyword in failure.get("error", "").lower() for keyword in 
                   ["nameresolutionerror", "connectionerror", "failed to resolve"]):
                network_failures.append(failure["file"])
        
        if network_failures:
            self.log(f"  📡 Network connectivity failures: {', '.join(network_failures)}")
        
        # Analyze missing file/key failures
        missing_data_failures = []
        for failure in self.failures:
            if any(keyword in failure.get("error", "").lower() for keyword in 
                   ["keyerror", "filenotfounderror", "no such file"]):
                missing_data_failures.append(failure["file"])
        
        if missing_data_failures:
            self.log(f"  📁 Missing data failures: {', '.join(missing_data_failures)}")
        
        # Analyze import failures
        import_failures = []
        for failure in self.failures:
            if failure.get("type") == "import_error":
                import_failures.append(failure["file"])
        
        if import_failures:
            self.log(f"  📦 Import failures: {', '.join(import_failures)}")
    
    def run_analysis(self):
        """Run the complete failing codes analysis"""
        self.log("🚀 Starting comprehensive failing codes analysis...")
        
        # Clear previous log
        if FAILING_CODES_LOG.exists():
            FAILING_CODES_LOG.unlink()
        
        # Find all Python files
        python_files = []
        repo_root = Path(__file__).parent
        for py_file in repo_root.glob("*.py"):
            if py_file.name != "find_failing_codes.py":  # Don't test this script itself
                python_files.append(py_file)
        
        self.log(f"Found {len(python_files)} Python files to test")
        
        # Test each Python file
        for py_file in python_files:
            self.test_python_file(str(py_file))
        
        # Analyze failure patterns
        self.analyze_specific_failures()
        
        # Generate summary
        self.generate_summary()
        
        # Save detailed report
        self.save_report()
    
    def generate_summary(self):
        """Generate a summary of the analysis"""
        total_files = len(self.failures) + len(self.successes)
        failure_count = len(self.failures)
        success_count = len(self.successes)
        
        self.log(f"\n📊 ANALYSIS SUMMARY:")
        self.log(f"  Total files tested: {total_files}")
        self.log(f"  Successful executions: {success_count}")
        self.log(f"  Failed executions: {failure_count}")
        self.log(f"  Success rate: {(success_count/total_files*100):.1f}%" if total_files > 0 else "  Success rate: N/A")
        
        if self.failures:
            self.log(f"\n❌ FAILING CODES:")
            for failure in self.failures:
                self.log(f"  - {failure['file']}: {failure['type']}")
        
        if self.successes:
            self.log(f"\n✅ SUCCESSFUL CODES:")
            for success in self.successes:
                self.log(f"  - {success['file']}")
    
    def save_report(self):
        """Save detailed report to JSON file"""
        report = {
            "analysis_timestamp": self.start_time.isoformat(),
            "total_files_tested": len(self.failures) + len(self.successes),
            "failures_count": len(self.failures),
            "successes_count": len(self.successes),
            "failures": self.failures,
            "successes": self.successes,
            "summary": {
                "network_dependent_failures": [f["file"] for f in self.failures 
                                              if any(kw in f.get("error", "").lower() 
                                                    for kw in ["nameresolutionerror", "connectionerror"])],
                "missing_data_failures": [f["file"] for f in self.failures 
                                         if any(kw in f.get("error", "").lower() 
                                               for kw in ["keyerror", "filenotfounderror"])],
                "import_failures": [f["file"] for f in self.failures if f.get("type") == "import_error"]
            }
        }
        
        with open(FAILING_CODES_REPORT, "w") as f:
            json.dump(report, f, indent=2)
        
        self.log(f"\n📄 Detailed report saved to: {FAILING_CODES_REPORT}")
        self.log(f"📄 Log file saved to: {FAILING_CODES_LOG}")

if __name__ == "__main__":
    finder = FailingCodesFinder()
    finder.run_analysis()
#!/usr/bin/env python3
"""
Bolt Health Check Utility
Monitors the health of the Bolt framework and its components
"""

import os
import sys
import yaml
import json
import argparse
import logging
import psutil
import platform
import socket
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bolt_health.log")
    ]
)

logger = logging.getLogger("bolt-health")

class BoltHealthCheck:
    def __init__(self, config_path: str = "bolt/config.yaml"):
        """Initialize the health check utility."""
        self.config_path = config_path
        self.config = self._load_config()
        self.start_time = datetime.now()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def check_file_system(self) -> Dict[str, Any]:
        """Check file system health."""
        results = {
            "status": "healthy",
            "issues": []
        }
        
        # Check experiments directory
        experiments_dir = self.config.get("general", {}).get("experiments_dir", "bolt/experiments")
        if not os.path.exists(experiments_dir):
            results["status"] = "warning"
            results["issues"].append(f"Experiments directory not found: {experiments_dir}")
        
        # Check results directory
        results_dir = self.config.get("general", {}).get("results_dir", "bolt/results")
        if not os.path.exists(results_dir):
            try:
                os.makedirs(results_dir)
                results["issues"].append(f"Created missing results directory: {results_dir}")
            except Exception as e:
                results["status"] = "error"
                results["issues"].append(f"Cannot create results directory: {results_dir}, error: {e}")
        
        # Check disk space
        try:
            disk_usage = psutil.disk_usage(os.path.dirname(experiments_dir))
            results["disk"] = {
                "total_gb": disk_usage.total / (1024**3),
                "used_gb": disk_usage.used / (1024**3),
                "free_gb": disk_usage.free / (1024**3),
                "percent_used": disk_usage.percent
            }
            
            if disk_usage.percent > 90:
                results["status"] = "warning"
                results["issues"].append(f"Disk space low: {disk_usage.percent}% used")
        except Exception as e:
            results["status"] = "error"
            results["issues"].append(f"Error checking disk space: {e}")
        
        return results
    
    def check_experiment_files(self) -> Dict[str, Any]:
        """Check experiment files for issues."""
        results = {
            "status": "healthy",
            "issues": [],
            "experiments": []
        }
        
        experiments_dir = self.config.get("general", {}).get("experiments_dir", "bolt/experiments")
        if not os.path.exists(experiments_dir):
            results["status"] = "error"
            results["issues"].append(f"Experiments directory not found: {experiments_dir}")
            return results
        
        # Check all TOML files
        for filename in os.listdir(experiments_dir):
            if not filename.endswith('.toml'):
                continue
            
            filepath = os.path.join(experiments_dir, filename)
            try:
                with open(filepath, "rb") as f:
                    import tomli
                    exp_config = tomli.load(f)
                
                exp_info = {
                    "name": exp_config.get("name", "Unnamed"),
                    "file": filename,
                    "status": "valid"
                }
                
                # Check for required fields
                missing_fields = []
                for field in ["name", "steps"]:
                    if field not in exp_config:
                        missing_fields.append(field)
                
                if missing_fields:
                    exp_info["status"] = "invalid"
                    exp_info["issues"] = f"Missing required fields: {', '.join(missing_fields)}"
                    results["status"] = "warning"
                    results["issues"].append(f"Invalid experiment file: {filename}")
                
                results["experiments"].append(exp_info)
                
            except Exception as e:
                results["status"] = "warning"
                results["issues"].append(f"Error parsing experiment file {filename}: {e}")
                results["experiments"].append({
                    "name": filename,
                    "file": filename,
                    "status": "error",
                    "issues": str(e)
                })
        
        # Count experiments
        valid_count = sum(1 for exp in results["experiments"] if exp["status"] == "valid")
        results["count"] = {
            "total": len(results["experiments"]),
            "valid": valid_count,
            "invalid": len(results["experiments"]) - valid_count
        }
        
        return results
    
    def check_recent_results(self) -> Dict[str, Any]:
        """Check recently completed experiments."""
        results = {
            "status": "healthy",
            "issues": [],
            "recent_results": []
        }
        
        results_dir = self.config.get("general", {}).get("results_dir", "bolt/results")
        if not os.path.exists(results_dir):
            results["status"] = "warning"
            results["issues"].append(f"Results directory not found: {results_dir}")
            return results
        
        # Get last modified time for each file
        results_files = []
        for filename in os.listdir(results_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(results_dir, filename)
            try:
                mtime = os.path.getmtime(filepath)
                results_files.append((filepath, mtime))
            except Exception:
                continue
        
        # Sort by modification time (newest first)
        results_files.sort(key=lambda x: x[1], reverse=True)
        
        # Check most recent files
        for filepath, mtime in results_files[:5]:  # Check 5 most recent
            try:
                with open(filepath, "r") as f:
                    result_data = json.load(f)
                
                experiment_name = result_data.get("experiment_name", "Unknown")
                success = result_data.get("success", False)
                execution_time = result_data.get("execution_time", "")
                
                result_info = {
                    "name": experiment_name,
                    "file": os.path.basename(filepath),
                    "success": success,
                    "execution_time": execution_time,
                    "steps_completed": len(result_data.get("steps", []))
                }
                
                results["recent_results"].append(result_info)
                
                if not success:
                    # Look for errors in steps
                    error_steps = [step for step in result_data.get("steps", []) 
                                   if step.get("status") == "error"]
                    
                    if error_steps:
                        first_error = error_steps[0]
                        result_info["error"] = first_error.get("error", "Unknown error")
                
            except Exception as e:
                results["status"] = "warning"
                results["issues"].append(f"Error parsing result file {os.path.basename(filepath)}: {e}")
        
        # Check success rate of recent experiments
        if results["recent_results"]:
            success_count = sum(1 for r in results["recent_results"] if r.get("success", False))
            success_rate = success_count / len(results["recent_results"])
            
            results["success_rate"] = success_rate
            
            if success_rate < 0.5:
                results["status"] = "warning"
                results["issues"].append(f"Low success rate: {success_rate:.2%}")
        
        return results
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        results = {
            "status": "healthy",
            "issues": []
        }
        
        # Check CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            results["cpu"] = {
                "percent": cpu_percent,
                "cores": psutil.cpu_count()
            }
            
            if cpu_percent > 90:
                results["status"] = "warning"
                results["issues"].append(f"High CPU usage: {cpu_percent}%")
        except Exception as e:
            results["issues"].append(f"Error checking CPU: {e}")
        
        # Check memory usage
        try:
            mem = psutil.virtual_memory()
            results["memory"] = {
                "total_gb": mem.total / (1024**3),
                "available_gb": mem.available / (1024**3),
                "used_gb": mem.used / (1024**3),
                "percent_used": mem.percent
            }
            
            if mem.percent > 90:
                results["status"] = "warning"
                results["issues"].append(f"High memory usage: {mem.percent}%")
        except Exception as e:
            results["issues"].append(f"Error checking memory: {e}")
        
        # Get system information
        results["system"] = {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "hostname": socket.gethostname()
        }
        
        return results
    
    def check_daemon_status(self) -> Dict[str, Any]:
        """Check the status of the Bolt daemon."""
        results = {
            "status": "unknown",
            "issues": []
        }
        
        # Check if daemon is enabled in config
        daemon_enabled = self.config.get("daemon", {}).get("enabled", False)
        if not daemon_enabled:
            results["status"] = "disabled"
            return results
        
        # On Linux, we could check for process
        try:
            daemon_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and 'bolt/agents/daemon.py' in ' '.join(cmdline):
                        daemon_running = True
                        results["pid"] = proc.info.get('pid')
                        results["uptime"] = time.time() - proc.create_time()
                        results["status"] = "running"
                        break
                except Exception:
                    continue
            
            if not daemon_running:
                results["status"] = "not_running"
                results["issues"].append("Daemon is enabled but not running")
        except Exception as e:
            results["issues"].append(f"Error checking daemon process: {e}")
        
        return results
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and compile a report."""
        logger.info("Running Bolt health checks...")
        
        # Run all checks
        file_system = self.check_file_system()
        experiment_files = self.check_experiment_files()
        recent_results = self.check_recent_results()
        system_resources = self.check_system_resources()
        daemon_status = self.check_daemon_status()
        
        # Determine overall status
        statuses = [
            file_system["status"],
            experiment_files["status"],
            recent_results["status"],
            system_resources["status"]
        ]
        
        if "error" in statuses:
            overall_status = "error"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "file_system": file_system,
            "experiment_files": experiment_files,
            "recent_results": recent_results,
            "system_resources": system_resources,
            "daemon_status": daemon_status
        }
        
        logger.info(f"Health check complete. Status: {overall_status}")
        
        # Save report if needed
        self._save_report(report)
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save the health report."""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "bolt/health_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{reports_dir}/health_{timestamp}.json"
            
            # Write report to file
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Health report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving health report: {e}")
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate a markdown report from the health check results."""
        timestamp = report["timestamp"]
        status = report["overall_status"].upper()
        
        md = f"# Bolt Health Report\n\n"
        md += f"Generated: {timestamp}\n\n"
        md += f"## Overall Status: {status}\n\n"
        
        # System Resources
        md += "## System Resources\n\n"
        system = report["system_resources"]
        
        if "system" in system:
            sys_info = system["system"]
            md += f"- **Platform**: {sys_info.get('platform', 'Unknown')}\n"
            md += f"- **Python**: {sys_info.get('python', 'Unknown')}\n"
            md += f"- **Hostname**: {sys_info.get('hostname', 'Unknown')}\n\n"
        
        if "cpu" in system:
            cpu = system["cpu"]
            md += f"- **CPU**: {cpu.get('percent', 0)}% (Cores: {cpu.get('cores', 'Unknown')})\n"
        
        if "memory" in system:
            mem = system["memory"]
            md += f"- **Memory**: {mem.get('percent_used', 0)}% used ({mem.get('used_gb', 0):.2f} GB / {mem.get('total_gb', 0):.2f} GB)\n"
        
        if "disk" in report["file_system"]:
            disk = report["file_system"]["disk"]
            md += f"- **Disk**: {disk.get('percent_used', 0)}% used ({disk.get('used_gb', 0):.2f} GB / {disk.get('total_gb', 0):.2f} GB)\n"
        
        # Daemon Status
        md += "\n## Daemon Status\n\n"
        daemon = report["daemon_status"]
        status_text = daemon["status"].replace("_", " ").title()
        md += f"- **Status**: {status_text}\n"
        
        if daemon["status"] == "running":
            uptime = daemon.get("uptime", 0)
            uptime_str = str(timedelta(seconds=int(uptime)))
            md += f"- **PID**: {daemon.get('pid', 'Unknown')}\n"
            md += f"- **Uptime**: {uptime_str}\n"
        
        # Experiment Files
        md += "\n## Experiment Files\n\n"
        exp_files = report["experiment_files"]
        counts = exp_files.get("count", {})
        
        md += f"- **Total**: {counts.get('total', 0)}\n"
        md += f"- **Valid**: {counts.get('valid', 0)}\n"
        md += f"- **Invalid**: {counts.get('invalid', 0)}\n\n"
        
        if counts.get("invalid", 0) > 0:
            md += "### Invalid Experiments\n\n"
            invalid_exps = [exp for exp in exp_files.get("experiments", []) if exp["status"] != "valid"]
            
            for exp in invalid_exps:
                md += f"- **{exp.get('name', 'Unknown')}** ({exp.get('file', '')}): {exp.get('issues', 'Unknown issue')}\n"
        
        # Recent Results
        md += "\n## Recent Experiment Results\n\n"
        results = report["recent_results"]
        
        if "success_rate" in results:
            success_rate = results["success_rate"] * 100
            md += f"- **Recent Success Rate**: {success_rate:.1f}%\n\n"
        
        md += "### Latest Experiments\n\n"
        md += "| Experiment | Status | Time | Steps |\n"
        md += "|------------|--------|------|-------|\n"
        
        for result in results.get("recent_results", []):
            status = "✅" if result.get("success", False) else "❌"
            name = result.get("name", "Unknown")
            time_str = result.get("execution_time", "").split("T")[0]
            steps = result.get("steps_completed", 0)
            
            md += f"| {name} | {status} | {time_str} | {steps} |\n"
        
        # Issues
        all_issues = []
        for section in ["file_system", "experiment_files", "recent_results", "system_resources", "daemon_status"]:
            if section in report and "issues" in report[section]:
                section_issues = report[section]["issues"]
                if section_issues:
                    all_issues.extend([f"**{section.replace('_', ' ').title()}**: {issue}" for issue in section_issues])
        
        if all_issues:
            md += "\n## Issues Detected\n\n"
            for issue in all_issues:
                md += f"- {issue}\n"
        
        return md

def main():
    parser = argparse.ArgumentParser(description="Check Bolt framework health")
    parser.add_argument('--config', default='bolt/config.yaml', help='Path to configuration file')
    parser.add_argument('--markdown', action='store_true', help='Generate Markdown report')
    parser.add_argument('--output', help='Output file for report (default: stdout)')
    
    args = parser.parse_args()
    
    health_check = BoltHealthCheck(args.config)
    report = health_check.run_all_checks()
    
    if args.markdown:
        md_report = health_check.generate_markdown_report(report)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(md_report)
            print(f"Markdown report written to {args.output}")
        else:
            print(md_report)
    else:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"JSON report written to {args.output}")
        else:
            print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
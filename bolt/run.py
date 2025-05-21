#!/usr/bin/env python3
"""
Bolt Experiment Runner
Executes experiments defined in TOML files with enhanced error handling and logging
"""

import os
import sys
import argparse
import tomli
import time
import yaml
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bolt.log")
    ]
)

logger = logging.getLogger("bolt")

class BoltExperiment:
    def __init__(self, config_path: str, env: str = "production"):
        """
        Initialize a Bolt experiment.
        
        Args:
            config_path: Path to the experiment configuration file
            env: Environment to run in (development, staging, production)
        """
        self.config_path = config_path
        self.env = env
        self.config = self._load_config()
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.load_system_config()
    
    def load_system_config(self):
        """Load the system configuration."""
        try:
            with open("bolt/config.yaml", "rb") as f:
                self.system_config = yaml.safe_load(f)
                
            # Set log level from config
            log_level = self.system_config.get("general", {}).get("log_level", "info").upper()
            logger.setLevel(getattr(logging, log_level))
            
            logger.debug("Loaded system configuration")
        except Exception as e:
            logger.warning(f"Could not load system configuration: {e}")
            self.system_config = {"general": {}, "execution": {}, "operations": {}}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load experiment configuration from TOML file."""
        try:
            with open(self.config_path, "rb") as f:
                config = tomli.load(f)
            logger.info(f"Loaded experiment: {config.get('name', 'Unnamed experiment')}")
            return config
        except Exception as e:
            logger.error(f"Error loading experiment config: {e}")
            sys.exit(1)
    
    def run(self) -> bool:
        """Execute the experiment steps."""
        self.start_time = datetime.now()
        
        logger.info(f"{'='*50}")
        logger.info(f"EXECUTING EXPERIMENT: {self.config.get('name', 'Unnamed')}")
        logger.info(f"DESCRIPTION: {self.config.get('description', 'No description')}")
        logger.info(f"{'='*50}")
        
        if 'steps' not in self.config:
            logger.error("No steps defined in experiment config")
            return False
        
        steps = self.config['steps']
        step_results = []
        success = True
        
        for i, step in enumerate(steps):
            logger.info(f"\nStep {i+1}/{len(steps)}: {step.get('op', 'unknown')}")
            logger.info(f"{'-'*30}")
            
            if 'op' not in step:
                logger.error("Error: Step missing 'op' field")
                step_results.append({
                    "status": "error", 
                    "error": "Missing 'op' field",
                    "step_index": i
                })
                success = False
                continue
            
            # Get timeout for this step
            timeout = step.get("timeout", 
                        self.system_config.get("execution", {}).get("timeout", 3600))
            
            max_retries = step.get("max_retries", 
                           self.system_config.get("execution", {}).get("max_retries", 3))
            
            retry_delay = self.system_config.get("execution", {}).get("retry_delay", 5)
            
            # Execute the step with retries
            result = None
            last_error = None
            for retry in range(max_retries + 1):
                try:
                    if retry > 0:
                        logger.info(f"Retry {retry}/{max_retries} after {retry_delay}s delay")
                        time.sleep(retry_delay)
                    
                    result = self._execute_operation(step, timeout)
                    break
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"Error executing step: {e}")
            
            if result:
                step_results.append(result)
                logger.info(f"Operation completed successfully")
            else:
                error_result = {
                    "status": "error",
                    "error": last_error or "Unknown error",
                    "step_index": i,
                    "step": step
                }
                step_results.append(error_result)
                logger.error(f"Step failed after {max_retries} retries")
                success = False
                
                # Check if we should continue on error
                if not step.get("continue_on_error", False):
                    logger.error("Stopping experiment due to step failure")
                    break
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.results = {
            "experiment_name": self.config.get('name', 'Unnamed'),
            "execution_time": self.start_time.isoformat(),
            "completion_time": self.end_time.isoformat(),
            "duration_seconds": duration,
            "steps": step_results,
            "success": success
        }
        
        # Save results
        self._save_results()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"EXPERIMENT COMPLETE: {'SUCCESS' if success else 'FAILURE'}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"{'='*50}\n")
        
        return success
    
    def _execute_operation(self, step: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Execute a single operation step with timeout."""
        op_type = step['op']
        
        # Get operation settings from system config
        op_config = self.system_config.get("operations", {}).get(op_type, {})
        
        # Simulate different operation types
        if op_type == "search":
            query = step.get('query', 'all')
            shovel = step.get('shovel', 'default')
            threshold = step.get('threshold', op_config.get('default_threshold', 0.7))
            
            logger.info(f"Searching for: {query} using {shovel} (threshold: {threshold})")
            time.sleep(1)  # Simulate work
            
            return {
                "status": "success", 
                "found": 42, 
                "query": query,
                "shovel": shovel,
                "threshold": threshold
            }
            
        elif op_type == "cluster":
            algorithm = step.get('algorithm', op_config.get('default_algorithm', 'kmeans'))
            k = step.get('k', op_config.get('default_k', 5))
            
            logger.info(f"Clustering using {algorithm} with k={k}")
            time.sleep(1.5)  # Simulate work
            
            return {
                "status": "success", 
                "clusters": k, 
                "algorithm": algorithm
            }
            
        elif op_type == "summarize":
            temp = step.get('temperature', op_config.get('default_temperature', 0.7))
            max_tokens = step.get('max_tokens', op_config.get('max_tokens', 500))
            
            logger.info(f"Summarizing with temperature {temp}, max_tokens {max_tokens}")
            time.sleep(2)  # Simulate work
            
            return {
                "status": "success", 
                "temperature": temp,
                "max_tokens": max_tokens
            }
            
        elif op_type == "publish":
            channel = step.get('channel', op_config.get('default_channel', 'default'))
            
            logger.info(f"Publishing to channel: {channel}")
            time.sleep(0.5)  # Simulate work
            
            return {
                "status": "success", 
                "channel": channel
            }
            
        else:
            logger.error(f"Unknown operation type: {op_type}")
            return {
                "status": "error", 
                "error": f"Unknown operation: {op_type}"
            }
    
    def _save_results(self):
        """Save experiment results to file."""
        try:
            # Create results directory if it doesn't exist
            results_dir = self.system_config.get("general", {}).get("results_dir", "bolt/results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate filename
            timestamp = self.start_time.strftime("%Y%m%d-%H%M%S")
            exp_name = self.config.get('name', 'unnamed').lower().replace(' ', '_')
            filename = f"{results_dir}/{exp_name}_{timestamp}.json"
            
            # Write results to file
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run a Bolt experiment")
    parser.add_argument('--experiment', required=True, help='Path to experiment TOML file')
    parser.add_argument('--env', default='production', choices=['development', 'staging', 'production'],
                       help='Environment to run in')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.experiment):
        logger.error(f"Experiment file not found: {args.experiment}")
        sys.exit(1)
    
    experiment = BoltExperiment(args.experiment, args.env)
    success = experiment.run()
    
    if success:
        logger.info("Experiment completed successfully")
        sys.exit(0)
    else:
        logger.error("Experiment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
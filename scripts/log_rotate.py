#!/usr/bin/env python3
"""
Log Rotation and Compression Script

Manages training logs by:
- Writing logs as NDJSON shards (max 10MB per shard)
- Compressing shards to .jsonl.gz on stage end
- Creating samples and summaries for git
"""

import json
import gzip
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LogRotator:
    """Manages log rotation and compression for training artifacts"""
    
    def __init__(self, run_id: str, max_shard_size_mb: int = 10):
        self.run_id = run_id
        self.max_shard_size_bytes = max_shard_size_mb * 1024 * 1024
        self.current_shard = 1
        self.current_size = 0
        self.current_file = None
        self.log_dir = Path(f"data/logs/train/{run_id}")
        self.samples_dir = Path("data/samples")
        
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.samples_dir.mkdir(parents=True, exist_ok=True)
    
    def start_logging(self):
        """Start a new log session"""
        self._open_new_shard()
        logger.info(f"Started logging for run {self.run_id}")
    
    def _open_new_shard(self):
        """Open a new log shard file"""
        if self.current_file:
            self.current_file.close()
        
        shard_filename = f"events-{self.current_shard:05d}.jsonl"
        self.current_file = open(self.log_dir / shard_filename, 'w')
        self.current_size = 0
        logger.info(f"Opened new shard: {shard_filename}")
    
    def write_event(self, event: Dict[str, Any]):
        """Write a single event to the current shard"""
        if not self.current_file:
            self._open_new_shard()
        
        # Write event as NDJSON
        event_line = json.dumps(event) + '\n'
        self.current_file.write(event_line)
        self.current_file.flush()
        
        self.current_size += len(event_line)
        
        # Check if we need a new shard
        if self.current_size >= self.max_shard_size_bytes:
            self.current_shard += 1
            self._open_new_shard()
    
    def flush_and_compress(self):
        """Flush current shard and compress all shards"""
        if self.current_file:
            self.current_file.close()
            self.current_file = None
        
        logger.info(f"Compressing {self.current_shard} shards for run {self.run_id}")
        
        # Compress all shards
        for shard_num in range(1, self.current_shard + 1):
            shard_file = self.log_dir / f"events-{shard_num:05d}.jsonl"
            if shard_file.exists():
                compressed_file = self.log_dir / f"events-{shard_num:05d}.jsonl.gz"
                
                # Compress the file
                with open(shard_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                # Remove original
                shard_file.unlink()
                logger.info(f"Compressed {shard_file.name} -> {compressed_file.name}")
    
    def create_sample(self, max_lines: int = 500):
        """Create a sample file for git (first N lines)"""
        sample_file = self.samples_dir / f"{self.run_id}-sample.json"
        
        # Find the first shard
        first_shard = self.log_dir / "events-00001.jsonl.gz"
        if not first_shard.exists():
            first_shard = self.log_dir / "events-00001.jsonl"
        
        if not first_shard.exists():
            logger.warning(f"No log files found for run {self.run_id}")
            return
        
        sample_events = []
        line_count = 0
        
        # Read from compressed or uncompressed file
        if first_shard.suffix == '.gz':
            with gzip.open(first_shard, 'rt') as f:
                for line in f:
                    if line_count >= max_lines:
                        break
                    try:
                        event = json.loads(line.strip())
                        sample_events.append(event)
                        line_count += 1
                    except json.JSONDecodeError:
                        continue
        else:
            with open(first_shard, 'r') as f:
                for line in f:
                    if line_count >= max_lines:
                        break
                    try:
                        event = json.loads(line.strip())
                        sample_events.append(event)
                        line_count += 1
                    except json.JSONDecodeError:
                        continue
        
        # Write sample
        with open(sample_file, 'w') as f:
            json.dump(sample_events, f, indent=2)
        
        logger.info(f"Created sample file: {sample_file} ({len(sample_events)} events)")
    
    def create_summary(self):
        """Create a summary file with counts and metrics"""
        summary_file = self.samples_dir / f"{self.run_id}-summary.json"
        
        # Count events and calculate metrics
        total_events = 0
        event_types = {}
        stages = set()
        
        # Process all shards
        for shard_file in self.log_dir.glob("events-*.jsonl*"):
            if shard_file.suffix == '.gz':
                with gzip.open(shard_file, 'rt') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            total_events += 1
                            
                            # Count event types
                            event_type = event.get('type', 'unknown')
                            event_types[event_type] = event_types.get(event_type, 0) + 1
                            
                            # Track stages
                            if 'stage' in event:
                                stages.add(event['stage'])
                        except json.JSONDecodeError:
                            continue
            else:
                with open(shard_file, 'r') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            total_events += 1
                            
                            # Count event types
                            event_type = event.get('type', 'unknown')
                            event_types[event_type] = event_types.get(event_type, 0) + 1
                            
                            # Track stages
                            if 'stage' in event:
                                stages.add(event['stage'])
                        except json.JSONDecodeError:
                            continue
        
        # Create summary
        summary = {
            "run_id": self.run_id,
            "timestamp": time.time(),
            "total_events": total_events,
            "event_types": event_types,
            "stages": list(stages),
            "shard_count": self.current_shard,
            "compressed": True
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Created summary file: {summary_file}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.current_file:
            self.current_file.close()
            self.current_file = None

def main():
    """Test the log rotator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Log rotation and compression")
    parser.add_argument("--run-id", required=True, help="Run ID for this training session")
    parser.add_argument("--test", action="store_true", help="Run test with sample events")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    rotator = LogRotator(args.run_id)
    
    if args.test:
        # Generate test events
        rotator.start_logging()
        
        for i in range(1000):
            event = {
                "timestamp": time.time(),
                "type": "training_step",
                "step": i,
                "loss": 0.5 + (i * 0.001),
                "stage": "baseline",
                "data": f"sample_data_{i}" * 100  # Make events larger
            }
            rotator.write_event(event)
        
        rotator.flush_and_compress()
        rotator.create_sample()
        rotator.create_summary()
        rotator.cleanup()
        
        print(f"✅ Test completed. Check data/logs/train/{args.run_id}/ and data/samples/")

if __name__ == "__main__":
    main()

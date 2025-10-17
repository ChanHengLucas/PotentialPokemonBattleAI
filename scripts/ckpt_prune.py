#!/usr/bin/env python3
"""
Checkpoint Pruning Script

Manages checkpoint storage by:
- Keeping only the last N checkpoints (default N=3)
- Deleting older checkpoints to save space
- Preserving metadata for analysis
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
import argparse
import logging

logger = logging.getLogger(__name__)

class CheckpointPruner:
    """Manages checkpoint pruning and cleanup"""
    
    def __init__(self, checkpoint_dir: str = "models/checkpoints", keep_count: int = 3):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.keep_count = keep_count
        self.samples_dir = Path("data/samples")
        
        # Create samples directory if it doesn't exist
        self.samples_dir.mkdir(parents=True, exist_ok=True)
    
    def prune_checkpoints(self) -> Dict[str, Any]:
        """Prune old checkpoints, keeping only the most recent N"""
        if not self.checkpoint_dir.exists():
            logger.warning(f"Checkpoint directory {self.checkpoint_dir} does not exist")
            return {"pruned": 0, "kept": 0, "errors": []}
        
        # Find all checkpoint directories
        checkpoint_dirs = []
        for item in self.checkpoint_dir.iterdir():
            if item.is_dir() and item.name.startswith("checkpoint_"):
                checkpoint_dirs.append(item)
        
        if len(checkpoint_dirs) <= self.keep_count:
            logger.info(f"Only {len(checkpoint_dirs)} checkpoints found, no pruning needed")
            return {"pruned": 0, "kept": len(checkpoint_dirs), "errors": []}
        
        # Sort by modification time (newest first)
        checkpoint_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep the most recent N checkpoints
        to_keep = checkpoint_dirs[:self.keep_count]
        to_prune = checkpoint_dirs[self.keep_count:]
        
        logger.info(f"Keeping {len(to_keep)} checkpoints, pruning {len(to_prune)}")
        
        pruned_count = 0
        errors = []
        
        for checkpoint_dir in to_prune:
            try:
                # Extract metadata before deletion
                metadata = self._extract_checkpoint_metadata(checkpoint_dir)
                if metadata:
                    self._save_checkpoint_metadata(checkpoint_dir.name, metadata)
                
                # Delete the checkpoint directory
                shutil.rmtree(checkpoint_dir)
                pruned_count += 1
                logger.info(f"Pruned checkpoint: {checkpoint_dir.name}")
                
            except Exception as e:
                error_msg = f"Failed to prune {checkpoint_dir.name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "pruned": pruned_count,
            "kept": len(to_keep),
            "errors": errors
        }
    
    def _extract_checkpoint_metadata(self, checkpoint_dir: Path) -> Dict[str, Any]:
        """Extract metadata from a checkpoint directory"""
        metadata = {
            "checkpoint_name": checkpoint_dir.name,
            "size_mb": self._get_directory_size_mb(checkpoint_dir),
            "files": []
        }
        
        # List files in checkpoint
        for file_path in checkpoint_dir.rglob("*"):
            if file_path.is_file():
                metadata["files"].append({
                    "name": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return metadata
    
    def _get_directory_size_mb(self, directory: Path) -> float:
        """Get directory size in MB"""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def _save_checkpoint_metadata(self, checkpoint_name: str, metadata: Dict[str, Any]):
        """Save checkpoint metadata to samples directory"""
        metadata_file = self.samples_dir / f"{checkpoint_name}-metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata for {checkpoint_name}")
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all checkpoints with metadata"""
        if not self.checkpoint_dir.exists():
            return []
        
        checkpoints = []
        for item in self.checkpoint_dir.iterdir():
            if item.is_dir() and item.name.startswith("checkpoint_"):
                metadata = {
                    "name": item.name,
                    "size_mb": self._get_directory_size_mb(item),
                    "modified": item.stat().st_mtime,
                    "files": len(list(item.rglob("*")))
                }
                checkpoints.append(metadata)
        
        # Sort by modification time (newest first)
        checkpoints.sort(key=lambda x: x["modified"], reverse=True)
        return checkpoints

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Checkpoint pruning utility")
    parser.add_argument("--checkpoint-dir", default="models/checkpoints", 
                       help="Checkpoint directory path")
    parser.add_argument("--keep", type=int, default=3, 
                       help="Number of checkpoints to keep")
    parser.add_argument("--list", action="store_true", 
                       help="List all checkpoints")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be pruned without actually deleting")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    pruner = CheckpointPruner(args.checkpoint_dir, args.keep)
    
    if args.list:
        checkpoints = pruner.list_checkpoints()
        print(f"\nFound {len(checkpoints)} checkpoints:")
        for cp in checkpoints:
            print(f"  {cp['name']} - {cp['size_mb']:.1f}MB - {cp['files']} files")
        return
    
    if args.dry_run:
        checkpoints = pruner.list_checkpoints()
        if len(checkpoints) > args.keep:
            print(f"\nWould prune {len(checkpoints) - args.keep} checkpoints:")
            for cp in checkpoints[args.keep:]:
                print(f"  {cp['name']} - {cp['size_mb']:.1f}MB")
        else:
            print(f"\nNo pruning needed ({len(checkpoints)} <= {args.keep})")
        return
    
    # Perform pruning
    result = pruner.prune_checkpoints()
    
    print(f"\nPruning complete:")
    print(f"  Pruned: {result['pruned']} checkpoints")
    print(f"  Kept: {result['kept']} checkpoints")
    
    if result['errors']:
        print(f"  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    {error}")

if __name__ == "__main__":
    main()

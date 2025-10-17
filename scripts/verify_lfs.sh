#!/bin/bash
# Verify that large files are properly tracked by Git LFS

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

MAX_SIZE_MB=50
MAX_SIZE_BYTES=$((MAX_SIZE_MB * 1024 * 1024))

print_info "Verifying Git LFS compliance (max size: ${MAX_SIZE_MB}MB)..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  print_error "Not in a git repository"
  exit 1
fi

# Get list of staged files
staged_files=$(git diff --cached --name-only 2>/dev/null || echo "")

if [ -z "$staged_files" ]; then
  print_success "No staged files to check"
  exit 0
fi

print_info "Checking staged files..."

# Get list of LFS tracked files
lfs_files=$(git lfs ls-files -n 2>/dev/null || echo "")

violations=0

# Check each staged file
while IFS= read -r file; do
  if [ -f "$file" ]; then
    # Get file size
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    
    if [ "$size" -gt "$MAX_SIZE_BYTES" ]; then
      size_mb=$((size / 1024 / 1024))
      
      # Check if file is tracked by LFS
      if echo "$lfs_files" | grep -q "^$file$"; then
        print_success "Large file properly tracked by LFS: $file (${size_mb}MB)"
      else
        print_error "Large file NOT tracked by LFS: $file (${size_mb}MB)"
        print_info "  This file should be tracked by LFS or reduced in size"
        print_info "  To fix: git lfs track \"$file\" && git add .gitattributes"
        violations=$((violations + 1))
      fi
    else
      # Small file, check if it's under data/logs/ and should be LFS tracked
      if [[ "$file" =~ ^data/logs/.*\.(json|jsonl|json\.gz|jsonl\.gz)$ ]]; then
        if echo "$lfs_files" | grep -q "^$file$"; then
          print_success "Training log properly tracked by LFS: $file"
        else
          print_warning "Training log not tracked by LFS: $file (may be small enough for regular Git)"
        fi
      fi
    fi
  fi
done <<< "$staged_files"

# Check for LFS files that should be tracked
if [ -n "$lfs_files" ]; then
  print_info "LFS tracked files:"
  echo "$lfs_files" | while read -r lfs_file; do
    if [ -n "$lfs_file" ]; then
      print_info "  $lfs_file"
    fi
  done
else
  print_info "No files currently tracked by LFS"
fi

if [ $violations -gt 0 ]; then
  print_error "Found $violations violations of LFS policy"
  print_info ""
  print_info "To fix violations:"
  print_info "1. For training logs: git lfs track \"data/logs/**/*.json\""
  print_info "2. For other large files: reduce file size or add to .gitignore"
  print_info "3. Stage .gitattributes: git add .gitattributes"
  exit 1
else
  print_success "All large files are properly tracked by LFS"
  exit 0
fi

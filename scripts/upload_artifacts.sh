#!/bin/bash
# Upload Artifacts Script

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

# Default values
MODE="local_only"
KEEP_CHECKPOINTS=2
RELEASE_TAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    github_release)
      MODE="github_release"
      shift
      ;;
    local_only)
      MODE="local_only"
      shift
      ;;
    --keep)
      KEEP_CHECKPOINTS="$2"
      shift 2
      ;;
    --tag)
      RELEASE_TAG="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [github_release|local_only] [--keep N] [--tag TAG]"
      echo ""
      echo "Modes:"
      echo "  github_release  - Upload to GitHub release"
      echo "  local_only      - Keep files locally (default)"
      echo ""
      echo "Options:"
      echo "  --keep N        - Keep last N checkpoints (default: 2)"
      echo "  --tag TAG       - Custom release tag"
      echo ""
      echo "Examples:"
      echo "  $0 github_release"
      echo "  $0 github_release --keep 3 --tag v1.0.0"
      echo "  $0 local_only --keep 5"
      exit 0
      ;;
    *)
      print_error "Unknown option: $1"
      exit 1
      ;;
  esac
done

print_info "Upload Artifacts - Mode: $MODE"

# Check if required directories exist
if [ ! -d "data/logs/train" ]; then
  print_error "Training logs directory not found: data/logs/train"
  exit 1
fi

if [ ! -d "models/checkpoints" ]; then
  print_error "Checkpoints directory not found: models/checkpoints"
  exit 1
fi

# Find the most recent run
LATEST_RUN=$(find data/logs/train -maxdepth 1 -type d -name "*" | sort | tail -1 | xargs basename)
if [ -z "$LATEST_RUN" ]; then
  print_error "No training runs found in data/logs/train"
  exit 1
fi

print_info "Latest run: $LATEST_RUN"

# Collect artifacts
ARTIFACTS=()
UPLOAD_DIR="artifacts_upload"

# Create upload directory
rm -rf "$UPLOAD_DIR"
mkdir -p "$UPLOAD_DIR"

# 1. Compressed logs
print_info "Collecting compressed logs..."
if [ -d "data/logs/train/$LATEST_RUN" ]; then
  for log_file in data/logs/train/$LATEST_RUN/*.jsonl.gz; do
    if [ -f "$log_file" ]; then
      cp "$log_file" "$UPLOAD_DIR/"
      ARTIFACTS+=("$(basename "$log_file")")
      print_info "  Added: $(basename "$log_file")"
    fi
  done
else
  print_warning "No compressed logs found for run $LATEST_RUN"
fi

# 2. Recent checkpoints
print_info "Collecting recent checkpoints (keeping last $KEEP_CHECKPOINTS)..."
checkpoint_count=0
for checkpoint_dir in models/checkpoints/checkpoint_*; do
  if [ -d "$checkpoint_dir" ]; then
    checkpoint_name=$(basename "$checkpoint_dir")
    
    # Create compressed checkpoint
    checkpoint_archive="$UPLOAD_DIR/${checkpoint_name}.tar.gz"
    tar -czf "$checkpoint_archive" -C models/checkpoints "$checkpoint_name"
    ARTIFACTS+=("${checkpoint_name}.tar.gz")
    print_info "  Added: ${checkpoint_name}.tar.gz"
    
    checkpoint_count=$((checkpoint_count + 1))
    if [ $checkpoint_count -ge $KEEP_CHECKPOINTS ]; then
      break
    fi
  fi
done

# 3. Samples and summaries
print_info "Collecting samples and summaries..."
if [ -d "data/samples" ]; then
  for sample_file in data/samples/*; do
    if [ -f "$sample_file" ]; then
      cp "$sample_file" "$UPLOAD_DIR/"
      ARTIFACTS+=("$(basename "$sample_file")")
      print_info "  Added: $(basename "$sample_file")"
    fi
  done
fi

# 4. Training diagnostics
print_info "Collecting training diagnostics..."
if [ -f "data/reports/training_diagnostics.json" ]; then
  cp "data/reports/training_diagnostics.json" "$UPLOAD_DIR/"
  ARTIFACTS+=("training_diagnostics.json")
  print_info "  Added: training_diagnostics.json"
fi

# Show collected artifacts
print_info "Collected artifacts:"
for artifact in "${ARTIFACTS[@]}"; do
  size=$(du -h "$UPLOAD_DIR/$artifact" | cut -f1)
  print_info "  $artifact ($size)"
done

# Handle upload mode
if [ "$MODE" = "github_release" ]; then
  print_info "Uploading to GitHub release..."
  
  # Check if gh CLI is installed
  if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed"
    print_info "Install it with: brew install gh (macOS) or visit: https://cli.github.com/"
    exit 1
  fi
  
  # Check if authenticated
  if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI"
    print_info "Run: gh auth login"
    exit 1
  fi
  
  # Generate release tag
  if [ -z "$RELEASE_TAG" ]; then
    RELEASE_TAG="train-$(date +%Y%m%d)-$LATEST_RUN"
  fi
  
  print_info "Creating release: $RELEASE_TAG"
  
  # Create release
  gh release create "$RELEASE_TAG" \
    --title "Training Artifacts - $LATEST_RUN" \
    --notes "Training artifacts for run $LATEST_RUN

Artifacts included:
$(printf '%s\n' "${ARTIFACTS[@]}" | sed 's/^/- /')

Generated on: $(date)
Run ID: $LATEST_RUN" \
    "$UPLOAD_DIR"/*
  
  if [ $? -eq 0 ]; then
    print_success "Successfully uploaded artifacts to GitHub release: $RELEASE_TAG"
    print_info "Release URL: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/releases/tag/$RELEASE_TAG"
  else
    print_error "Failed to create GitHub release"
    exit 1
  fi
  
elif [ "$MODE" = "local_only" ]; then
  print_info "Keeping artifacts locally..."
  print_success "Artifacts collected in: $UPLOAD_DIR/"
  print_info "Total size: $(du -sh "$UPLOAD_DIR" | cut -f1)"
  print_info ""
  print_info "To upload manually:"
  print_info "  - Upload $UPLOAD_DIR/ to your preferred storage"
  print_info "  - Or use: gh release create <tag> $UPLOAD_DIR/*"
fi

# Cleanup old artifacts if requested
if [ "$MODE" = "github_release" ]; then
  print_info "Cleaning up old local artifacts..."
  
  # Remove old compressed logs (keep last 3 runs)
  find data/logs/train -maxdepth 1 -type d | sort | head -n -3 | xargs rm -rf 2>/dev/null || true
  
  # Prune old checkpoints
  if [ -f "scripts/ckpt_prune.py" ]; then
    python3 scripts/ckpt_prune.py --keep $KEEP_CHECKPOINTS
  fi
  
  print_success "Cleanup completed"
fi

print_success "Upload artifacts completed successfully!"

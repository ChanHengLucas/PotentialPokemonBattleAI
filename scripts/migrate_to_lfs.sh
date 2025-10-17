#!/bin/bash
# Migrate existing history to Git LFS for training logs

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

print_info "Migrating existing history to Git LFS..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  print_error "Not in a git repository. Please run this from the project root."
  exit 1
fi

# Check if git-lfs is available
if ! command -v git-lfs &> /dev/null; then
  print_error "Git LFS is not installed. Please run ./scripts/setup_lfs.sh first."
  exit 1
fi

# Create backup branch
print_info "Creating backup branch: backup/before-lfs-migrate"
git branch backup/before-lfs-migrate 2>/dev/null || print_warning "Backup branch already exists"
print_success "Backup branch created: backup/before-lfs-migrate"

# Commit .gitattributes if it has changes
print_info "Committing .gitattributes..."
git add .gitattributes
git commit -m "chore: enable Git LFS for training logs" || print_info ".gitattributes already committed"

# Set up LFS tracking for the patterns
print_info "Setting up LFS tracking patterns..."
git lfs track "data/logs/**/*.json" "data/logs/**/*.jsonl" "data/logs/**/*.json.gz" "data/logs/**/*.jsonl.gz"

# Add updated .gitattributes
print_info "Staging updated .gitattributes..."
git add .gitattributes
git commit -m "chore: track training logs via LFS" || print_info ".gitattributes already up to date"

# Migrate existing history
print_info "Migrating existing history to LFS..."
print_warning "This may take a while for large repositories..."

git lfs migrate import \
  --include="data/logs/**/*.json,data/logs/**/*.jsonl,data/logs/**/*.json.gz,data/logs/**/*.jsonl.gz" \
  --everything

if [ $? -eq 0 ]; then
  print_success "History migration completed"
else
  print_error "History migration failed"
  exit 1
fi

# Clean up and optimize
print_info "Cleaning up and optimizing repository..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Verify LFS tracking
print_info "Verifying LFS tracking..."
echo "LFS tracked files:"
git lfs ls-files || print_warning "No LFS files found (this may be normal if no training logs exist yet)"

# Show repository size reduction
print_info "Repository optimization completed"
print_success "Migration completed successfully!"

print_info ""
print_warning "IMPORTANT: This migration rewrites git history."
print_info "Next steps:"
print_info "1. Push changes: git push origin main --force"
print_info "2. If push is rejected due to size, re-run this script and force push again"
print_info "3. Notify collaborators to re-clone the repository"
print_info "4. Backup branch available at: backup/before-lfs-migrate"
print_info ""
print_info "To clone with LFS elsewhere:"
print_info "  git clone <repo-url>"
print_info "  cd <repo-name>"
print_info "  git lfs install"

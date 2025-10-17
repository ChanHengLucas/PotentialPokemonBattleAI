#!/bin/bash
# Setup Git LFS for PokéAI training logs

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

print_info "Setting up Git LFS for PokéAI training logs..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  print_error "Not in a git repository. Please run this from the project root."
  exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
  print_error "Git is not installed. Please install Git first."
  exit 1
fi

# Check if git-lfs is available
if ! command -v git-lfs &> /dev/null; then
  print_error "Git LFS is not installed."
  print_info "Install instructions:"
  print_info "  macOS: brew install git-lfs"
  print_info "  Windows: winget install Git.Git-LFS"
  print_info "  Linux: sudo apt install git-lfs (Ubuntu/Debian)"
  print_info "         sudo yum install git-lfs (RHEL/CentOS)"
  print_info "         sudo pacman -S git-lfs (Arch)"
  exit 1
fi

print_success "Git LFS is installed"

# Install Git LFS for this repository
print_info "Installing Git LFS for this repository..."
git lfs install

if [ $? -eq 0 ]; then
  print_success "Git LFS installed successfully"
else
  print_error "Failed to install Git LFS"
  exit 1
fi

# Check if .gitattributes exists and has the right patterns
if [ ! -f ".gitattributes" ]; then
  print_error ".gitattributes file not found. Please ensure it exists with LFS patterns."
  exit 1
fi

# Verify .gitattributes has the required patterns
print_info "Verifying .gitattributes patterns..."

# Check for each pattern individually
if grep -q "data/logs/\*\*/\*.json" .gitattributes; then
  print_success "Pattern found: data/logs/**/*.json"
else
  print_error "Missing pattern: data/logs/**/*.json"
  exit 1
fi

if grep -q "data/logs/\*\*/\*.jsonl" .gitattributes; then
  print_success "Pattern found: data/logs/**/*.jsonl"
else
  print_error "Missing pattern: data/logs/**/*.jsonl"
  exit 1
fi

if grep -q "data/logs/\*\*/\*.jsonl.gz" .gitattributes; then
  print_success "Pattern found: data/logs/**/*.jsonl.gz"
else
  print_error "Missing pattern: data/logs/**/*.jsonl.gz"
  exit 1
fi

if grep -q "data/logs/\*\*/\*.json.gz" .gitattributes; then
  print_success "Pattern found: data/logs/**/*.json.gz"
else
  print_error "Missing pattern: data/logs/**/*.json.gz"
  exit 1
fi

# Stage .gitattributes if it has changes
if git diff --cached --name-only | grep -q ".gitattributes" || git diff --name-only | grep -q ".gitattributes"; then
  print_info "Staging .gitattributes..."
  git add .gitattributes
  print_success ".gitattributes staged"
else
  print_info ".gitattributes is already up to date"
fi

print_success "Git LFS setup completed!"
print_info ""
print_info "Next steps:"
print_info "1. Run: ./scripts/migrate_to_lfs.sh"
print_info "2. This will migrate existing history to LFS"
print_info "3. You'll need to force push: git push origin main --force"
print_warning "Note: Migration rewrites git history. Make sure you have backups!"

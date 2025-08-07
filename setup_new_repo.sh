#!/bin/bash

# Replace YOUR_USERNAME and YOUR_REPO_NAME with actual values
# Example: https://github.com/modir123456/persian-file-copier-pro.git

echo "=== Setting up new repository ==="

# Remove old remote
git remote remove origin

# Add new remote (replace with your new repo URL)
echo "Enter your new repository URL:"
read NEW_REPO_URL
git remote add origin $NEW_REPO_URL

# Push current branch to new repository
git push -u origin windows-compatibility-fix

# Also push main branch
git checkout main 2>/dev/null || git checkout master 2>/dev/null || echo "No main/master branch found"
git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || echo "Could not push main/master"

# Switch back to the feature branch
git checkout windows-compatibility-fix

echo "=== Setup complete! ==="
echo "Your code is now in the new repository on branch: windows-compatibility-fix"
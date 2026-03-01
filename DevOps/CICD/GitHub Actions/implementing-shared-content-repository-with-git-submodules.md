---
title: Implementing a Shared Content Repository with Git Submodules and GitHub Actions
image: git
tags:
- Git
- GitHub Actions
- CI/CD
- Submodules
- Automation
- DevOps
- Hexo
- Static Sites
---
## Description

This article documents the implementation of a shared content repository architecture using Git submodules and GitHub Actions to manage markdown content across multiple static site deployments. The solution enables centralized content management with automated deployment to multiple frontends.

## Architecture Overview

The implementation uses a three-repository structure:

1. **Content Repository** (`wikip-co/content`): Central repository containing all markdown files
2. **Site Repository 1** (`wikip-co/wikip.co`): Hexo static site using content as a submodule
3. **Site Repository 2** (`anthonyrussano/anthonyrussano.com`): Hexo static site using content as a submodule

When markdown files are modified in the content repository, GitHub Actions automatically triggers rebuilds of both site repositories.

## Implementation Steps

### Step 1: Analyze Existing Content

First, compare the content between both repositories to identify differences:

```bash
# Count markdown files in each repo
find /home/anthony/wikip.co/site/source/_posts -name "*.md" | wc -l
# Result: 3,188 files

find /home/anthony/anthonyrussano.com/site/source/_posts -name "*.md" | wc -l
# Result: 3,195 files

# Compare directories to find differences
diff -r wikip.co/site/source/_posts/ anthonyrussano.com/site/source/_posts/ --brief
```

**Reasoning**: Understanding the differences between repositories ensures no content is lost during the merge. In this case, there were only 8 differences:
- 2 files with different content
- 6 unique files/folders across both repos

### Step 2: Create Unified Content Repository

Merge content from both repositories into a single unified collection:

```bash
# Create unified directory with content from one repo
mkdir -p /home/anthony/content-unified
cp -r /home/anthony/anthonyrussano.com/site/source/_posts/* /home/anthony/content-unified/

# Copy unique files from the other repo
cp -r "/home/anthony/wikip.co/site/source/_posts/Child Development/Parenting" \
     "/home/anthony/content-unified/Child Development/"
cp -r "/home/anthony/wikip.co/site/source/_posts/Current Events/Technology" \
     "/home/anthony/content-unified/Current Events/"

# Resolve conflicts by choosing the better version
cp "/home/anthony/wikip.co/site/source/_posts/Natural Healing/Oils and Fats/coconut-oil.md" \
   "/home/anthony/content-unified/Natural Healing/Oils and Fats/coconut-oil.md"
```

**Reasoning**: Starting with the repo containing more files (anthonyrussano.com with 3,195 files) as the base, then adding unique content from the other repo ensures all content is preserved. For conflicting files, manual review determined which version had more complete information.

Final unified count: **3,198 markdown files**

### Step 3: Create GitHub Repository for Content

Initialize the unified content as a Git repository and push to GitHub:

```bash
cd /home/anthony/content-unified
git init
git config user.email "me@anthonyrussano.com"
git config user.name "Anthony Russano"
git add .
git commit -m "Initial commit: unified markdown content from wikip.co and anthonyrussano.com"

# Create repository using GitHub CLI
gh repo create wikip-co/content --public \
  --description "Shared markdown content for wikip.co and anthonyrussano.com" \
  --source . --remote origin

# Push to GitHub
git branch -M main
git push -u origin main
```

**Reasoning**: Using `gh` CLI streamlines repository creation and automatically configures the remote. The organization account (`wikip-co`) provides a neutral namespace for shared content accessible to both sites.

### Step 4: Configure Submodules in Site Repositories

Replace the `_posts` directory in each site repository with the content submodule:

```bash
# For wikip.co
cd /home/anthony/wikip.co
git rm -r site/source/_posts
git submodule add https://github.com/wikip-co/content.git site/source/_posts
git add .
git commit -m "Replace _posts with content submodule"
git push

# For anthonyrussano.com
cd /home/anthony/anthonyrussano.com
git rm -r site/source/_posts
git submodule add https://github.com/wikip-co/content.git site/source/_posts
git add .
git commit -m "Replace _posts with content submodule"
git push
```

**Reasoning**: Git submodules allow referencing an external repository at a specific commit. This enables both site repos to share the same content while maintaining their own site configurations, themes, and build processes.

### Step 5: Configure Submodule to Track Main Branch

Update `.gitmodules` to track the main branch:

```bash
# Edit .gitmodules in both repos to add:
[submodule "site/source/_posts"]
    path = site/source/_posts
    url = https://github.com/wikip-co/content.git
    branch = main
```

**Reasoning**: By specifying `branch = main`, `git submodule update --remote` will fetch the latest commit from the main branch rather than staying locked to a specific commit. This enables automatic content updates.

### Step 6: Create Trigger Workflow in Content Repository

Create a GitHub Actions workflow that triggers both site repositories when content changes:

```yaml
# .github/workflows/trigger-sites.yml
name: Trigger Site Rebuilds

on:
  push:
    branches:
      - main
    paths:
      - '**/*.md'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  trigger-rebuilds:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger wikip.co rebuild
        run: |
          curl -L \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.TRIGGER_TOKEN }}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            https://api.github.com/repos/wikip-co/wikip.co/dispatches \
            -d '{"event_type":"content-updated","client_payload":{}}'

      - name: Trigger anthonyrussano.com rebuild
        run: |
          curl -L \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.TRIGGER_TOKEN }}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            https://api.github.com/repos/anthonyrussano/anthonyrussano.com/dispatches \
            -d '{"event_type":"content-updated","client_payload":{}}'
```

**Reasoning**: Using `repository_dispatch` events allows triggering workflows in other repositories. The workflow only runs when `.md` files change, avoiding unnecessary builds for infrastructure changes.

### Step 7: Set Up GitHub Token

Create and configure a Personal Access Token for triggering workflows:

```bash
# The existing gh CLI token already had repo scope
# Store it as a secret in the content repository
gh auth token | gh secret set TRIGGER_TOKEN -R wikip-co/content

# Verify the secret was created
gh secret list -R wikip-co/content
```

**Reasoning**: The `repo` scope includes permission to trigger `repository_dispatch` events. Using the existing `gh` CLI token avoids creating additional tokens, and storing it as a GitHub Secret keeps it secure.

### Step 8: Update Site Repository Workflows

Modify the deployment workflows in both site repositories to:
1. Listen for `repository_dispatch` events
2. Update submodules to pull latest content

**For wikip.co** (`/.github/workflows/generator.yml`):

```yaml
on:
  workflow_dispatch:
  repository_dispatch:
    types: [content-updated]
  push:
    branches:
      - main
    paths:
      - 'site/**'
```

Update the build step:

```yaml
- name: Build site
  env:
    NODE_OPTIONS: --max-old-space-size=5168
  run: |
    git config --global user.email "me@anthonyrussano.com"
    git config --global user.name "Anthony Russano"
    git submodule update --init --remote
    git pull
    # ... rest of build steps
```

**For anthonyrussano.com** (`.github/workflows/generator.yml`):

Same changes as wikip.co, but with `master` branch instead of `main`.

**Reasoning**:
- `repository_dispatch` with type `content-updated` allows external triggers from the content repo
- `git submodule update --init --remote` fetches the latest commit from the tracked branch (main)
- Removing `--merge` flag avoids merge conflicts by simply checking out the latest commit

### Step 9: Add Email Notifications (Optional)

Fetch email credentials from Vault and store as GitHub Secrets:

```bash
# Fetch credentials from on-prem Vault
curl -s -H "X-Vault-Token: <token>" \
  https://vault.wikip.co/v1/secret/data/jarvis/email | jq -r '.data.data'

# Store as GitHub Secrets in both site repos
printf "jarvis@wikip.co" | gh secret set EMAIL_USERNAME -R wikip-co/wikip.co
printf "<password>" | gh secret set EMAIL_PASSWORD -R wikip-co/wikip.co
printf "smtp.protonmail.ch" | gh secret set EMAIL_SMTP_SERVER -R wikip-co/wikip.co
printf "587" | gh secret set EMAIL_SMTP_PORT -R wikip-co/wikip.co

# Repeat for anthonyrussano.com
```

Add email notification step to workflows:

```yaml
- name: Send email notification
  if: always()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: ${{ secrets.EMAIL_SMTP_SERVER }}
    server_port: ${{ secrets.EMAIL_SMTP_PORT }}
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'wikip.co Build ${{ job.status }}: ${{ github.event.head_commit.message }}'
    to: me@anthonyrussano.com
    from: ${{ secrets.EMAIL_USERNAME }}
    body: |
      Repository: ${{ github.repository }}
      Branch: ${{ github.ref }}
      Commit: ${{ github.sha }}
      Status: ${{ job.status }}
      Workflow: ${{ github.workflow }}
      Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

**Reasoning**:
- Fetching credentials from Vault maintains a single source of truth
- Storing as GitHub Secrets enables use with GitHub-hosted runners (Vault is only accessible from on-prem runners)
- Using `if: always()` ensures notifications are sent even if the build fails
- Including run URL in email body provides quick access to build logs

## Workflow Execution

When a markdown file is updated in the content repository:

1. **Content repo** workflow triggers on push to main
2. GitHub Actions sends `repository_dispatch` events to both site repos
3. **Site repos** receive the event and trigger their workflows
4. Site workflows:
   - Check out code with submodules
   - Run `git submodule update --init --remote` to get latest content
   - Build Hexo site
   - Push generated HTML to public submodule
   - Build and push Docker image
   - Send email notification

## Common Issues and Solutions

### Issue: "refusing to merge unrelated histories"

**Problem**: Using `git submodule update --remote --merge` causes merge errors.

**Solution**: Remove the `--merge` flag:
```bash
git submodule update --init --remote
```

**Reasoning**: The submodule just needs to check out the latest commit, not merge changes.

### Issue: Git push rejected during workflow

**Problem**: Race condition when pushing to site repo while workflow is running.

**Solution**: This is cosmetic - the important parts (site generation and deployment to public repo) complete successfully. The final push failure doesn't affect the deployed site.

### Issue: Missing TRIGGER_TOKEN secret

**Problem**: Content workflow fails with "Bad credentials" error.

**Solution**: Ensure the token is created and stored:
```bash
gh auth token | gh secret set TRIGGER_TOKEN -R wikip-co/content
```

## Benefits of This Architecture

1. **Single Source of Truth**: All markdown content exists in one repository
2. **Simplified Content Management**: Writers only need to commit to one place
3. **Automated Deployment**: Changes automatically propagate to all sites
4. **Version Control**: Full Git history for all content changes
5. **Separation of Concerns**: Content separated from site configuration and themes
6. **Flexible Frontends**: Each site can have different themes, configurations, or frameworks

## Alternative Approaches

### Manual Submodule Updates

Instead of automatic triggers, sites could manually update submodules:

```bash
cd /home/anthony/wikip.co/site/source/_posts
git pull origin main
cd ../../..
git add site/source/_posts
git commit -m "Update content"
git push
```

**Trade-off**: More control but requires manual intervention for every content update.

### Monorepo Approach

All content and site configurations in a single repository with separate build paths.

**Trade-off**: Simpler structure but less flexibility for different site configurations and harder to manage permissions.

### Content API

Content served via API (headless CMS) instead of Git submodules.

**Trade-off**: More dynamic but adds infrastructure complexity and potential latency.

## Conclusion

This Git submodule approach provides an optimal balance between automation and simplicity for managing shared content across multiple static sites. It leverages GitHub Actions for orchestration while maintaining the simplicity and version control benefits of Git.

The implementation required approximately:
- **3,198 markdown files** unified from two repositories
- **3 repositories** total (1 content, 2 sites)
- **3 GitHub Actions workflows** (1 trigger, 2 deployment)
- **1 Personal Access Token** for cross-repository communication

## Sources

[^1]: [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
[^2]: [GitHub Actions Documentation](https://docs.github.com/en/actions)
[^3]: [GitHub repository_dispatch Event](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
[^4]: [GitHub CLI Manual](https://cli.github.com/manual/)

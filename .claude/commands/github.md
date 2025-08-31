---
description: Commit changes with descriptive message and push to GitHub
---

I'll commit all changes, create a descriptive commit message, and push to GitHub. Let me check the current status and create an appropriate commit.

First, let me check what changes are staged and ready to commit:

```bash
git status
git diff --cached
git diff
```

Then I'll add any untracked files that should be committed and create a comprehensive commit message based on the changes:

```bash
git add .
git commit -m "$(cat <<'EOF'
$ARGUMENTS

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push
```

The commit message will be based on your arguments, or if no arguments are provided, I'll analyze the changes and create a descriptive message automatically.

$ARGUMENTS
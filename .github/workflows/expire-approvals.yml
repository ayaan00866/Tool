name: Expire approvals

on:
  schedule:
    - cron: "5 * * * *"
  push:
    paths:
      - "aproval.txt"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: expire-approvals
  cancel-in-progress: false

jobs:
  tidy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Stamp dates and remove expired lines
        run: |
          python3 "$(find . -name expire_approvals.py -not -path './.git/*' | head -n 1)"

      - name: Commit changes
        run: |
          if [ -n "$(git status --porcelain aproval.txt)" ]; then
            git config user.name "approval-bot"
            git config user.email "approval-bot@users.noreply.github.com"
            git add aproval.txt
            git commit -m "approval-bot: update approvals"
            git push
          else
            echo "Nothing to commit"
          fi

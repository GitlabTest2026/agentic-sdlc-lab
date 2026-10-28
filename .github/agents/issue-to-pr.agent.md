## State protocol
- First action: read docs/agent-state/.md. If it does not exist, create it from the template.
- Verify the file against `git log --oneline -5` and the unit tests before continuing. The branch wins.
- After every step: tick the step, set last_commit and heartbeat, run the unit tests, commit.
- Never record secrets, tokens or pasted source code in the state file.
- If you cannot continue, set status: blocked and write the question under Open questions.

# Security

claude-kit runs a shell script on every Claude Code status line refresh and edits `~/.claude/settings.json`, so a flaw here runs with your user's rights. Please report a vulnerability privately through GitHub's "Report a vulnerability" button on the Security tab, not in a public issue.

What the kit runs, and when, is described in [How it works](docs/explanation/how-it-works.md). The status line reads only the JSON Claude Code sends, git state, and the transcript of the current session, and it calls no network service other than `gh` for the state of a pull request the session linked.

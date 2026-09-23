# GitHub CLI across Windows and WSL

Use the available authenticated executable. On Windows, discover `gh` with `Get-Command gh`;
quote an absolute path with spaces and invoke it with PowerShell's call operator `&`.

OpenCode on this installation runs in WSL while GitHub CLI is installed on Windows. Check
`command -v gh.exe`; if absent, test the actual Windows installation path, commonly
`/mnt/c/Program Files/GitHub CLI/gh.exe`. Quote it, for example:

```bash
"/mnt/c/Program Files/GitHub CLI/gh.exe" --version
"/mnt/c/Program Files/GitHub CLI/gh.exe" auth status --hostname github.com
```

The path is a candidate, not a guarantee. Discover a different install location if needed.
Prefer this existing Windows authentication over installing Linux gh or copying credentials.
Keep local Git operations on the Git executable that owns the checkout. Windows gh and WSL
git can have different credentials; success with one does not establish push access for the other.

For remote queries, pass `--repo HOST/OWNER/REPO` (or `gh api --hostname HOST`) explicitly so
Windows gh does not need to infer a Linux checkout through its working directory. Substitute
the verified host/repository, never examples. If the Linux cwd is inaccessible to Windows,
run remote-only queries from a Windows-accessible directory with explicit repo arguments.
Avoid `gh pr checkout` or commands that implicitly mutate local Git across that boundary.

Windows executables receive arguments without Linux-to-Windows path conversion. For an approved
PR body, either convert a Windows-accessible file path with `wslpath -w` or use stdin:

```bash
"$gh_bin" pr create --repo "$repo" --head "$head" --base "$base" \
  --title "$title" --body-file - < "$body_file"
```

This is a publication command, only after the gate in SKILL.md and an approved explicit push.
Variables represent previously verified values, not shell fragments. Use process arguments,
never `eval`, and do not put Markdown into a shell command with interpolated substitutions.
Check interop/auth failures explicitly; never translate them into "no PRs" or retry by exposing
tokens. Do not alter PATH, credential helpers or global configuration just to work around them.

References (consult current help for version-specific details):
- [GitHub CLI PR creation](https://cli.github.com/manual/gh_pr_create)
- [GitHub CLI environment and repository selection](https://cli.github.com/manual/gh_help_environment)
- [Microsoft WSL interoperability and paths](https://learn.microsoft.com/en-us/windows/wsl/filesystems#run-windows-tools-from-linux)

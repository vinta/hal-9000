#!/usr/bin/env python3
"""Fast-forward the default branch from origin in the repo at argv[1], or in every
repo directly inside it when it is a plain folder, then rebase the branch checked
out at argv[2] onto origin's default branch.
Prints STOP and exits 1 whenever the rebase needs a human decision."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NoReturn


def stop(reason: str) -> NoReturn:
    print(f"STOP {reason}")
    sys.exit(1)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)  # noqa: S603 S607 PLW1510 subprocess-without-shell-equals-true start-process-with-partial-path subprocess-run-without-check


def out(repo: Path, *args: str) -> str:
    return git(repo, *args).stdout.strip()


def default_branch(repo: Path) -> str:
    r = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    return r.stdout.strip().removeprefix("origin/") if r.returncode == 0 else "main"


def main_checkouts(path: Path) -> list[Path]:
    if (path / ".git").exists():
        # A worktree shares the main checkout's branches, so sync those there.
        return [Path(out(path, "rev-parse", "--path-format=absolute", "--git-common-dir")).parent]
    # A worktree's .git is a file; its main checkout is synced on its own.
    return sorted(p for p in path.iterdir() if (p / ".git").is_dir())


def sync_default_branches(path: Path) -> bool:
    print("== default branches")
    all_ok = True
    for repo in main_checkouts(path):
        branch = default_branch(repo)
        current = out(repo, "branch", "--show-current")
        r = git(repo, "pull", "--ff-only", "-q") if current == branch else git(repo, "fetch", "-q", "origin", f"{branch}:{branch}")
        ok = r.returncode == 0
        all_ok &= ok
        tip = out(repo, "log", "--oneline", "-1", branch)
        print(f"{repo.name:<30} {'ok' if ok else 'FAIL':<4} {branch} (checkout on {current or 'detached'}) {tip}")
        if not ok:
            print("    " + (r.stderr or r.stdout).strip().splitlines()[-1])
    return all_ok


def adopt_upstream(top: Path, branch: str, upstream_base: str) -> None:
    upstream = out(top, "rev-parse", "--abbrev-ref", "@{u}")

    # Branch commits on each side with no equal patch on the other; main's commits don't count.
    def unique(side: str) -> list[str]:
        return out(top, "rev-list", "--cherry-pick", side, "--no-merges", "HEAD...@{u}", f"^{upstream_base}").split()

    remote_only = unique("--right-only")
    if remote_only:
        print(out(top, "log", "--oneline", "--no-walk", *remote_only))
        stop(f"{upstream} has {len(remote_only)} commits {branch} lacks")
    # The remote is already this branch rebased onto main (pushed from elsewhere): adopt it.
    on_main = git(top, "merge-base", "--is-ancestor", upstream_base, "@{u}").returncode == 0
    if not unique("--left-only") and on_main and out(top, "rev-parse", "HEAD") != out(top, "rev-parse", "@{u}"):
        old = out(top, "rev-parse", "--short", "HEAD")
        if git(top, "rebase", "-q", "@{u}").returncode:
            git(top, "rebase", "--abort")
            stop(f"rebase onto {upstream} failed; {branch} is back at {old}")
        print(f"{upstream} already held {branch} rebased onto {upstream_base}: moved {branch} from {old} to it")


def rebase_onto_default(target: Path) -> None:
    print(f"== branch at {target}")
    r = git(target, "rev-parse", "--show-toplevel")
    if r.returncode:
        print("not a git checkout: nothing to rebase")
        return
    top = Path(r.stdout.strip())
    base_branch = default_branch(top)
    upstream_base = f"origin/{base_branch}"
    branch = out(top, "branch", "--show-current")
    if not branch or branch == base_branch:
        print(f"on {branch or 'detached HEAD'}: nothing to rebase")
        return

    if git(top, "fetch", "-q", "origin").returncode:
        stop(f"git fetch origin failed in {top}")
    dirty = out(top, "status", "--porcelain")
    if dirty:
        print(dirty)
        stop(f"uncommitted changes in {top}")
    if git(top, "rev-parse", "-q", "--verify", "@{u}").returncode == 0:
        adopt_upstream(top, branch, upstream_base)
    merges = out(top, "log", "--oneline", "--merges", f"{upstream_base}..HEAD")
    if merges:
        print(merges)
        stop(f"merge commits in {branch}: a rebase would flatten them")

    base = out(top, "rev-parse", "--short", upstream_base)
    if git(top, "merge-base", "--is-ancestor", upstream_base, "HEAD").returncode == 0:
        print(f"{branch} already sits on {upstream_base} {base}")
        return

    old = out(top, "rev-parse", "--short", "HEAD")
    if git(top, "rebase", "-q", upstream_base).returncode:
        conflicts = out(top, "diff", "--name-only", "--diff-filter=U")
        git(top, "rebase", "--abort")
        print(conflicts)
        stop(f"conflict rebasing {branch} onto {upstream_base} {base}; rebase aborted, {branch} is back at {old}")

    # With no overlap between the branch and main, the rebase changes the tree by exactly main's new commits.
    if out(top, "diff", old, "HEAD") == out(top, "diff", f"{old}...{upstream_base}"):
        check = f"tree changed by exactly {upstream_base}'s new commits"
    else:
        check = f"tree change differs from {upstream_base}'s new commits (branch and main touch the same files): review git diff {old} HEAD"
    print(f"rebased {branch} onto {upstream_base} {base}: old tip {old}, new tip {out(top, 'rev-parse', '--short', 'HEAD')}; {check}")
    print(out(top, "status", "-sb").splitlines()[0])


def main() -> int:
    sync_path, branch_path = map(Path, sys.argv[1:3])
    ok = sync_default_branches(sync_path)
    rebase_onto_default(branch_path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

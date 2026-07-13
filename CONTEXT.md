# HAL 9000 Dotfile Management

Manages files under `~` from a single manifest (`dotfiles/hal_dotfiles.json`). Three concepts differ only in direction and in which side holds the truth.

## Language

**Manifest**:
The single JSON file declaring every managed entry, grouped by kind (`links`, `copies`, `backups`). Each entry has a `src` (what the forward operation reads) and a `dest` (what it writes).
_Avoid_: Config, dotfiles.json

**Link**:
A file whose truth lives in the repo and appears in `~` as a symlink. Editing the file in `~` edits the repo.
_Avoid_: Symlink entry

**Copy**:
A file whose truth lives in the repo and is materialized into `~` as an independent file, used where a symlink can't work or isn't wanted. Local edits are overwritten on the next sync.
_Avoid_: One-way sync

**Backup**:
Live data in `~` whose truth stays in `~`, additively copied out to a backup destination (Dropbox) for safekeeping. A backup never deletes anything at the destination.
_Avoid_: Copy, archive, mirror

**Sync**:
Reconciling the manifest to disk for repo-owned entries: all links and copies, repo → home. Never touches backups.
_Avoid_: Update (that's the Ansible command)

**Restore**:
The reverse of backup: destination → home, overwriting local files after confirmation. The only operation that runs against an entry's declared direction.
_Avoid_: Rollback, recover

# Final demo checks

- Video: 2:15, H.264/AAC, no subtitles. Full decode passed; billing frame is readable; transcription covers the approved script. AI narration is disclosed beside the video.
- Login: admin / admin passed in the running browser. `create_demo_user` creates a regular user only in DEBUG mode and preserves conflicting existing accounts.
- Code: 181 tests and Ruff passed. The final full suite includes the readable JSON export change. Django checks and migration-drift checks passed.
- Export: actual browser export parsed successfully and retained the outage Human Review decision. Original five displayed records are unchanged.
- New inference: none. Ten speech calls and one transcription check use the existing provisional $1 allowance; actual billing is unknown.

The recording reuses the authentic submission capture and four saved results. It does not imply another live model run. Private keys, browser sessions and database backups are excluded.

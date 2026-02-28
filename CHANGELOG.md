# Changelog

## 5.0.0

Release scope: changes from `main` to `codex_revamp`.

### Added

- Config-driven non-GUI mode using `[STARTUP] usegui = False`.
- Headless terminal UX for:
  - required `[USERINPUT]` prompts when no default is provided
  - `YESNO` confirmation prompts
  - `MSGBOX` messages with pause-for-acknowledgement
  - `POPLIST` numbered selections from inline lists or files
- Headless preflight summary showing config, mode, active options, resolved defaults, and expected prompts before execution begins.
- `--liveviewlog` for non-GUI runs so log output streams to the terminal while still writing the normal log file.
- `[IF][THEN][ELSE]` Tarpl support with simple condition evaluation.
- Optional final GUI error popup controlled by `[STARTUP] displayfinalerrors = True`, with a scrollable dialog limited to the first 3 logged errors.
- Example extensive test profiles split into:
  - `example-ini-files/extensive_functionality_test_gui.ini`
  - `example-ini-files/extensive_functionality_test_headless.ini`
- Cross-platform one-file PyInstaller build scripts:
  - `useful_scripts/build_pyinstaller_windows.bat`
  - `useful_scripts/build_pyinstaller_macos.sh`
  - `useful_scripts/build_pyinstaller_linux.sh`
- `requirements-build.txt` for packaging dependencies.
- Expanded automated tests for config parsing, headless flow, Tarpl behavior, task file handling, and utility helpers.
- GitHub Actions test workflow.

### Changed

- GUI layout refreshed while keeping the existing two-column structure and popup options workflow.
- Progress panel redesigned to better balance branding, status, progress, and action controls.
- Options popup styling and spacing improved.
- `README.md` substantially expanded and clarified for startup settings, headless mode, Tarpl usage, packaging, and examples.
- Startup config handling now supports optional GUI-only keys when running headless.
- Installer branding now supports configurable PNG/ICO app icons.

### Fixed

- Linux `[FILES]` token expansion behavior.
- GUI thread-safety issues during status/progress updates.
- `[MODIFY]` add operations so existing-file `{ADD}` entries no longer fail and correctly expand tokens/returnvars.
- Headless option dependency propagation for `ALSOCHECKOPTION`.
- Sample callback behavior so headless-compatible examples no longer depend on Tk dialogs.
- PyInstaller asset path handling in generated build scripts.
- PyInstaller launcher selection in build scripts to prefer `python` and fall back to `python3`.
- Logging so subprocess stdout/stderr is captured more clearly.
- Whitespace handling in file modification logic.

### Examples and Test Profiles

- Added intentional test-error options in the extensive example INIs to exercise final error reporting.
- Added richer GUI and headless example coverage for defaults, prompts, options, `POPLIST`, `YESNO`, `MSGBOX`, `IFGOTO`, and `[IF][THEN][ELSE]`.

### Internal and Project Maintenance

- Version updated to `5.0.0`.
- `.gitignore` improved for logs, caches, and local metadata.
- macOS metadata files are ignored.
- Workspace/run configuration updated during active development.

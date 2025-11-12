# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

## [0.9.10] - 2025-10-04

### Added

- `--totalhelp` switch added to list all help

## [0.9.9] - 2025-09-29

### Fixed

- Gitlab library included

### Added

- `autogit` command and switches

## [0.9.8] - 2025-09-04

### Fixed

- Wrong bash return value for `detect-uncompiled`
- Fixed other ad hoc return values

### Added

- `check-pins` to attempt to upgrade `include:` elements to latest hash or git tag.

## [0.9.7] - 2025-09-01

### Fixed

- Fix performance with lazy loading, rtoml.
- Fix performance and caching logic for update checker.

## [0.9.6] - 2025-09-01

### Fixed

- json schema loaded from cache, then URL, then resource. Won't start using resource until there is some staleness logic.
- Prime cache before attempting to validate on multiple threads

## [0.9.5] - 2025-08-28

### Fixed

- Backwards compatibility for 3.8, etc


## [0.9.4] - 2025-08-28

### Added
- New validate command to validate yaml against json schema. Previously you had to compile to validate.

### Changed
- New dependency on orjson, urllib3 for speed. Tomli for backwards compatibility.

## [0.9.3] - 2025-08-27

### Fixed
- Detect drift failed on arg parse. Validated with more comprehensive basic_check.sh test.

## [0.9.2] - 2025-08-23

### Fixed

- Bash style error handling in CLI code with sys.exit + numeric error code, python exceptions everywhere else.
- Better error reporting when running gui/tui/interactive without installing `[all]`

## [0.9.1] - 2025-08-22

### Fixed

- Core mode less likely to fail in import errors. Install help is now vertically more compact.
- `doctor` command should be fixed now.

## [0.9.0] - 2025-08-22

### Changed

- Installation is `bash2gitlab` for core in the CI/build server or `bash2gitlab[all]` for all commands on your laptop.
  this will mitigate against supply chain risks as the core has very, very few 3rd party packages.

### Added

- CLI option for `bash2gitlab run --in-file .gitlab-ci.yml` for best efforts to run a pipeline locally. This is not a
  real runner!

## [0.8.22] - 2025-08-21

### Changed

- Map deploy writes to multiple folders.
- Map commit gathers multiple folders. Does not handle conflicts yet.

### Added

- Best effort local runner will attempt to run a `.gitlab-ci.yml`, obviously without many, many feature.

## [0.8.21] - 2025-08-20

### Added

- `# Pragma: do-not-validate-schema` for `!reference` code. Gitlab merges all templates before json validation.

## [0.8.20] - 2025-08-20

### Fixed

- Fixed regression where stages were turned into string blocks.

### Added

- Now validates yaml against Gitlab's Json Schema. No flag to ignore validation results.

## [0.8.19] - 2025-08-19

### Fixed

- Fixed regression where scripts were quoted lists again. Added a lot of unit tests.

### Added

- Compile will skip if no changes have been made since last compile to any file in the input folder.

## [0.8.18] - 2025-08-19

### Fixed

- Fix for variable lists turning into a string block/`!reference` turning into a plain list.

## [0.8.17] - 2025-08-17

### Fixed

- Graph failed to retry other renderers
- Graph failed on utf-8 error
- Color logging not useful in GUI/TUI Popen calls
- Lint didn't get gitlab_url from config
- Fix `Pragma` feature
- Fix tkinter to change tab when command run

## [0.8.16] - 2025-08-17

### Changed

- Documentation, docstrings, help text
- Init now covers all the config option.

## [0.8.15] - 2025-08-16

### Added

- Interactive mode via bash2gitlab-interactive command
- GUI via bash2gitlab-gui command

### Changed

- `shred` renamed to decompile.
- Config updates to support storing almost all command options in config file
- Inline supports Pragma commands to skip certain bash from being in-lined.
    - `# Pragma: do-not-inline`: Prevents inlining on the current line.
    - `# Pragma: do-not-inline-next-line`: Prevents inlining on the next line.
    - `# Pragma: start-do-not-inline`: Starts a block where no inlining occurs.
    - `# Pragma: end-do-not-inline`: Ends the block.
    - `# Pragma: allow-outside-root`: Bypasses the directory traversal security check.

## [0.8.14] - 2025-08-16

### Added

- Basc textual TUI added to mirror the CLI interface
- Generates makefile for decompile command

## [0.8.13] - 2025-08-15

### Fixed

- decompile command had wrong CLI argument validation

### Changed

- `graph` command will attempt other graphing styles if graphviz not available.

## [0.8.12] - 2025-08-14

### Added

- Graph command
- Doctor command for diagnostics
- Show config command to show how cascading config resolves

### Fixed

- decompile write to a folder now.
- decompile will take --in-file or --in-folder
- decompile records `!reference [.job, key]` as bash comment
- decompile now logs with relative path.
- decompile should now use path relative to yaml not cwd
- Leading `.` got stripped from file names. Fixed

## [0.8.11] - 2025-08-14

### Added

- Install/uninstall git precommit hooks to compile before commit (not integrated with the popular pre-commit tool).
  Support for
  integration with the `pre-commit` tool is on the way.
- Pluggy support for plugins

### Changed

- Now support inlining a much larger list of script languages using variations on `interpreter -c "..."`

## [0.8.10] - 2025-08-11

### Fixed

- Minimize all "script as yaml lists" because they are not compatible with line continuation characters. No one should
  use any version of bash2gitlab before 0.8.10.

## [0.8.9] - 2025-08-11

### Fixed

- Lost all new lines.

## [0.8.8] - 2025-08-11

### Added

- Support for inlining other languages, python, etc. using `python -c`, etc.

### Fixed

- Force new line at the end of any script.
- Minimize bash written in `- code` lists because of risk of quoting problems.
- Quote strings more aggressively

## [0.8.7] - 2025-08-10

### Changed

- File invocations followed by comment are now detected.
- Concept of script folder and template folder gone. Input folder and output folder is enough.

### Removed

- Global variable file feature is broken, will need to rethink

### Added

- Clean command that only removes unmodified files from output folder
- Checks for stray files in output folder before compiling
- Lint command, but it is in "beta" testing

### Fixed

- No longer rewrites files even when there are no changes

## [0.8.6] - 2025-08-09

### Changed

- Map deploy and map commit now restricted to .sh, .ps1 and .y\[a\]ml files.

### Added

- Map commit CLI available.
- Suggestions on incorrect cli command

## [0.8.5] - 2025-08-08

### Changed

- Discourage excessive quotes

### Fixed

- Gracefully degrade if someone changes generated yaml to invalid yaml.

### Added

- Map deploy started.

## [0.8.4] - 2025-08-06

### Added

- Shows command used to generate in the header
- Added "detect-drift" command, to complement the existing drift detection that runs at compile time.

### Fixed

- Bug that stringified certain complex values in yaml maps.

## [0.8.3] - 2025-08-05

### Added

- Basic ps1 file support

### Fixed

- Fixed bug with copy2local

## [0.8.2] - 2025-08-05

### Added

- Checks for updated package from pypi.

### Changed

- copy2local now copies the contents of src folder to destination folder, to reduce nesting.

## [0.8.1] - 2025-08-05

### Added

- Improve logging

## [0.8.0] - 2025-08-04

### Added

- Inlines bash by same logic as inlining bash into yaml. Looks for `source script.sh` and inlines it.

### Changed

- clone2local is now copy2local using archive and copy commands to get a part of your remote repo into a dependent
  report for testing.

### Fixed

- Reference or multiple scripts in a script list would all be stomped by last script.

## [0.7.0] - 2025-08-02

### Added

- Started work on a clone feature to get scripts into dependent repos for testing. Not fully baked yet.

### Removed

- A `--format` option was a bad idea because all of the major yaml formatting tools are in various states of
  unsupportedness and cause failures unrelated to bash2gitlab's outputs. Use your favorite orchestration tool, such as
  make or just to format with a yaml formatter that works for you.

## [0.6.0] - 2025-07-30

### Changed

- Hash is now a bash64 encode of whole yaml document so reformats with more than just whitespace changes can be detected
  correctly

### Fixed

- Loosely detect anchors (assumes all hashes with a list value and ./script.sh pattern are script anchors)
- Detects jobs with only before_script or after_script

## [0.5.1] - 2025-07-30

### Fixed

- Preserve long lines
- Remove leading blank lines from scripts to avoid indentation indicators (e.g. `|2-`)

## [0.5.0] - 2025-07-29

### Fixed

- Subfolders with yaml files are now processed

### Added

- Started a feature to detect modification, currently warns and doesn't stop.

## [0.4.1] - 2025-07-27

### Fixed

- Command line aliases are now bash2gitlab and b2gl. Previously had some copy-paste junk.

## [0.4.0] - 2025-07-27

### Added

- Watch mode (--watch) to recompile on file changes
- decompile supports job-level variables
- decompile automatically includes if-block to include job level and global variables.
- decompile generates mock CI variables file
- init command to generate config file

## [0.3.0] - 2025-07-27

### Added

- Option to use toml config file or envvar config instead of CLI switches

### Fixed

- Python 3.14 support fixed.

## [0.2.0] - 2025-07-27

### Added

- decompile command to turn pre-existing bash-in-yaml pipeline templates into shell files and yaml

## [0.1.0] - 2025-07-26

### Added

- compile command exists
- verbose and quiet logging
- CLI interface
- supports simple in/out project structure
- supports corralling scripts and templates into a scripts or templates folder, which confuses path resolution 
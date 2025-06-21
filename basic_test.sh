#❯ bug_trail --help
#usage: bug_trail [-h] [--clear] [--config CONFIG] [--version] [--verbose] [--watch]
#
#Tool for local logging and error reporting.
#
#options:
#  -h, --help       show this help message and exit
#  --clear          Clear the database and log files
#  --config CONFIG  Path to the configuration file
#  --version        show program's version number and exit
#  --verbose        verbose output
#  --watch          watch database, generate continuously
set -e
bug_trail
bug_trail --verbose
bug_trail --version
# everything else does something


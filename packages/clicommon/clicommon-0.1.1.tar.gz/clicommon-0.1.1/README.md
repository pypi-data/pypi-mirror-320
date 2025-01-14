# clicommon

Python Common Client Library

## Common Functions

### bcheck

    Checks variabled passwed defined a true or false, not defined is considered false
    bcheck(variable) -> bool

### mlog

  General logging function
  mlog(msg_type, msg_string = None, exit_code = None, datelog = None, colors = None):

  msg_type with corresponding Colors (if colors flat is True)
    INFO=GREEN
    SUCCESS=GREEN
    WARN=YELLOW
    WARNING=YELLOW
    FATAL=RED
    ERROR=RED
    CRITICAL=RED
    TEST=GRAY
    DEBUG=MAGENTA
    VERBOSE=BRIGHT_CYAN
    BUILD_DEBUG=BRIGHT_GREEN
    CODE_DEBUG=BRIGHT_GREEN

  msg_string (anything)
    NOTE: If msg_string is not defined msg_type is considered the msg_string

  exit_code if boolean is true after output exit

  datelog if boolean is true add ISO8601 datetime to output

  colors if boolean is true add ASCII colors to output bsaed on msg_type color codes

### rcmd

  Small function to run command sub process and return results
  rcmd (command)

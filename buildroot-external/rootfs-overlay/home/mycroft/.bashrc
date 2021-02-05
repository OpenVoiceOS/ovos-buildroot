export TERM=xterm-xfree86

PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\] '

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

alias ll='ls -la'

######################################################################
# Initialize OpenVoiceOS CLI Environment
######################################################################
source cli_login.sh

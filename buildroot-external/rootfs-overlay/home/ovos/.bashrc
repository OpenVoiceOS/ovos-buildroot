PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\] '

alias ll='ls -la'
alias ovos-cli-client='podman exec --interactive --tty ovos_cli ovos-cli-client'
alias ovos-config='podman exec --interactive --tty ovos_cli ovos-config'
alias ovos-speak='podman exec --interactive --tty ovos_cli ovos-speak'
alias ovos-log-watch='journalctl --user-unit=ovos_* -f'
alias mana='podman exec --interactive --tty ovos_cli mana'

######################################################################
# Initialize OpenVoiceOS CLI Environment
######################################################################
source cli_login.sh

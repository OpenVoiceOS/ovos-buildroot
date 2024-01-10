PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\] '

alias ll='ls -la'
alias ovos-cli-client='podman exec --interactive --tty ovos-cli ovos-cli-client'
alias ovos-simple-cli='podman exec --interactive --tty ovos-cli ovos-simple-cli'
alias ovos-config='podman exec --interactive --tty ovos-cli ovos-config'
alias ovos-speak='podman exec --interactive --tty ovos-cli ovos-speak'
alias ovos-listen='podman exec --interactive --tty ovos-cli ovos-listen'
alias ovos-say-to='podman exec --interactive --tty ovos-cli ovos-say-to'
alias ovos-log-watch='journalctl --user-unit=ovos_* -f'
alias mana='podman exec --interactive --tty ovos-cli mana'

######################################################################
# Initialize OpenVoiceOS CLI Environment
######################################################################
source cli_login.sh

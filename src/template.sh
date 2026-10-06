#!/usr/bin/env bash
# ---------------------------------------------------------------------------------------- #
# Description                                                                              #
# ---------------------------------------------------------------------------------------- #
# A simple script which will implement asn level blocking via TCP Wrappers. The script     #
# uses whois to identify the ASN for the given IP range. It will then use the default      #
# 'ACTION' to decide wether to deny or approve the connection.                             #
#                                                                                          #
# Action:                                                                                  #
#     ALLOW: Only allow connections from specified ASNs.                                   #
#     DENY: Deny all connections from specified ASNs.                                      #
# ---------------------------------------------------------------------------------------- #
# TCP Wrapper config:                                                                      #
#                                                                                          #
# /etc/hosts.allow                                                                         #
#      sshd: ALL: aclexec /usr/sbin/asn-filter %a                                          #
#                                                                                          #
# /etc/hosts.deny                                                                          #
#      sshd: ALL                                                                           #
# ---------------------------------------------------------------------------------------- #

# Template version. Printed by --version and included in deny logs.
VERSION='0.1.1'

ALLOW_ACTION='ALLOW'
DENY_ACTION='DENY'

# Space-separated or comma-separated values matched as whole tokens.
BAN_LIST=''

# Allow or Deny countries listed
ACTION=$DENY_ACTION

# ---------------------------------------------------------------------------------------- #
# In multiplexer                                                                           #
# ---------------------------------------------------------------------------------------- #
# A simple wrapper to check if the script is being run via the multiplex or not.           #
# ---------------------------------------------------------------------------------------- #

function in_multiplexer
{
    [[ "${MUX}" = true ]] && return 0 || return 1;
}

# ---------------------------------------------------------------------------------------- #
# In terminal                                                                              #
# ---------------------------------------------------------------------------------------- #
# A simple wrapper to check if the script is being run in a terminal or not.               #
# ---------------------------------------------------------------------------------------- #

function in_terminal
{
    [[ -t 1 ]] && return 0 || return 1;
}

# ---------------------------------------------------------------------------------------- #
# Debug                                                                                    #
# ---------------------------------------------------------------------------------------- #
# Show output only if we are running in a terminal.                                        #
# ---------------------------------------------------------------------------------------- #

function debug()
{
    local message="${1:-}"

    if [[ -n "${message}" ]]; then
        if in_terminal || in_multiplexer; then
            echo "${message}"
        fi
        logger "${message}"
    fi
}

# ---------------------------------------------------------------------------------------- #
# Is listed                                                                                #
# ---------------------------------------------------------------------------------------- #
# True when item is one whole token in the list. AS64 does not match AS64496.              #
# ---------------------------------------------------------------------------------------- #

function is_listed()
{
    local item="${1:-}"
    local list="${2:-}"
    local token
    local -a tokens=()

    shopt -s nocasematch
    IFS=$' \t\n,' read -ra tokens <<< "${list}"
    for token in "${tokens[@]}"; do
        if [[ -n "${token}" && "${token}" == "${item}" ]]; then
            return 0
        fi
    done
    return 1
}

# ---------------------------------------------------------------------------------------- #
# Check results                                                                            #
# ---------------------------------------------------------------------------------------- #
# A wrapper to check individual results against a given array and deny as required.        #
# ---------------------------------------------------------------------------------------- #

function check_results()
{
    local item="${1:-}"
    local list="${2:-}"

    #
    # Check the current item and list and decide what action to take
    #
    if [[ "${ACTION}" == 'DENY' ]]; then
        is_listed "${item}" "${list}" && RESPONSE=${DENY_ACTION} || RESPONSE=${ALLOW_ACTION}
    else
        is_listed "${item}" "${list}" && RESPONSE=${ALLOW_ACTION} || RESPONSE=${DENY_ACTION}
    fi

    if [[ $RESPONSE = "${DENY_ACTION}" ]]; then
        debug "$RESPONSE sshd connection from ${IP} ($item) version ${VERSION}"
        exit 1
    fi

    #
    # Default (REPONSE=ALLOW) is to do nothing
    #
}

# ---------------------------------------------------------------------------------------- #
# Handle blocks                                                                            #
# ---------------------------------------------------------------------------------------- #
# A wrapper which looks up the 'thing' and checks to see if it is on the ban list.         #
# ---------------------------------------------------------------------------------------- #
function handle_blocks
{
    local test_item="item1"

    check_results "${test_item}" "${BAN_LIST}"
}

# ---------------------------------------------------------------------------------------- #
# Main()                                                                                   #
# ---------------------------------------------------------------------------------------- #
# The main function where all of the heavy lifting and script config is done.              #
# ---------------------------------------------------------------------------------------- #

function main()
{
    #
    # Version, so a copied filter can be identified.
    #
    if [[ "${1:-}" == "--version" || "${1:-}" == "-V" ]]; then
        echo "tcp-wrapper-template ${VERSION}"
        exit 0
    fi

    #
    # NO IP given - error and abort
    #
    if [[ -z "${1}" ]]; then
        debug 'Ip addressed not supplied - Aborting'
        exit 0
    fi

    #
    # Set a variable (Could pass it at function call)
    #
    declare -g IP="${1}"

    #
    # Are we being called from the multiplexer?
    #
    if [[ -n "${2}" ]]; then
        declare -g MUX=true
    else
        declare -g MUX=false
    fi

    #
    # Turn off case sensitivity
    #
    shopt -s nocasematch

    #
    # Blocking
    #
    handle_blocks

    # Default allow
    exit 0
}

# ---------------------------------------------------------------------------------------- #
# Main()                                                                                   #
# ---------------------------------------------------------------------------------------- #
# The actual 'script' and the functions/sub routines are called in order.                  #
# ---------------------------------------------------------------------------------------- #

main "${@}"

# ---------------------------------------------------------------------------------------- #
# End of Script                                                                            #
# ---------------------------------------------------------------------------------------- #
# This is the end - nothing more to see here.                                              #
# ---------------------------------------------------------------------------------------- #

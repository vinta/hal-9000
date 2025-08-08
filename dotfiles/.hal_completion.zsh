#compdef hal

_hal() {
    local -a commands

    # Commands extracted from hal script
    commands=(
        'update:pull the repo and run ansible-playbook'
        'link:add the file to the dotfiles repository'
        'copy:copy the file to the dotfiles repository'
        'sync:force sync dotfiles'
        'open-the-pod-bay-doors:open the pod bay doors, please, HAL'
    )

    if (( CURRENT == 2 )); then
        # First argument - show commands and options
        _describe -t commands 'hal commands' commands
        _arguments \
            '(-h --help)'{-h,--help}'[show help message]' \
            '(-v --version)'{-v,--version}'[show version]'
    else
        # Additional arguments based on command
        case "$words[2]" in
            link|copy)
                _files
                ;;
            *)
                # No special completion for other commands
                ;;
        esac
    fi
}

compdef _hal hal
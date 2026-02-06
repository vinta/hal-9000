#compdef hal

_hal() {
    local -a commands

    # Commands extracted from hal script
    commands=(
        'update:pull repo and run ansible-playbook'
        'link:move file into dotfiles and symlink it back'
        'unlink:restore file from dotfiles and remove symlink'
        'copy:copy file into dotfiles (no symlink)'
        'backup:backup arbitrary src to arbitrary dest'
        'sync:sync all links, copies, and backups'
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
            link|unlink|copy)
                _files
                ;;
            *)
                # No special completion for other commands
                ;;
        esac
    fi
}

compdef _hal hal
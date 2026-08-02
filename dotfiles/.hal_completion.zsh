#compdef hal

_hal() {
    local -a commands

    commands=(
        'update:pull repo and run ansible-playbook (extra args pass through, e.g. --tags python,node)'
        'link:move file into dotfiles and symlink it back'
        'unlink:move file back from dotfiles and remove symlink'
        'copy:copy file into dotfiles (no symlink)'
        'sync:sync all links and copies'
        'backup:back up all backup entries to their destinations'
        'restore:restore all backup entries, overwriting local files'
        'open-the-pod-bay-doors:open the pod bay doors, please, HAL'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'hal commands' commands
        _arguments \
            '(-h --help)'{-h,--help}'[show help message]' \
            '(-v --version)'{-v,--version}'[show version]'
    else
        case "$words[2]" in
            link|unlink|copy)
                _files
                ;;
            *)
                ;;
        esac
    fi
}

compdef _hal hal
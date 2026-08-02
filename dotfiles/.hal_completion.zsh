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
        shift words
        (( CURRENT-- ))
        case "$words[1]" in
            update)
                _arguments \
                    '(-h --help)'{-h,--help}'[show this help message and exit]' \
                    '--tags[only run plays and tasks tagged with these values]:tags: ' \
                    '--skip-tags[skip plays and tasks whose tags match these values]:tags: '
                ;;
            link|unlink|copy)
                _arguments \
                    '(-h --help)'{-h,--help}'[show this help message and exit]' \
                    ':filename:_files'
                ;;
            sync)
                _arguments \
                    '(-h --help)'{-h,--help}'[show this help message and exit]' \
                    '--force[replace real directories at link destinations]'
                ;;
            backup|restore|open-the-pod-bay-doors)
                _arguments \
                    '(-h --help)'{-h,--help}'[show this help message and exit]'
                ;;
            *)
                ;;
        esac
    fi
}

compdef _hal hal
#compdef hal

_hal() {
    local -a commands
    local -a options
    
    options=(
        '(-h --help)'{-h,--help}'[show help message]'
        '(-v --version)'{-v,--version}'[show version]'
        '--print-completion[print shell completion script]:shell:(bash zsh tcsh)'
    )
    
    # Commands extracted from hal script
    commands=(
        'update:pull the repo and run ansible-playbook'
        'link:add the file to the dotfiles repository'
        'unlink:remove the file from the dotfiles repository'
        'sync:force sync dotfiles'
        'open-the-pod-bay-doors:open the pod bay doors, please, HAL'
    )
    
    if (( CURRENT == 2 )); then
        _arguments $options
        _describe -t commands 'hal commands' commands
    else
        # Check which commands need filename completion
        case "$words[2]" in
            link|unlink)
                _arguments \
                    '(-h --help)'{-h,--help}'[show help message]' \
                    '*:filename:_files'
                ;;
            *)
                _arguments \
                    '(-h --help)'{-h,--help}'[show help message]'
                ;;
        esac
    fi
}

_hal "$@"

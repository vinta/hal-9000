#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Generating zsh completion..."

# Parse commands from the Python script using grep and sed
echo "Extracting commands from bin/hal..."

# Create the completion file
cat > dotfiles/.hal_completion.zsh << 'EOF'
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
EOF

# Extract subparser definitions and their help text
grep -A1 "subparsers.add_parser" bin/hal | grep -E "(add_parser|help=)" | \
    sed "s/.*add_parser('\([^']*\)'.*help='\([^']*\)'.*/        '\1:\2'/" | \
    sed '/^--$/d' >> dotfiles/.hal_completion.zsh

cat >> dotfiles/.hal_completion.zsh << 'EOF'
    )
    
    if (( CURRENT == 2 )); then
        _arguments $options
        _describe -t commands 'hal commands' commands
    else
        # Check which commands need filename completion
        case "$words[2]" in
EOF

# Find commands that have filename arguments
grep -B2 "add_argument.*filename" bin/hal | grep "add_parser" | \
    sed "s/.*add_parser('\([^']*\)'.*/\1/" | \
    paste -sd '|' - | sed 's/^/            /' >> dotfiles/.hal_completion.zsh

cat >> dotfiles/.hal_completion.zsh << 'EOF'
)
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
EOF

echo "Completion generated: dotfiles/.hal_completion.zsh"
echo "Run 'hal sync' to update your local completion."
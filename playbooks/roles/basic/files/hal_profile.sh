# https://github.com/vinta/hal-9000
export PATH="/usr/local/hal-9000/bin:$PATH"

# Set up zsh completion for hal
if [[ -n "$ZSH_VERSION" ]]; then
    # Ensure .zsh_completions directory exists
    mkdir -p ~/.zsh_completions

    # Copy completion file if it exists
    if [[ -f ~/.hal_completion.zsh ]]; then
        cp ~/.hal_completion.zsh ~/.zsh_completions/_hal
    fi

    # Add to fpath and initialize completions
    fpath=(~/.zsh_completions $fpath)
    autoload -Uz compinit && compinit
fi


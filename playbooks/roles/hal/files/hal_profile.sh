# shellcheck shell=bash disable=SC1090,SC1091

# https://github.com/vinta/hal-9000
export PATH="/usr/local/hal-9000/bin:$PATH"

if [[ -f ~/.hal_completion.zsh ]]; then
  source ~/.hal_completion.zsh
fi

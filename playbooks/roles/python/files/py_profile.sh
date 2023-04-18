# https://github.com/yyuu/pyenv
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi

# https://python-poetry.org/docs/#installation
export PATH="/Users/vinta/.local/bin:$PATH"

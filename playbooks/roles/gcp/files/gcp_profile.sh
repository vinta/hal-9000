if [ -f "$HOME/.google-cloud-sdk/path.zsh.inc" ]; then
  source "$HOME/.google-cloud-sdk/path.zsh.inc"
  # source "$HOME/.google-cloud-sdk/completion.zsh.inc"
fi

if [ -x "$HOME/.google-cloud-sdk-venv/bin/python" ]; then
  export CLOUDSDK_PYTHON="$HOME/.google-cloud-sdk-venv/bin/python"
  export CLOUDSDK_PYTHON_SITEPACKAGES=1
fi

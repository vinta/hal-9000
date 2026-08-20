if [ -f "$HOME/.google-cloud-sdk/path.zsh.inc" ]; then
  source "$HOME/.google-cloud-sdk/path.zsh.inc"
  # source "$HOME/.google-cloud-sdk/completion.zsh.inc"
fi

if [ -x "$HOME/.google-cloud-sdk-venv/bin/python" ]; then
  export CLOUDSDK_PYTHON="$HOME/.google-cloud-sdk-venv/bin/python"
  # Drops the -S that would otherwise hide NumPy from gcloud.
  export CLOUDSDK_PYTHON_SITEPACKAGES=1
fi

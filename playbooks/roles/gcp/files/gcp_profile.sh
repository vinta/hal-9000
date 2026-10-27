if [ -f "$HOME/.google-cloud-sdk/path.zsh.inc" ]; then
  source "$HOME/.google-cloud-sdk/path.zsh.inc"
  # source "$HOME/.google-cloud-sdk/completion.zsh.inc"
fi

if [ -x "$HOME/.config/gcloud/virtenv/bin/python" ]; then
  export CLOUDSDK_PYTHON="$HOME/.config/gcloud/virtenv/bin/python"
  export CLOUDSDK_PYTHON_SITEPACKAGES=1
fi

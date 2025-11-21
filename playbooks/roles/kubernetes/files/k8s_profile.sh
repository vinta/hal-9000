if [ -f "$HOME/.google-cloud-sdk/path.zsh.inc" ]; then
  export USE_GKE_GCLOUD_AUTH_PLUGIN=True
  source "$HOME/.google-cloud-sdk/path.zsh.inc"
  # source "$HOME/.google-cloud-sdk/completion.zsh.inc"
fi

if [ $commands[kubectl] ]; then
  source <(kubectl completion zsh)
fi

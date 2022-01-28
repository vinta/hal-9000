if [ -f "$HOME/vendors/google-cloud-sdk/path.zsh.inc" ]; then
  source "$HOME/vendors/google-cloud-sdk/path.zsh.inc"
  source "$HOME/vendors/google-cloud-sdk/completion.zsh.inc"
fi

if [ $commands[kubectl] ]; then
  source <(kubectl completion zsh)
fi

[ -f "$HOME/.fubectl.source" ] && source "$HOME/.fubectl.source"

autoload -U colors; colors
source ~/vendors/zsh-kubectl-prompt/kubectl.zsh
RPROMPT='%{$fg[blue]%}($ZSH_KUBECTL_PROMPT)%{$reset_color%}'

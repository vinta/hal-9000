if [[ -o login ]]; then
  if [ x"$TERM" != "xscreen" ]; then
    # Indicates start of command output. Runs just before command executes.
    iterm2_before_cmd_executes() {
      printf "\033]133;C;\r\007"
    }

    iterm2_set_user_var() {
      printf "\033]1337;SetUserVar=%s=%s\007" "$1" $(printf "%s" "$2" | base64)
    }

    # Users can write their own version of this method. It should call
    # iterm2_set_user_var but not produce any other output.
    # e.g., iterm2_set_user_var currentDirectory $PWD
    # Accessible in iTerm2 (in a badge now, elsewhere in the future) as
    # \(user.currentDirectory).
    iterm2_print_user_vars() {
    }

    iterm2_print_state_data() {
      printf "\033]1337;RemoteHost=%s@%s\007" "$USER" "$iterm2_hostname"
      printf "\033]1337;CurrentDir=%s\007" "$PWD"
      iterm2_print_user_vars
    }

    # Report return code of command; runs after command finishes but before prompt
    iterm2_after_cmd_executes() {
      printf "\033]133;D;$?\007"
      iterm2_print_state_data
    }

    # Mark start of prompt
    iterm2_prompt_start() {
      printf "\033]133;A\007"
    }

    # Mark end of prompt
    iterm2_prompt_end() {
      printf "\033]133;B\007"
    }

    iterm2_precmd() {
      iterm2_after_cmd_executes

      # The user or another precmd may have changed PS1 (e.g., powerline-shell).
      # Ensure that our escape sequences are added back in.
      if [[ "$ITERM2_SAVED_PS1" != "$PS1" ]]; then
        PS1="%{$(iterm2_prompt_start)%}$PS1%{$(iterm2_prompt_end)%}"
        ITERM2_SAVED_PS1="$PS1"
      fi
    }

    iterm2_preexec() {
      PS1="$ITERM2_SAVED_PS1"
      iterm2_before_cmd_executes
    }

    # If hostname -f is slow on your system, set iterm2_hostname prior to sourcing this script.
    [[ -z "$iterm2_hostname" ]] && iterm2_hostname=`hostname -f`

    [[ -z $precmd_functions ]] && precmd_functions=()
    precmd_functions=($precmd_functions iterm2_precmd)

    [[ -z $preexec_functions ]] && preexec_functions=()
    preexec_functions=($preexec_functions iterm2_preexec)

    iterm2_print_state_data
    printf "\033]1337;ShellIntegrationVersion=1\007"
  fi
fi

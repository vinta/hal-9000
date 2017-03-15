# Path to your oh-my-zsh installation.
export ZSH=/Users/vinta/.oh-my-zsh

fpath=(/usr/local/share/zsh-completions $fpath)

# Set name of the theme to load.
# Look in ~/.oh-my-zsh/themes/
# Optionally, if you set this to "random", it'll load a random theme each
# time that oh-my-zsh is loaded.
ZSH_THEME="gentoo"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
HIST_STAMPS="yyyy-mm-dd"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(docker fasd)

# User configuration

source $ZSH/oh-my-zsh.sh

# You may need to manually set your language environment
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

# export ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=240"
# export ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE="40"
# source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
# source ~/.zsh/zsh-history-substring-search/zsh-history-substring-search.zsh

source ~/.iterm2_shell_integration.zsh

eval $(gdircolors ~/.dircolors-solarized/dircolors.ansi-dark)

eval "$(fasd --init auto)"

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi
export EDITOR='sublime'

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# ssh
# export SSH_KEY_PATH="~/.ssh/dsa_id"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.

# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

alias grep='grep --color=auto'
alias stat='gstat'
alias ls='gls --color=auto'
alias la='ls -AU'
alias ll='ls -lAU'

alias o='a -e open'
alias v='f -e sublime'

alias docker-stopall='docker stop $(docker ps -a -q)'
alias docker-rmall='docker rm $(docker ps -a -q)'
alias docker-rmiall='docker rmi $(docker images -q)'

source ~/Projects/HAL-9000/playbooks/roles/basic/files/hal_profile
source ~/Projects/HAL-9000/playbooks/roles/go/files/gvm_profile
source ~/Projects/HAL-9000/playbooks/roles/node/files/nvm_profile
source ~/Projects/HAL-9000/playbooks/roles/python/files/pyenv_profile

source ~/Projects/dps/playbook/ssh_alias
source ~/Projects/streetvoice-deployment/ssh_alias

if which java > /dev/null; then
  export JAVA_HOME=$(/usr/libexec/java_home -v 1.8);
fi

if which pyspark > /dev/null; then
  export SPARK_HOME="/usr/local/Cellar/apache-spark/2.1.0/libexec"
  export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.4-src.zip:$PYTHONPATH
fi

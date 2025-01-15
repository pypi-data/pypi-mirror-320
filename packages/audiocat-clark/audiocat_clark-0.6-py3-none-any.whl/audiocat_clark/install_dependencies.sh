#!/bin/bash
set -e
set -x
set -o pipefail

sudo $(which apt) update
sudo $(which apt) install minimodem
sudo $(which apt) install gpg
sudo $(which apt) install bc
# --------------------------
# sudo $(which apt) install gnupg
# sudo $(which apt) install termux-api
# sudo $(which apt) install tmux
# sudo $(which apt) install cool-retro-term

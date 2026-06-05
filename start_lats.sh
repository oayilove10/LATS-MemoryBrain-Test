#!/bin/bash

cd ~/LATS_PRODUCTION

gnome-terminal -- bash -c "python3 -m memory_v3.runtime_runner; exec bash"

gnome-terminal -- bash -c "watch -n 30 'tail -n 20 logs/memory_v3/runtime.log'; exec bash"

gnome-terminal -- bash -c "./sync_runtime_backup.sh; exec bash"

gnome-terminal -- bash -c "top; exec bash"

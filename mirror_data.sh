#!/bin/bash

echo "Syncing gtd/..."
rsync -a --delete $HOME/data/gtd/ data_copy/gtd/
echo "Syncing gtd-img/..."
rsync -a --delete $HOME/data/gtd-img/ data_copy/gtd-img/

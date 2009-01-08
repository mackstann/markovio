#!/bin/sh
for i in 1 2 3 4 5
do
    ./markovio.py
    cp /tmp/markovio.out.png outputsample$i.png
done
git add outputsample*.png
git status
msg='new samples'
test -n "$1" && msg="$msg: $1"
git commit -m "$msg"
git push

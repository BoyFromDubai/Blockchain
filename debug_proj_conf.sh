#!/bin/bash
comment=${1:-'.'}

prev_comment=$(cat prev_comment.txt)
if [[$prev_comment -eq $comment]]
then
    comment="${comment} [DEBUG]"
fi


git add .
git commit -m "$comment"
git push

ansible-playbook ini_proj.yml
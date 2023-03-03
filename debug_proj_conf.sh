#!/bin/bash
comment=${1:-'.'}
FILE=prev_comment.txt
if ! test -f "$FILE"
then
    touch $FILE
fi

prev_comment=$(cat prev_comment.txt)

echo $comment > $FILE

if [[ "$prev_comment" == "$comment" ]]
then
    comment="${comment} [DEBUG]"
fi

echo $comment

git add .
git commit -m "$comment"
git push

ansible-playbook ini_proj.yml
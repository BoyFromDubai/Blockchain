comment=${1:-'.'}

git add .
git commit -m "$comment"
git push

ansible-playbook ini_proj.yml
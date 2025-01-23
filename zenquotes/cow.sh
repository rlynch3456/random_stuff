#!bash
cwd=$pwd
cd /Users/lynchr/src_personal/zenquotes
source .venv/bin/activate
python3 zenquotes.py | cowsay -f dragon-and-cow
deactivate
cd $cwd

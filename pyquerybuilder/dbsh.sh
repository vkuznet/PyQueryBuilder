#!/bin/bash

# check and install if neceesary profile files.
if [ ! -f $HOME/.ipython/ipy_profile_dbsh.py ] || [ ! -f $HOME/.ipython/ipythonrc ]; then
cat > /tmp/dbsh_init.py << EOF
#!/usr/bin/env python

import sys, os, shutil

def copyConfig(f):
    if os.path.isfile(f):
       homedir=os.getenv('HOME')+'/.ipython'
       try:
          os.makedirs(homedir)
       except:
          pass
       try:
          print "cp %s %s"%(f,homedir)
          shutil.copy(f,homedir)
       except:
          pass
for dir in sys.path:
    if  os.path.isdir(dir):
        f = dir+"/pyquerybuilder/dbsh/ipy_profile_dbsh.py"
        copyConfig(f)
        f = dir+"/pyquerybuilder/config/ipythonrc"
        copyConfig(f)
        f = dir+"/pyquerybuilder/dbsh/ipy_user_conf.py"
        copyConfig(f)
        f = dir+"/pyquerybuilder/config/map.yaml"
        copyConfig(f)
EOF
   mkdir -p $HOME/.ipython/
   python /tmp/dbsh_init.py
   rm /tmp/dbsh_init.py
fi

ipython -p dbsh

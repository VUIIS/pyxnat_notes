from pyxnat import Interface
import os

# Initially, you should login with your user name, p/w
xnat = Interface(server='masi.vuse.vanderbilt.edu',
                user='user',
                passowrd='password',
                cachedir=os.path.join(os.path.expanduser('~'),'.xnat_store'))
                
# store this in a cfg file and use it from then on so you don't have to publish
# your p/w in source code
xnat_cfg = os.path.join(os.path.expanduser('~'), '.xnat.cfg')
xnat.save_config(xnat_cfg)

xnat = []

xnat = Interface(config=xnat_cfg)


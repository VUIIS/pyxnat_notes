import os
from ConfigParser import ConfigParser

from pyxnat import Interface
from pdb import set_trace

def load_xnat(cfg=os.path.join(os.path.expanduser('~'), '.xnat.cfg')):
    """Initialize and test xnat connection from a previously-stored cfg file
    
    Parameters
    ----------
    cfg: str
        Path to a stored interface configuration
        This is not from Interface.save_config but rather looks like this:
        [xnat]
        user: [your user name]
        password: [your password]
        server: [your xnat server]
        cache: [dir]
        
    Returns
    -------
    A valid Interface object to your XNAT system.
    
    This may throw something from pyxnat.core.errors
    """
    
    cp = ConfigParser()
    with open(cfg) as f:
        cp.readfp(f)
    user = cp.get('xnat', 'user')
    password = cp.get('xnat', 'password')
    server = cp.get('xnat', 'server')
    cachedir = cp.get('xnat', 'cache')
    
    if '~' in cachedir:
        cachedir = os.path.expanduser(cachedir)
    
    xnat = Interface(server=server,
                    user=user,
                    password=password,
                    cachedir=cachedir)
    # Because the constructor doesn't test the connection, make sure 'admin' is 
    # in the list of users. Any errors are passed to the caller.
    if user not in xnat.manage.users():
        raise ValueError('This XNAT is weird.')
    return xnat
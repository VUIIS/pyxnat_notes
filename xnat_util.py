import os
from ConfigParser import ConfigParser

from pyxnat import Interface

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

    This may throw an error from pyxnat.core.errors
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
    
def subject(project, name, demo={}):
    """ Create a new subject/Update subject info
    
    WARNING: Previously stored data will be overwritten

    Parameters
    ----------
    project: pyxnat.Interface.project()
        An established project
    name: str
        Subject identifier
    demo: dict
        Demographic data to set in xnat
        See 'xnat:subjectData' at
        http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts
        for allowed keys

    Returns
    -------
    sub: a valid subject object
    """
    if not project.exists():
        raise ValueError("Project %s doesn't exist" % project.id() )
    sub = project.subject(name)
    if not sub.exists():
        sub.create()
    #  multiple attribute set
    if demo:
        #  let NotImplementedError keep going
        passed_check, bad_keys = _key_check('subject', demo.keys())
        if passed_check:
            sub.attrs.mset(demo)
        else:
            raise ValueError("Bad demographics keys: %s" % ' '.join(bad_keys))
    return sub

def _key_check(check_type, keys):
    """ Private method to validate parameters before resource creation.

    Parameters
    ----------
    check_type: subject
        resource type
    keys: iterable
        parameters to check
    Returns
    -------
    passed: bool
        True if keys match xnat parameters, False if not
    bad_keys: iterable
        keys the caller specified that xnat won't accept
    """
    allowed_keys = {'subject': set(['group', 'src', 'pi_lastname', 'pi_firstname',
                    'dob',' yob', 'age', 'gender', 'handedness', 'ses',
                    'education', 'educationDesc', 'race', 'ethnicity',
                    'weight', 'height', 'gestational_age',
                    'post_menstrual_age', 'birth_weight'])}
    if check_type not in allowed_keys:
        raise NotImplementedError("Cannot currently check %s" % check_type)
    key_set = set(keys)
    passed = False
    bad_keys = []
    if allowed_keys[check_type].issuperset(key_set):
        passed = True
    else:
        bad_keys.extend(allowed_keys[check_type].difference(key_set))
    return passed, bad_keys


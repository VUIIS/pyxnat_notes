import os

from pyxnat import Interface
import xnat_util

"""
# Initially, you should login with your user name, p/w
xnat = Interface(server='http://masi.vuse.vanderbilt.edu/xnat',
                user='user',
                password='password',
                cachedir=os.path.join(os.path.expanduser('~'),'.xnat_store'))
                
store this in a cfg file and use it from then on so you don't have to publish
your p/w in source code
xnat.save_config('/a/path/to/your/config')
"""


"""
20110912
Code speaks for itself...
>>> xnat = Interface(server='http://masi.vuse.vanderbilt.edu/xnat', 
                    user='sburns', 
                    password='password', 
                    cachedir=os.path.join(os.path.expanduser('~'), '.xnat_store'))
>>> xnat.manage.users()
Out[4]: ['admin', 'boss', 'sburns', 'guest', 'testuser']
>>> xnat.save_config(os.path.join(os.path.expanduser('~'), '.xnat.cfg'))
>>> del xnat
>>> xnat = Interface(config=os.path.join(os.path.expanduser('~'), '.xnat.cfg'))
>>> xnat.manage.users()
ERROR: An unexpected error occurred while tokenizing input
The following traceback may be corrupted or invalid
The error message is: ('EOF in multi-line statement', (4, 0))

---------------------------------------------------------------------------
DatabaseError                             Traceback (most recent call last)
/Users/scottburns/Code/pyxnat_notes/<ipython-input-8-c7c4cb0dec76> in <module>()
----> 1 xnat.manage.users()

/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pyxnat/core/users.pyc in __call__(self)
     39         self._intf._get_entry_point()
     40 
---> 41         return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
     42                          ).get('login', always_list=True)
     43 

/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pyxnat/core/interfaces.pyc in _get_json(self, uri)
    299 
    300         if is_xnat_error(content):
--> 301             catch_error(content)
    302 
    303         return csv_to_json(content)

/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pyxnat/core/errors.pyc in catch_error(msg_or_exception)
     67             raise OperationalError('Connection failed')
     68         else:
---> 69             raise DatabaseError(error)
     70 
     71     # handle other errors, raised for instance by the http layer


DatabaseError: Method Not Implemented

?????????????????????

For now, I implemented my own Interface(config=) function in xnat_util.load_xnat
"""


xnat = xnat_util.load_xnat()
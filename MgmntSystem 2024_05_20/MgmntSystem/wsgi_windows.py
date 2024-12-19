activate_this = 'C:/Python36/Pyvenv/env/MgmntSystem/Scripts/activate_this.py'


# execfile(activate_this, dict(__file__=activate_this))
exec(open(activate_this).read(),dict(__file__=activate_this))

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Python36/Pyvenv/env/MgmntSystem/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/Python36/Pyvenv/projects/MgmntSystem')
sys.path.append('C:/Python36/Pyvenv/projects/MgmntSystem/MgmntSystem')

os.environ['DJANGO_SETTINGS_MODULE'] = 'MgmntSystem.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MgmntSystem.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()




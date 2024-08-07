=============
ckanext-msal
=============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!
A CKAN Extension for Azure Active Directory authentication using `MSAL <https://github.com/AzureAD/microsoft-authentication-library-for-js/wiki/MSAL-Installation>`_, compatible with CKAN 2.10 and based on a previous extensión here: `ONGOV <https://github.com/ongov/ckanext-msal>`_
We just change the authentication flow a bit and use the default new session handler library from CKAN 2.10

------------
Requirements
------------

MSAL

------------
Installation
------------

To install ckanext-msal:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-msal Python package into your virtual environment::

     git clone https://github.com/davilla41/un-ckan-msal.git
     cd un-ckan-msal/
     python setup.py develop
     pip install -r requirements.txt

3. Add ``un-ckan-msal`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/ckan.ini``).

4. Create and name a file msal_config.py. You can use this template: `msal_config.py <https://github.com/ongov/ckanext-msal/blob/ckan_2.9.7_compatible/ckanext/msal/msal_config.py>`_ and replace the generic values with your specific credentials. Put this new file in the same hierarchy than plugin.py file.

5.  Restart CKAN. For example if you've deployed CKAN on Ubuntu:

     sudo service supervisor restart


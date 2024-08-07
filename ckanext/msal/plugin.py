import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import ckan.model as model
from ckan.common import request, session
from flask import current_app as app, Blueprint, redirect
import ckan.lib.helpers as h
import msal
from . import msal_config


log = logging.getLogger(__name__)

application = msal.ConfidentialClientApplication(
    msal_config.CLIENT_ID,
    authority=msal_config.AUTHORITY,
    client_credential=msal_config.CLIENT_SECRET
)

def msal_login():
    '''Make call to authorization_url to authenticate user and get authorization code.'''
    #log.debug('Starting MSAL login process')
    authorization_url = application.get_authorization_request_url(
        msal_config.SCOPE,
        redirect_uri=msal_config.REDIRECT_URI
    )
    #log.error(authorization_url)
    #log.debug('MSAL login initiated')
    return redirect(authorization_url)

def get_a_token():
    '''Handle Azure AD callback.'''
    try:
        #log.debug("Starting get_a_token function")
        code = request.args['code']
        #log.debug(f"Authorization code received: {code}")
        
        result = application.acquire_token_by_authorization_code(
            code,
            scopes=msal_config.SCOPE,
            redirect_uri=msal_config.REDIRECT_URI
        )
        #log.debug(f"Token acquisition result: {result}")

        user = result.get("id_token_claims", {}).get("preferred_username")  # email
        #log.debug(f"User email from token: {user}")
        
        user_name = user.lower().replace('.', '_').split('@')[0].strip()  # ckan's username
        #log.debug(f"CKAN username: {user_name}")

        user_obj = model.User.get(user_name)
        #log.debug(f"User object from CKAN: {user_obj}")

        if not user_obj:
            # Create a new user in CKAN
            user_obj = model.User(name=user_name, email=user.lower(), password='default_password')
            user_obj.save()
            #log.info(f"Created new user in CKAN: {user_name}")
        else:
            # Activate the user if not already active
            if user_obj.state != 'active':
                user_obj.state = 'active'
                user_obj.save()
                log.info(f"Activated user: {user_name}")

        #log.debug(f"User {user} retrieved with username {user_name}")

        user_id = user_obj.id
        #log.debug(f"User ID: {user_id}")        

        # Set session for the user        
        session["_user_id"] = user_name
        session.save()
        #log.debug(f"Session Object: {session}")
        #log.debug(f"Session set for user: {user_name}")
        
        
        # Redirect to dataset
        site_url = app.config.get('ckan.site_url')
        resp = redirect(f'{site_url}/dashboard/datasets')

        #log.debug("Redirecting to dataset")
        return resp
    except ValueError as e:
        log.error('ValueError: {}'.format(repr(e)))
        return toolkit.abort(403, 'Not authorized.')
    except Exception as e:
        log.error('Exception raised. Unable to authenticate user: {}'.format(repr(e)))
        return toolkit.abort(403, 'Not authorized.')

def _get_repoze_handler(handler_name):
    '''Returns the URL that repoze.who will respond to and perform a login or logout.'''
    return getattr(request.environ['repoze.who.plugins']['friendlyform'], handler_name)

class MsalPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IAuthenticator)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'msal')

    # IAuthenticator
    def login(self):
        pass

    def identify(self):
        pass
    
    def logout(self):
      try:        
        session.clear()
        msad_url = msal_config.AUTHORITY
        site_url = app.config.get('ckan.site_url')
        logout_url = f"{msad_url}/oauth2/v2.0/logout?post_logout_redirect_uri={site_url}/user/login"
        log.info(f"Redirecting to logout URL: {logout_url}")
        return redirect(logout_url)
      except Exception as e:
        log.error(f"Error during logout: {e}")
        return toolkit.abort(500, 'Internal Server Error')

    # IBlueprint
    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        rules = [
            ('/msal/login', 'msal_login', msal_login),
            ('/getAToken', 'get_a_token', get_a_token)
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)
        return blueprint

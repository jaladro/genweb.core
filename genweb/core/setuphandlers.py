# -*- coding: utf-8 -*-
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.site import ISiteSchema

from genweb.core.interfaces import IHomePage

import logging
import transaction
import pkg_resources

try:
    pkg_resources.get_distribution('Products.PloneLDAP')
except pkg_resources.DistributionNotFound:
    HAS_LDAP = False
else:
    HAS_LDAP = True
    from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
    from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder

PROFILE_ID = 'profile-genweb.core:default'
# Specify the indexes you want, with ('index_name', 'index_type')
INDEXES = (('obrirEnFinestraNova', 'FieldIndex'),
           ('is_important', 'BooleanIndex'),
           ('favoritedBy', 'KeywordIndex'),
           ('exclude_from_nav', 'FieldIndex'),
           ('newsImageFile', 'FieldIndex')
           )


# Afegit creació d'indexos programàticament i controladament per:
# http://maurits.vanrees.org/weblog/archive/2009/12/catalog
def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger(__name__)

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    indexables = []
    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('genweb.core_various.txt') is None:
        return

    # Add additional setup code here
    #
    portal = context.getSite()
    logger = logging.getLogger(__name__)
    transforms = getToolByName(portal, 'portal_transforms')
    transform = getattr(transforms, 'safe_html')
    valid = transform.get_parameter_value('valid_tags')
    nasty = transform.get_parameter_value('nasty_tags')

    # GW4 Valid tags
    gw4_valid = ['script', 'object', 'embed', 'param', 'iframe', 'applet', 'button']
    for tag in gw4_valid:
        # Acceptar a la llista de valides
        valid[tag] = 1
        # Eliminar de la llista no desitjades
        if tag in nasty:
            del nasty[tag]

    stripped = transform.get_parameter_value('stripped_attributes')
    # GW4 remove some stripped
    for tag in ['cellspacing', 'cellpadding', 'valign']:
        if tag in stripped:
            stripped.remove(tag)

    kwargs = {}
    kwargs['valid_tags'] = valid
    kwargs['nasty_tags'] = nasty
    kwargs['stripped_attributes'] = stripped
    for k in list(kwargs):
        if isinstance(kwargs[k], dict):
            v = kwargs[k]
            kwargs[k + '_key'] = v.keys()
            kwargs[k + '_value'] = [str(s) for s in v.values()]
            del kwargs[k]
    transform.set_parameters(**kwargs)
    transform._p_changed = True
    transform.reload()

    if HAS_LDAP:
        try:
                manage_addPloneLDAPMultiPlugin(portal.acl_users, "ldapUPC",
                    title="ldapUPC", use_ssl=1, login_attr="cn", uid_attr="cn", local_groups=0,
                    users_base="ou=Users,dc=upc,dc=edu", users_scope=2,
                    roles="Authenticated", groups_base="ou=Groups,dc=upc,dc=edu",
                    groups_scope=2, read_only=True, binduid="cn=ldap.upc,ou=Users,dc=upc,dc=edu", bindpwd="conldapnexio",
                    rdn_attr="cn", LDAP_server="ldap.upc.edu", encryption="SSHA")
                portal.acl_users.ldapUPC.acl_users.manage_edit("ldapUPC", "cn", "cn", "ou=Users,dc=upc,dc=edu", 2, "Authenticated",
                    "ou=Groups,dc=upc,dc=edu", 2, "cn=ldap.upc,ou=Users,dc=upc,dc=edu", "conldapnexio", 1, "cn",
                    "top,person", 0, 0, "SSHA", 1, '')
                plugin = portal.acl_users['ldapUPC']

                plugin.manage_activateInterfaces(['IGroupEnumerationPlugin', 'IGroupsPlugin', 'IPropertiesPlugin', 'IGroupIntrospection', 'IAuthenticationPlugin', 'IRolesPlugin', 'IUserEnumerationPlugin', 'IRoleEnumerationPlugin'])
                #Comentem la linia per a que no afegeixi
                #LDAPUserFolder.manage_addServer(portal.acl_users.ldapUPC.acl_users, "ldap.upc.edu", '636', use_ssl=1)

                LDAPUserFolder.manage_deleteLDAPSchemaItems(portal.acl_users.ldapUPC.acl_users, ldap_names=['sn'], REQUEST=None)
                LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapUPC.acl_users, ldap_name='sn', friendly_name='Last Name', public_name='name')

                # Move the ldapUPC to the top of the active plugins.
                # Otherwise member.getProperty('email') won't work properly.
                from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
                portal.acl_users.plugins.movePluginsUp(IPropertiesPlugin, ['ldapUPC'])
                #portal.acl_users.plugins.manage_movePluginsUp('IPropertiesPlugin', ['ldapUPC'], context.REQUEST.RESPONSE)
        except:
                pass

    #try:
            # Fora el sistema de cookies que fan buscar al LDAP cn=*
    #        portal.acl_users.manage_delObjects('credentials_cookie_auth')
    #except:
    #        pass

    if HAS_LDAP:
        plugin = portal.acl_users['ldapUPC']
        plugin.ZCacheable_setManagerId('RAMCache')

        portal_role_manager = portal.acl_users['portal_role_manager']
        portal_role_manager.assignRolesToPrincipal(["Manager"], "UPC.Plone.Admins")
        portal_role_manager.assignRolesToPrincipal(["Manager"], "UPCnet.Plone.Admins")
        portal_role_manager.assignRolesToPrincipal(["Manager"], "UPCnet.ATIC")
        portal_role_manager.assignRolesToPrincipal(["Manager"], "UPCNET.Frontoffice.2n.nivell")

    # deshabilitem inline editing
    site_properties = ISiteSchema(portal)
    site_properties.enable_inline_editing = False

    # configurem els estats del calendari
    pct = getToolByName(portal, 'portal_calendar')
    pct.calendar_states = ('published', 'intranet')
    # Fixem el primer dia de la setamana com dilluns (0)
    pct.firstweekday = 0

    # Mark the home page
    if getattr(portal, 'front-page', False):
        alsoProvides(portal['front-page'], IHomePage)
        portal['front-page'].reindexObject()

    # Set mailhost
    mh = getToolByName(portal, 'MailHost')
    mh.smtp_host = 'localhost'
    portal.email_from_name = 'Genweb Administrator'
    portal.email_from_address = 'no-reply@upcnet.es'

    transaction.commit()

    add_catalog_indexes(portal, logger)

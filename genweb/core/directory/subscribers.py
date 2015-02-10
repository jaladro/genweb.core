from five import grok
from plone import api
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.PluggableAuthService.interfaces.events import IPropertiesUpdatedEvent
from repoze.catalog.query import Eq
from souper.interfaces import ICatalogFactory
from souper.soup import get_soup
from souper.soup import Record
from zope.component import getUtility


@grok.subscribe(IPropertiedUser, IPropertiesUpdatedEvent)
def add_user_to_catalog(principal, event):
    """ This subscriber hooks on user creation and adds user properties to the
        soup-based catalog for later searches
    """
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    exist = [r for r in soup.query(Eq('username', principal.getUserName()))]
    user_properties_utility = getUtility(ICatalogFactory, name='user_properties')
    indexed_attrs = user_properties_utility(portal).keys()

    if exist:
        user_record = exist[0]
    else:
        record = Record()
        record_id = soup.add(record)
        user_record = soup.get(record_id)

    user_record.attrs['username'] = principal.getUserName()

    for attr in indexed_attrs:
        if attr in event.properties:
            user_record.attrs[attr] = event.properties[attr]

    soup.reindex(records=[user_record])
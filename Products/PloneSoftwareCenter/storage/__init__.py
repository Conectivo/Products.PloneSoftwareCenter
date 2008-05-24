from zope.interface import implements
from zope.component import adapts
from zope.component import getAdapter
from zope.component import getAdapters
from zope.component import getGlobalSiteManager

from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage

class DynamicStorage(object):
    """This storage will trigger the right kind of storage
    given the user settings at root level"""
    def get(self, name, instance, **kwargs):
        return self._getStorage(instance).get(name, instance, **kwargs)

    def set(self, name, instance, value, **kwargs):
        return self._getStorage(instance).set(name, instance, value, **kwargs)

    def unset(self, name, instance, **kwargs):
        return self._getStorage(instance).get(name, instance, **kwargs)

    def getName(self):
        return 'dynamic'

    def _getStorage(self, instance):
        """returns the storage name, which is stored at PSC level"""
        # XXX crawl back up - what if the node in not in a PSC instance ?
        # need a better code here
        from Products.PloneSoftwareCenter.content.root import PloneSoftwareCenter
        from Products.Five import BrowserView
        
        psc = instance
        while not isinstance(psc, PloneSoftwareCenter):
            if isinstance(psc, BrowserView):
                psc = psc.context
            psc = psc.aq_inner.aq_parent
        name = psc.getStorageStrategy()
        return getAdapter(psc, IPSCFileStorage, name)

def getFileStorageAdapters(context):
    return getAdapters((context,), IPSCFileStorage)
    
def getFileStorageVocab(context):
    """return a vocab for the psc edit form. should probably go on a view somewhere eventually"""
    adapters = getFileStorageAdapters(context)
    return [ (name, "%s (%s)" % (storage.title, storage.description)) for name, storage in adapters ]
    
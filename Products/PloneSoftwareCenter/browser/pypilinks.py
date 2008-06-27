"""
 View that provides a page of links compatible
 with easy_install.

$Id:$
"""
import itertools

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class PyPILinksView(BrowserView):
    """view used for the main index page"""

    def get_urls_and_titles(self, brain):
        """returns url and title"""
        for element in brain.getObject().objectValues():
            info = {'title': element.title or ''}
            if element.portal_type == 'PSCFileLink':
                info['url'] = element.externalURL
            else:
                info['url'] = element.absolute_url()
            yield info

    def get_files(self):
        """provides the simple view over the projects
        with links to the published files"""
        sc = self.context
        catalog = getToolByName(self.context, 'portal_catalog')
        sc_path = '/'.join(sc.getPhysicalPath())
        query = {'path': sc_path, 'portal_type': 'PSCRelease',
                 'sort_on': 'getId',
                 'review_state': ('alpha', 'beta', 'pre-release', 'final')}
        return itertools.chain(*[self.get_urls_and_titles(brain)
                                 for brain in catalog(**query)])
       

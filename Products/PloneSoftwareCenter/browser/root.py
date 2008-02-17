from urllib import quote

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class SoftwareCenterView(BrowserView):
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()
        
        self.context_path = '/'.join(self.context.getPhysicalPath())
        
    def rss_url(self):
        """Get the URL to the RSS feed for the project center
        """
        return "%s/search_rss?" \
                "portal_type=PSCRelease&" \
                "sort_on=Date&sort_order=reverse&"\
                "review_state=alpha&review_state=beta&" \
                "review_state=release-candidate&review_state=final" \
                % self.context.absolute_url()
    
    def active_projects(self):
        """Get all active projects (i.e. they have one alpha/beta/rc/final 
        release).
        """
        return self.catalog(review_state = 'published',
                            portal_type = 'PSCProject',
                            path = self.context_path,
                            releaseCount = {'query' : 1, 'range' : 'min'},
                            sort_on = 'sortable_title',
                            sort_order = 'asc')
    
    def can_add_project(self):
        """Determine if the current user has permission to add a project
        """
        return self.membership.checkPermission('PloneSoftwareCenter: Add Project', self.context)
        
    def project_count(self):
        """Return number of projects
        """
        return len(self.catalog(portal_type = 'PSCProject', path = self.context_path))
        
    def release_count(self):
        """Return number of releases
        """
        return len(self.catalog(portal_type = 'PSCRelease', path = self.context_path))
        
    def categories(self):
        """Get categories to list
        
        Returns a list of dicts with keys id, title, rss_url, releases,
        num_projects.
        
        releases is a list of dicts with keys title, description,
        parent_url, review_state, date
        """
        
        def parent_url(url):
            return '/'.join(url.split('/')[:-2])
        
        vocab = self.context.getAvailableCategoriesAsDisplayList() 
        uniqueCategories = self.catalog.uniqueValuesFor('getCategories')
        field = self.context.getField('availableCategories')
        
        for cat in vocab.keys(): 
            if cat in uniqueCategories: 
                id = field.lookup(self.context, cat, 0)
                name = field.lookup(self.context, cat, 1)
                description = field.lookup(self.context, cat, 2)
                rss_url = "%s/search_rss?portal_type=PSCRelease&sort_on=Date&sort_order=reverse&path=%s&getCategories=%s&review_state=alpha&review_state=beta&review_state=release-candidate&review_state=final" % (self.portal_url, self.context_path, cat,)
                
                releases = []
                for r in self.catalog(path = self.context_path,
                                      portal_type = 'PSCRelease',
                                      getCategories = cat,
                                      sort_on = 'Date',
                                      sort_order = 'reverse',
                                      sort_limit = 5)[:5]:
                    releases.append(dict(title = r.Title,
                                         description = r.Description,
                                         parent_url = parent_url(r.getURL()),
                                         review_state = r.review_state,
                                         date = r.Date))
                
                num_projects = len(self.catalog(path = self.context_path, 
                                                portal_type = 'PSCProject',
                                                getCategories = cat))
        
                yield dict(name = name, description = description,
                           rss_url = rss_url, releases = releases,
                           num_projects = num_projects, id = id)

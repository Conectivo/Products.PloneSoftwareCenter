from base import PSCTestCase

from AccessControl.Permission import Permission
from AccessControl import Unauthorized
from DateTime.DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.permissions import AddSoftwareCenter
from Products.PloneSoftwareCenter.browser.pypi import PyPIView

def allowMembersToAddCenter(obj):
    perms = [p for p in obj.ac_inherited_permissions(1) if p[0] == AddSoftwareCenter]
    p = perms[0]
    name, value = perms[0][:2]
    p = Permission(name, value, obj)
    roles = p.getRoles()
    if 'Member' not in roles:
        if type(roles) == type(()):
            roles = list(roles)
            roles.append('Member')
            roles = tuple(roles)
        else:
            roles.append('Member')
    p.setRoles(roles)

class Resp:
    def setStatus(self, status):
        pass
    def setHeader(self, header, value, ext):
        if header.lower() == 'www-authenticate':
            raise Unauthorized()

class Req:
    def __init__(self, form):
        self.form = form
        self.response = Resp()


class TestPyPI(PSCTestCase):

    def afterSetUp(self):
        # Actual changes to portal
        allowMembersToAddCenter(self.portal)
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('user1', 'secret', ['Member'], [])
        membership.addMember('user2', 'secret', ['Member'], [])
        
    def testSubmit(self):
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        # a user can submit a package
        # that creates a project and a release folder, to hold
        # release infos.
        # no links or file links are created
        # until the project is published by the PSC owner
        self.login('user2')
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'xxx', 'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))
        view.submit()
        # check what has been created
        iw_dist = psc['iw.dist']
        rel = iw_dist.releases['0.1.0dev-r6983']
        # we don't want any file or file link
        self.assertEquals(rel.objectIds(), [])

        # now let the user 1 publish the project
        self.login('user1')
        
        wf = self.portal.portal_workflow
        wf.doActionFor(iw_dist, 'publish')

        self.login('user2')
        # and see how the submit works now
        view.submit()
        # check what has been created
        iw_dist = psc['iw.dist']
        rel = iw_dist.releases['0.1.0dev-r6983']
        # we don't want any file or file link
        self.assertEquals(rel.objectIds(), ['download'])

    def test_edit_project(self):
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        # making sure the project is correctly set
        self.login('user2')
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'The summary', 
                'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))

        view.submit()
        iw_dist = psc['iw.dist']
        self.assertEquals(iw_dist.getText(),  '<p>xxx</p>\n')

        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb',
                'version': '0.1.0dev-r6983'} 

        view = PyPIView(psc, Req(form))
        view.submit()
        self.assertEquals(iw_dist.getText(),  '<p>xxx</p>\n')



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPyPI))
    return suite


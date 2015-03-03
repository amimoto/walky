
import re
import types

from walky.utils import *
from walky.constants import *


class ACL(object):
    """ Define a single ACL
    """
    def __init__(self,
                    group,
                    allow=None,
                    deny=None,
                    mode=MODE_READ|MODE_WRITE|MODE_EXECUTE):
        self.group = group
        self.allow = allow
        self.deny = deny
        self.mode = mode

    def _acl_to_be_used(self,user,attr,mode,obj):
        """ Based upon the user's groups, is this ACL appropriate?
        """

        # If we do not service this mode
        if not self.mode & mode: 
            return False

        # And check if we can service this request
        if is_function(self.group):
            return self.group(user,attr,obj)
        else:
            if user.in_group(self.group):
                return True

        return False

    def _acl_allow_match(self,user,attr,mode,match,obj):
        """ check if we want to service this request
        """
        if is_function(match):
            return match(user,attr,mode,match,obj)
        else:
            for match_regex in match:
                if re.search("^"+match_regex+"$",attr):
                    return True
        return None

    def _acl_allows(self,user,attr,mode,obj):
        """ Check if we're allowed to access this attribute based upon
            ACLs
        """

        # First apply the allow filter
        allowed = self._acl_allow_match(user,attr,mode,self.allow,obj)
        if not allowed: return False

        # Then apply the deny filter
        denied = self._acl_allow_match(user,attr,mode,self.deny,obj)
        if denied: return False

        return True


class ACLMixin(object):
    """ Easy way of adding ACL support to a class.
        IMPORTANT: This doesn't automatically add security to calling
        functions and attributes. You'll need to do additional work, or
        use the ObjectWrapper class for that.
        This class only makes it possible to do things like check if
        an attribute is allowed.
    """

    _acls_ = None
    _acls_processed_ = {}

    def _acl(self,
                    groups,
                    allow=None,
                    deny=None,
                    mode=MODE_READ|MODE_WRITE|MODE_EXECUTE,
                    ):
        """ Adds a single _acl_ to our cache. Returns the _acl_ structure
        """
        if isinstance(groups,ACL):
            acl = groups
        else:
            acl = ACL(groups,allow,deny,mode)
        self._acls_.append(acl)
        return acl

    def _acl_set_fqn(self):
        return self.__module__+"."+self.__class__.__name__

    def _acl_init(self):
        """ Ensure all the ACL that have been prototyped
            are objects. This only needs to be called once.
            Note that there's a bit of craziness in this since
            we want to ensure that acl_init is called once for
            each class that inherits (including this one).
        """
        acl_fqn = self._acl_set_fqn()
        if self._acls_processed_.get(acl_fqn): return

        for i in range(len(self._acls_)):
            acl = self._acls_[i]
            if isinstance(acl,ACL): continue
            self._acls_[i] = ACL(*acl)

        self._acls_processed_[acl_fqn] = True

    def _acl_list(self,*acl_list):
        """ Adds a list of _acl_s to our cache
        """
        self._acl_init()
        for acl in acl_list:
            self._acl(acl)
        return self._acls_


    def _acl_allows(self,
                    user,
                    attr,
                    mode):
        """ Checks if a particular obj.attribute (mode) is allowed against
            our _acl_set
        """

        # Note that we do not allow any access to attributes
        # that prefix with _acl
        if re.search('^_acl',attr): 
            return False

        # Finally, iterate through the list to see if we can
        # allow the user to access this attribute
        for acl in self._acl_list():
            if acl._acl_to_be_used(user,attr,mode,self):
                return acl._acl_allows(user,attr,mode,self)

        return False


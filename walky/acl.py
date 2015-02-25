import re
import types

import walky.objects

RULE_TYPE_CLASS = 1
RULE_TYPE_FUNCTION = 2

MODE_READ = 0x04
MODE_WRITE = 0x02
MODE_EXECUTE = 0x01

class ACL(object):
    """ Define a single set of ACLs for objects
    """
    _attr_rules = None
    _obj_rules = None

    def __init__(self,*args,**kwargs):
        self._attr_rules = []
        self._obj_rules = []

    def obj_rule(self,
                    target_class,
                    evaluate=None,
                    allow=None,
                    deny=None,
                    sequence=0,
                    mask=MODE_READ|MODE_WRITE|MODE_EXECUTE):
        self._obj_rules.append({
            'type': RULE_TYPE_CLASS,
            'match': target_class,
            'allow': allow,
            'deny': deny,
            'sequence': sequence, 
            'mask': mask
        })

    def attr_rule(self,
                    target_class,
                    evaluate=None,
                    allow=None,
                    deny=None,
                    sequence=0,
                    mask=MODE_READ|MODE_WRITE|MODE_EXECUTE):
        self._attr_rules.append({
            'type': RULE_TYPE_CLASS,
            'match': target_class,
            'allow': allow,
            'deny': deny,
            'sequence': sequence, 
            'mask': mask
        })


    def match(self,obj,match,attr):
        if not match:
            return None

        if isinstance(match,types.UnboundMethodType) or \
           isinstance(match,types.FunctionType) or \
           isinstance(match,types.BuiltinFunctionType) or \
           isinstance(match,types.BuiltinMethodType) \
           : 
            if not match(obj,obj_attr,attr):
                return True
        else:
            for match_regex in match:
                if re.search(match_regex,attr):
                    break
            else: return True

        return False

    def check_allowed(self,obj,rule,attr):
        allowed = self.match(obj,rule.get('allow'),attr)
        if not allowed: return False
        denied = self.match(obj,rule.get('deny'),attr)
        if denied: return False
        return True

    def obj_allowed(self,
                    obj,
                    mode=None):
        if mode == None:
            raise Exception("Mode must be set")
        if not isinstance(obj,walky.objects.ObjectWrapper):
            raise Exception("Object must be of type walky.objects.ObjectWrapper")
        obj_fqn = obj.fqn()
        for rule in self._obj_rules:
            if not rule['mask'] & mode: continue
            if rule['type'] == RULE_TYPE_FUNCTION:
                if rule['match'] == None or rule['match'](obj):
                    return self.check_allowed(obj,rule,obj_fqn)
            if rule['type'] == RULE_TYPE_CLASS:
                if rule['match'] == None or isinstance(obj,rule['match']):
                    return self.check_allowed(obj,rule,obj_fqn)
        return False

    def attr_allowed(self,
                    obj,
                    attr=None,
                    mode=None):
        if mode == None:
            raise Exception("Mode must be set")
        # Validate that the user is allowed to access the object
        if not self.obj_allowed(obj,mode):
            return False
        # And if we're allowed to access the object, let's see
        # if we're allowed to access the particular attr
        for rule in self._attr_rules:
            if not rule['mask'] & mode: continue
            if rule['type'] == RULE_TYPE_FUNCTION:
                if rule['match'] == None or rule['match'](obj,attr):
                    return self.check_allowed(obj,rule,attr)
            if rule['type'] == RULE_TYPE_CLASS:
                if rule['match'] == None or isinstance(obj,rule['match']):
                    return self.check_allowed(obj,rule,attr)
        return False

if __name__ == '__main__':

    class TestClass(object):
        def a(self):
            return 'yar'
        b = 'foo'
        _c = None

    acl = ACL()

    acl.obj_rule( 
        TestClass,
        ['.*'],
        []
    )
    acl.attr_rule(
        None,
        ['.*'],
        ['_.*']
    )

    tc = TestClass()
    wtc = walky.objects.ObjectWrapper(tc)

    print "ALLOW" if acl.attr_allowed(wtc,'b',MODE_EXECUTE) else "NOPE"
    print "ALLOW" if acl.attr_allowed(wtc,'_b',MODE_EXECUTE) else "NOPE"

    # print "ALLOW" if acl.allowed(tc,mode=MODE_OBJECT) else "NOPE"


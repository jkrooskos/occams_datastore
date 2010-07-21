import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import zope.schema
from zope.component import provideUtility
from zope.interface import Interface
from zope.interface import verify
from zope.interface.interface import InterfaceClass

import sqlalchemy as sa

import avrc.data.store
from avrc.data.store import schema
from avrc.data.store import interfaces
from avrc.data.store import session
from avrc.data.store import model

class IObject(Interface):
    """
    OBJECT SCHEMAZ
    """
    
    foo = zope.schema.TextLine(title=u"FOO")
    
class IDummy(Interface):
    """
    This is a dummy schema to test if the schema manger can properly import it.
    """
    
    integer = zope.schema.Int(title=u"INTEGER", description=u"INTEGERDESC")
    
    string = zope.schema.TextLine(title=u"STRING", description=u"STRINGDESC")
    
    boolean = zope.schema.Bool(title=u"BOOL", description=u"BOOLDESC")
    
    decimal = zope.schema.Decimal(title=u"DECIMAL", description=u"DECIMALDESC")
    
    date = zope.schema.Date(title=u"DATE", description=u"DATE")
    
    #object = zope.schema.Object(title=u"OBJECT", description=u"OBJECTDESC", schema=IObject)
    
_SA_ECHO = False

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', avrc.data.store)
            fiveconfigure.debug_mode = False
            
            # Create a fake in-memory session
            engine = sa.create_engine("sqlite:///:memory:", echo=_SA_ECHO)
            
            model.setup_fia(engine)
            model.setup_pii(engine)
            
            utility = session.SessionFactory(bind=engine)
            
            provideUtility(utility, provides=interfaces.ISessionFactory)
            
            Session = utility()
            
            Session.add_all([
                model.Type(title=u"binary"),
                model.Type(title=u"boolean"),
                model.Type(title=u"datetime"),
                model.Type(title=u"integer"),
                model.Type(title=u"string"),
                model.Type(title=u"real"),
                model.Type(title=u"object"),
                ])
            Session.commit()

        @classmethod
        def tearDown(cls):
            provideUtility(None, provides=interfaces.ISessionFactory)

    def test_implementation(self):
        """
        Tests proper implementation
        """
        interface = interfaces.ISchemaManager
        cls = schema.SchemaManager
        
        self.assertTrue(interface.implementedBy(cls), "Not implemented")
        self.assertTrue(verify.verifyClass(interface, cls))
        
    def test_schema_import(self):
        """
        Tests that the schema manager can properly import a schema into the
        data store. The way it does this is it import the schema into the
        data store, retrieves it and then checks if it's equivalent.
        """
        
        mg = schema.SchemaManager()
        mg.importSchema(IDummy)
        
        klass = mg.getSchema(IDummy.__name__)
        
        self.assertTrue(isinstance(klass, InterfaceClass))
        self.assertTrue(klass.isOrExtends(interfaces.IMutableSchema))
        self.assertEquals(klass.__name__, IDummy.__name__)
        self.assertEquals("avrc.data.store.schema.generated", klass.__module__)
        
        # Check to make sure the generated interface still specifies the
        # correct fields
        dummynames = set(zope.schema.getFieldNames(IDummy))
        klassnames = set(zope.schema.getFieldNames(klass))
        self.assertTrue(set(dummynames) < set(klassnames))
        
        # Check that we can properly recreate the fields also
        for name in dummynames:
            self.assertEquals(klass[name], IDummy[name])
            

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

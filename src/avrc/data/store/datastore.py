"""
This module is in charge of handling the
the datastore instances through the use of Object events to keep track of
multiple instances across sites.
"""
import logging
from datetime import datetime, date, time
from collections import deque as queue

import zope.schema
from zope.component import createObject
from zope.component import getUtility
from zope.component import adapter
from zope.component import getSiteManager
from zope.component.factory import Factory
from zope.interface import implements
from zope.interface import providedBy
from zope.i18nmessageid import MessageFactory
from zope.lifecycleevent import IObjectCreatedEvent
from zope.lifecycleevent import IObjectRemovedEvent

import sqlalchemy as sa
from sqlalchemy import orm

from avrc.data.store import model
from avrc.data.store import interfaces

_ = MessageFactory(__name__)
log = logging.getLogger(__name__)

_ECHO_ENABLED = True

class Datastore(object):
    """
    """
    implements(interfaces.IDatastore)

    __name__ = __parent__ = None

    title = None
    dsn = None

    def __init__(self, title, dsn):
        """
        """
        self.title = title
        self.dsn = dsn

    @property
    def schemata(self):
        return interfaces.ISchemaManager(self)

    @property
    def protocols(self):
        return interfaces.IProtocolManager(self)

    def has(self, key):
        """
        This will check the data store if a particular instance exists.
        """

    def get(self, key):
        """
        This will retrieve a single an object from the data store based on
        it's key.
        """


    def keys(self):
        """
        Key's should be known... or can they?
        """
        raise NotImplementedError("This method is not implemented")

    def put(self, target):
        """
        Store the object into the database based on it's interface. The
        provided interface in the objects needs to have some sort of versioning
        metadata
        """
        types = getUtility(zope.schema.interfaces.IVocabularyFactory,
                           name="avrc.data.store.SupportedTypes"
                           )()
        Session = getUtility(interfaces.ISessionFactory)()

        # (parent object, corresponding parent db entry, value)
        to_visit = [(None, None, target)]

        primitive_types = (int, str, float, bool, date, time, datetime,)

        # Do a breadth-first pre-order traversal insertion
        while len(to_visit) > 0:
            (parent_obj, instance_rslt, value) = to_visit.popleft()

            # An object, add it's properties to the traversal queue
            if not isinstance(value, primitive_types):
                if not interfaces.ISchema.providedBy(value):
                    raise Exception("This object is not going to work out")

                try:
                    (schema_obj,) = list(value.__provides__)
                except ValueError as e:
                    raise Exception("Object has multiple inheritance: %s" % e)

                schema_rslt = Session.query(model.Schema)\
                              .filter_by(create_date=target.__version__)\
                              .join(model.Specification)\
                              .filter_by(module=schema_obj.__class__.__name__)\
                              .first()

                instance_rslt = model.Instance(schema=schema_rslt)

                for name, field_obj in zope.schema.getFieldsInOrder(schema_obj):
                    child = getattr(value, name)
                    to_visit.append((value, instance_rslt, child,))

            else:

                attribute_rslt = Session.query(model.Attribute)\
                                 .filter_by(name=unicode(name))\
                                 .join(instance_rslt.schema)\
                                 .first()

                type_name = attribute_rslt.type.title

                if type_name in (u"binary",):
                    Field = model.Binary
                elif type_name in (u"date", u"time", u"datetime"):
                    Field = model.Datetime
                elif type_name in (u"integer",):
                    Field = model.Integer
                elif type_name in (u"object",):
                    Field = model.Object
                elif type_name in (u"real",):
                    Field = model.Real
                elif type_name in (u"text", u"string"):
                    Field = model.String
                else:
                    raise Exception("Type %s unsupported."  % type_name)

                value_rslt = Field(
                    instance=instance_rslt,
                    attribute=attribute_rslt,
                    value=value
                    )

                Session.add(value_rslt)

        Session.commit()

    def purge(self, key):
        """
        By fire, be
        """

    def retire(self, key):
        """
        Keeping you around
        """

DatastoreFactory = Factory(
    Datastore,
    title=_(u"Data store factory"),
    description=_(u"Does stuff")
    )

class SessionFactory(object):
    """
    @see avrc.data.store.interfaces.ISessionFactory
    TODO: This module might have some issue with nested Sessions... this might
    need to be fixed on a per request basis. (using scoped_session maybe?)
    """

    implements(interfaces.ISessionFactory)

    def __init__(self,
                 autocommit=False,
                 autoflush=True,
                 twophase=False,
                 bind=None,
                 binds=None):
        """
        Our ISessionFactory implementation takes an extra parameter which
        will be the database bindings.
        """
        self.autocommit = autocommit
        self.autoflush = autoflush
        self.twophase = twophase
        self.binds = binds
        self.bind = bind

    def __call__(self):
        """
        Creates the Session object and binds it to the appropriate databases.
        @see: avrc.data.store.interfaces.ISessionFactory#__call__
        """

        Session  = orm.scoped_session(orm.sessionmaker(
            autocommit=self.autocommit,
            autoflush=self.autoflush,
            twophase=self.twophase
            ))

        Session.configure(bind=self.bind, binds=self.binds)

        return Session

def setupSupportedTypes():
    """
    This method should be used when setting up the supported types for a
    Datastore content type being added to a folder in the zope site.
    """
    rslt = []
    Session = getUtility(interfaces.ISessionFactory)()
    types_factory = getUtility(zope.schema.interfaces.IVocabularyFactory,
                               name="avrc.data.store.SupportedTypes")

    for t in list(types_factory()):
        rslt.append(model.Type(
            title=unicode(t.token),
            description=unicode(getattr(t.value, "__doc__", None)),
            ))

    Session.add_all(rslt)
    Session.commit()

@adapter(interfaces.IDatastore, IObjectCreatedEvent)
def handleDatastoreCreated(datastore, event):
    """
    Triggered when a new DataStore instance is added to a container (i.e.
    when it is added to a site.
    This method will setup all metadata needed for the engine to fully
    offer it's services.
    """
    engine = sa.create_engine(datastore.dsn, echo=True)

    model.setup(engine)

    # Set autocommit true so that components create their own sessions.
    sm = getSiteManager(datastore)
    sm.registerUtility(SessionFactory(bind=engine),
                       provided=interfaces.ISessionFactory)

    setupSupportedTypes()

@adapter(interfaces.IDatastore, IObjectRemovedEvent)
def handleDatastoreRemoved(datastore, event):
    """
    Triggered when a new DataStore instance is removed from a container
    """
    sm = getSiteManager(datastore)
    sm.registerUtlity(None, provided=interfaces.ISessionFactory)


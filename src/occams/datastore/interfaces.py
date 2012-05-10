"""
Specification of services provided by this plug-in.

This system employs a database framework known as
`Entity-Attribute-Value with Schema-Relationships Models` or simply `EAV`_ for
short.

.. _EAV: http://www.ncbi.nlm.nih.gov/pmc/articles/PMC61391/
"""

import zope.interface
import zope.schema
from zope.schema.interfaces import IVocabulary
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from occams.datastore import MessageFactory as _


# Fixed type vocabulary
typesVocabulary = SimpleVocabulary([
        SimpleTerm(value=zope.schema.Bool, token='boolean', title='Boolean'),
        SimpleTerm(value=zope.schema.Decimal, token='decimal', title='Decimal'),
        SimpleTerm(value=zope.schema.Int, token='integer', title='Integer'),
        SimpleTerm(value=zope.schema.Date, token='date', title='Date'),
        SimpleTerm(value=zope.schema.Datetime, token='datetime', title='Datetime'),
        SimpleTerm(value=zope.schema.TextLine, token='string', title='String'),
        SimpleTerm(value=zope.schema.Text, token='text', title='Text'),
        SimpleTerm(value=zope.schema.Object, token='object', title='Object'),
    ],
    IVocabulary
    )


class DataStoreError(Exception):
    """
    Base exception class for this module
    """


class NotFoundError(DataStoreError):
    """
    Raised when the entry was not found
    """


class UnexpectedResultError(DataStoreError):
    """
    Raised when  the result set returned from the database is not the expected
    value. Examples include receiving more than one result when only one is
    expected.
    """


class MissingKeyError(DataStoreError):
    """
    Raised when a new item is missing a unique name
    """


class AlreadyExistsError(DataStoreError):
    """
    Raised when trying to add an entry that already exists
    """


class CorruptAttributeError(DataStoreError):
    """
    Raised when the specified checksum of an attribute does not actually match
    the generated checksum.
    """


class XmlError(DataStoreError):
    """
    Raised when there is an error generating or parsing an XML file.
    """


class NonExistentUserError(DataStoreError):
    """
    Raised when flushing data with an non-existent user.
    """


class InvalidEntitySchemaError(DataStoreError):
    """
    Raised when an entity is being added for an invalid schema. (e.g. unpublished)
    """


class ConstraintError(DataStoreError):
    """
    Raised when an invalid value is set to an entity
    """


class IDataStoreComponent(zope.interface.Interface):
    """
    Marker interface for components of this package.
    """


class IReferenceable(IDataStoreComponent):
    """
    An object that can be stored in a database.
    """

    id = zope.schema.Int(
        title=_(u'Database ID'),
        description=_(
            u'This value is auto-generated by the database and assigned to '
            u'the item. It should not be modified, otherwise risking '
            u'altered database behavior.'
            ),
        readonly=True
        )


class IUser(IReferenceable):
    """
    A simple user for audit trails
    """

    key = zope.schema.ASCIILine(
        title=_(u'User Key'),
        description=_(u'A unique way of distinguishing a user (e.g. email or uid)')
        )


class IDescribeable(IDataStoreComponent):
    """
    A human-readable object.
    """

    name = zope.schema.BytesLine(
        title=_(u'Internal name.'),
        description=_(
            u'This value is usually an ASCII label to be used for '
            u'easy reference of the item. When naming an item, lowercase '
            u'alphanumeric characters or hyphens. The name should also be '
            u'unique within a container.'
            )
        )

    title = zope.schema.TextLine(
        title=_(u'Human readable name'),
        )

    description = zope.schema.Text(
        title=_(u'Description/Prompt')
        )


class IModifiable(IDataStoreComponent):
    """
    An object with modification metadata.
    """

    create_date = zope.schema.Datetime(
        title=_(u'Date Created'),
        readonly=True,
        )

    create_user = zope.schema.Object(
        title=_(u'Created By'),
        schema=IUser,
        readonly=True,
        )

    modify_date = zope.schema.Datetime(
        title=_(u'Date Modified'),
        readonly=True,
        )

    modify_user = zope.schema.Object(
        title=_(u'Modified By'),
        schema=IUser,
        readonly=True,
        )


class IDataBaseItem(IReferenceable, IDescribeable, IModifiable):
    """
    An object that originates from database.
    """


class ICategory(IDataBaseItem):
    """
    Logical categories for schemata in order to be able to group them.
    """


class ISchema(IDataBaseItem):
    """
    An object that describes how an EAV schema is generated.
    Typically, an EAV schema represents a group of attributes that represent
    a meaningful data set. (e.g. contact details, name, test result.)
    Resulting schema objects can then be used to produce forms such as
    Zope-style interfaces.
    """

    sub_schemata = zope.schema.Iterable(
        title=_(u'Sub Schemata'),
        description=_(u'Listing of schemata that subclass the Zope-style interface.'),
        )

    categories = zope.schema.Set(
        title=_(u'Categories'),
        description=_(u'Listing of schema categories.'),
        value_type=zope.schema.Object(schema=ICategory),
        )

    state = zope.schema.Choice(
        title=_(u'Circulation State'),
        values=sorted(['draft', 'review', 'published', 'retracted']),
        default='draft',
        )

    storage = zope.schema.Choice(
        title=_(u'Storage method'),
        description=_(
            u'How the generated objects will be stored. Storage methods are: '
            u'eav - individual values are stored in a type-sharded set of tables; '
            u'resource - the object exists in an external service, such as MedLine; '
            u'table - the object is stored in a conventional SQL table;'
            ),
        values=sorted(['resource', 'eav', 'table']),
        default='eav',
        )

    publish_date = zope.schema.Date(
        title=_(u'The date the schema was published for data collection')
        )

    is_association = zope.schema.Bool(
        title=_(u'Is the schema an association?'),
        description=_(
            u'If set and True, the schema is an defines an association for '
            u'multiple schemata.'
            ),
        required=False,
        )

    is_inline = zope.schema.Bool(
        title=_(u'Is the resulting object inline?'),
        description=_(
            u'If set and True, the schema should be rendered inline to other '
            u'container schemata. '
            ),
        required=False,
        )


# Needs to be defined here, because it's type refers to itself.
ISchema.base_schema = zope.schema.Object(
    title=_(u'Base schema'),
    description=_(
        u'A base schema for this schema to extend, thus emulating OO-concepts.'
        ),
    schema=ISchema,
    required=False,
    )


class IAttribute(IDataBaseItem):
    """
    An object that describes how an EAV attribute is generated.
    Typically, an attribute is a meaningful property in the class data set.
    (e.g. user.firstname, user.lastname, contact.address, etc..)
    Note that if the attribute's type is an object, an object_class must
    be specified as well as a flag setting whether the object is to be
    rendered inline.
    Resulting attribute objects can then be used to produce forms such as
    Zope-style schema field.
    """

    schema = zope.schema.Object(
        title=_(u'Schema'),
        description=_(u'The schema that this attribute belongs to'),
        schema=ISchema,
        )

    type = zope.schema.Choice(
        title=_(u'Type'),
        values=sorted(typesVocabulary.by_token.keys()),
        )

    choices = zope.schema.Iterable(
        title=_(u'Acceptable answer choices of type IChoice.')
        )

    is_collection = zope.schema.Bool(
        title=_(u'Is the attribute a collection?'),
        default=False,
        )

    is_required = zope.schema.Bool(
        title=_(u'Is the attribute a required field?'),
        default=False,
        )

    object_schema = zope.schema.Object(
        title=_(u'The object\'s schema'),
        description=_(u'Only applies to attributes of type "object". '),
        schema=ISchema,
        required=False
        )

    value_min = zope.schema.Int(
        title=_(u'Minimum value'),
        description=u'Minimum length or value (depending on type)',
        required=False,
        )

    value_max = zope.schema.Int(
        title=_(u'Maximum value'),
        description=u'Maximum length or value (depending on type)',
        required=False
        )

    collection_min = zope.schema.Int(
        title=_(u'Minimum list length'),
        required=False,
        )

    collection_max = zope.schema.Int(
        title=_(u'Maximum list length'),
        required=False
        )

    validator = zope.schema.TextLine(
        title=_(u'Validation regular expressions'),
        description=_(
            u'Use Perl-derivative regular expression to validate the attribute value.'
            ),
        required=False,
        )

    order = zope.schema.Int(
        title=_(u'Display Order')
        )


class IChoice(IDataBaseItem):
    """
    Possible value constraints for an attribute.
    Note objects of this type are not versioned, as they are merely an
    extension of the IAttribute objects. So if the choice constraints
    are to be modified, a new version of the IAttribute object
    should be created.
    """

    attribute = zope.schema.Object(
        title=_(u'Attribute'),
        description=_(u'The attribute that will be constrained.'),
        schema=IAttribute
        )

    value = zope.schema.TextLine(
        title=_(u'Value'),
        description=_(u'The value will be coerced when stored.')
        )

    order = zope.schema.Int(
        title=_(u'Display Order')
        )


class IEntity(IDataBaseItem):
    """
    An object that describes how an EAV object is generated.
    Note that work flow states may be assigned to class entities.
    """

    schema = zope.schema.Object(
        title=_(u'Object Schema'),
        description=_(u'The scheme the object will provide once generated.'),
        schema=ISchema
        )

    state = zope.schema.Choice(
        title=_(u'The current workflow state'),
        values=sorted([
            'pending-entry', 'pending-review',
            'complete', 'not-done',
            'error',
            ]),
        default='pending-entry',
        )

    collect_date = zope.schema.Date(
        title=_(u'Date Collected'),
        description=_(u'The date that the information was physically collected'),
        )


class IValue(IDataBaseItem):
    """
    An object that records values assigned to an EAV Entity.
    """

    entity = zope.schema.Object(
        title=_(u'Entity'),
        schema=IEntity
        )

    attribute = zope.schema.Object(
        title=_(u'Property'),
        schema=IAttribute
        )

    choice = zope.schema.Object(
        title=_('Choice'),
        description=_(
            u'Used for book keeping purposes as to where the value was '
            u'assigned from.'
            ),
        schema=IChoice,
        required=False
        )

    value = zope.schema.Field(
        title=_(u'Assigned Value'),
        )


class IManager(IDataStoreComponent):
    """
    A manager component that is in charge of accessing a particular class of
    data. Note that a manager is simply a utility into to the data store,
    therefore creating multiple instances of a manager should have no effect on
    the objects being managed as they are still being pulled from the same source.

    In theory, anything that can be done in a manager should be able to be
    done using the models themselves.
    """

    def keys():
        """
        Generates a collection of the keys for the objects the component is
        managing.

        Returns
            A listing of the object keys being managed by this manager.
        """

    def has(key):
        """
        Checks if the component is managing the item.

        Arguments
            ``key``
                The name of the item.

        Returns
            ``True`` if the manager is in control of the item, ``False`` otherwise
        """

    def purge(key):
        """
        Completely removes the target and all data associated with it
        from the database. Note that any constraints that are in place in
        the database will take precedence, possibly raising
        ``ConstraintNotSatisfied`` errors

        Arguments
            ``key``
                The name of the item.

        Returns
            The number of items purged from the dabase. (This does
            not include all related items).
        """

    def get(key):
        """
        Retrieve an item in the database.

        Arguments
            ``key``
                The name of the item.

        Returns
            An object maintained by the manger.

        Raises
            ``ManagerKeyError`` if the item is not found
        """

    def put(key, item):
        """
        Adds the item to the manager.

        Arguments
            ``key``
                The name of the item.
            ``item``
                The item to be stored in the manager.

        Returns
            The database id number of the newly stored item
        """


class IUserManager(IManager):
    # No new functionality yet.
    pass


class IUserManagerFactory(IDataStoreComponent):

    def __call__(session):
        """
        Schema Manager constructor call signature.

        Arguments
            ``session``
                A database session to use for retrieval of entry information.
        """


class ISchemaManager(IManager):

    def keys(on=None):
        """
        Generates a collection of the keys for the objects the component is
        managing.

        Arguments
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Returns
            A listing of the object keys being managed by this manager.
        """

    def has(key, on=None):
        """
        Checks if the component is managing the item.

        Arguments
            ``key``
                The name of the item.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Returns
            ``True`` if the manager is in control of the item, ``False`` otherwise
        """

    def purge(key, on=None, ever=False):
        """
        Completely removes the target and all data associated with it
        from the data store.

        Arguments
            ``key``
                The name of the item.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.
            ``ever``


        Returns
            The number of items purged from the data store. (This does
            not include all related items).
        """

    def get(key, on=None):
        """
        Retrieve an item in the manager.

        Arguments
            ``key``
                The name of the item.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Returns
            An object maintained by the manger.

        Raises
            ``ManagerKeyError`` if the item is not found
        """


class ISchemaManagerFactory(IDataStoreComponent):

    def __call__(session):
        """
        Schema Manager constructor call signature.

        Arguments
            ``session``
                A database session to use for retrieval of entry information.
        """


class IHierarchy(IDataStoreComponent):
    """
    Offers functionality on inspecting a the hierarchy of a schema
    description.
    """

    def children(key, on=None):
        """
        Return the children (leaf nodes) in the hierarchy of the specified name.

        Arguments
            ``key``
                The name of the parent schema.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Raises
            ``ManagerKeyError`` if the parent schema is not found
        """

    def iterChildren(key, on=None):
        """
        Returns an iterator over the children (leaf nodes) in the hierarchy of
        the specified name.

        Arguments
            ``key``
                The name of the parent schema.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Raises
            ``ManagerKeyError`` if the parent schema is not found
        """


    def childrenNames(key, on=None):
        """
        Return the names of all the children (leaf nodes) in the hierarchy of
        the specified name.

        Arguments
            ``key``
                The name of the parent schema.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Raises
            ``ManagerKeyError`` if the parent schema is not found
        """

    def iterChildrenNames(key, on=None):
        """
        Return an iterator over the names of all the children (leaf nodes) in
        the hierarchy of the specified name.

        Arguments
            ``key``
                The name of the parent schema.
            ``on``
                (Optional) Query for the most recent schema as of the date
                specified. A value of ``None`` (default) indicates the most
                recent schema.

        Raises
            ``ManagerKeyError`` if the parent schema is not found
        """


class IHierarchyFactory(IDataStoreComponent):

    def __call__(session):
        """
        Hierarchy Inspector constructor call signature

        Arguments
            ``session``
                A database session to use for retrieval of entry information.
        """
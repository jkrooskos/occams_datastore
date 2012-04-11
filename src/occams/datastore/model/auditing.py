"""
Auditing components for mappings.
Note that the majory of this code was copied from the SQLAlchemy examples on
``versioning``/``history``. Our team decided to rename the mechanics to
``auditing`` as we felt it was a better suited name and also avoids confusion
with the schema deep-copying mechanics we already have (which our team
refers to as ``versioning``)

Credit to **zzzeek** et al.
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapper
from sqlalchemy.orm import attributes
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm import object_session
from sqlalchemy.orm.exc import UnmappedColumnError
from sqlalchemy.orm.properties import RelationshipProperty


class Auditable(object):
    """
    Enables a mapping to have an "audit" table of previous modifications done
    to its entries. Useful for auditing purposes and helps keeping old entries
    backed up without interfereing with "live" data.
    """

    @declared_attr
    def __mapper_cls__(cls):
        def map(cls, *arg, **kw):
            mp = mapper(cls, *arg, **kw)
            auditMapper(mp)
            return mp
        return map

def auditMapper(mapping):
    """
    Creates an identical mapping for auditing purposes
    This method should only be called when the 'live' table's mapping is complete
    so that it can properly replicate all the corresponding columns
    """

    # Set the 'active_history' flag only on column-mapped attributes so that
    # the old revision of the info is always loaded
    for prop in mapping.iterate_properties:
        getattr(mapping.class_, prop.key).impl.active_history = True


    super_mapper = mapping.inherits
    super_history_mapper = getattr(mapping.class_, '__audit_mapper__', None)

    polymorphic_on = None

    if not super_mapper or mapping.local_table is not super_mapper.local_table:
        super_fks = []
        cols = []

        def col_references_table(col, table):
            for fk in col.foreign_keys:
                if fk.references(table):
                    return True
            return False

        for column in mapping.local_table.c:
            if column.name == 'revision':
                continue

            col = column.copy()
            col.unique = False

            if super_mapper and col_references_table(column, super_mapper.local_table):
                super_fks.append((col.key, list(super_history_mapper.local_table.primary_key)[0]))

            cols.append(col)

            if column is mapping.polymorphic_on:
                polymorphic_on = col

        if super_mapper:
            super_fks.append(('revision', super_history_mapper.base_mapper.local_table.c.revision))
            cols.append(Column('revision', Integer, primary_key=True))
        else:
            cols.append(Column('revision', Integer, primary_key=True))

        if super_fks:
            cols.append(ForeignKeyConstraint(*zip(*super_fks)))

        table = Table(mapping.local_table.name + '_audit', mapping.local_table.metadata,
           *cols
        )
    else:
        # single table inheritance.  take any additional columns that may have
        # been added and add them to the history table.
        for column in mapping.local_table.c:
            if column.key not in super_history_mapper.local_table.c:
                col = column.copy()
                col.unique = False
                super_history_mapper.local_table.append_column(col)
        table = None

    if super_history_mapper:
        bases = (super_history_mapper.class_,)
    else:
        bases = mapping.base_mapper.class_.__bases__

    mapping.class_.__audit_mapper__ = mapper(
        class_=type.__new__(type, '%sAudit' % mapping.class_.__name__, bases, {}),
        local_table=table,
        inherits=super_history_mapper,
        polymorphic_on=polymorphic_on,
        polymorphic_identity=mapping.polymorphic_identity
        )

    if not super_history_mapper:
        revisionColumn = Column('revision', Integer, default=1, nullable=False)
        mapping.local_table.append_column(revisionColumn)
        mapping.add_property('revision', mapping.local_table.c.revision)


def createRevision(instance, deleted=False):
    """
    Inspects the instance for changes and bumps it's previous row data to
    the audit table.
    """
    obj_mapper = object_mapper(instance)
    audit_mapper = instance.__audit_mapper__
    audit_cls = audit_mapper.class_

    obj_state = attributes.instance_state(instance)

    attr = {}

    changed = False

    for om, hm in zip(obj_mapper.iterate_to_root(), audit_mapper.iterate_to_root()):
        if hm.single:
            continue

        for hist_col in hm.local_table.c:
            if hist_col.key == 'revision':
                continue

            obj_col = om.local_table.c[hist_col.key]

            # get the value of the attribute based on the MapperProperty
            # related to the mapped column.  this will allow usage of
            # MapperProperties that have a different keyname than that of the
            # mapped column.
            try:
                prop = obj_mapper.get_property_by_column(obj_col)
            except UnmappedColumnError:
                # in the case of single table inheritance, there may be
                # columns on the mapped table intended for the subclass only.
                # the 'unmapped' status of the subclass column on the
                # base class is a feature of the declarative module as of sqla 0.5.2.
                continue

            # expired object attributes and also deferred cols might not be in the
            # dict.  force it to load no matter what by using getattr().
            if prop.key not in obj_state.dict:
                getattr(instance, prop.key)

            # (added, unchanged, deleted)
            (a, u, d) = attributes.get_history(instance, prop.key)

            if d:
                attr[hist_col.key] = d[0]
                changed = True
            elif u:
                attr[hist_col.key] = u[0]
            else:
                # if the attribute had no value.
                attr[hist_col.key] = a[0]
                changed = True

    if not changed:
        # not changed, but we have relationships.  OK check those too
        for prop in obj_mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty) and \
                attributes.get_history(instance, prop.key).has_changes():
                changed = True
                break

    if changed or deleted:
        session = object_session(instance)
        attr['revision'] = instance.revision
        session.add(audit_cls(**attr))
        instance.revision += 1


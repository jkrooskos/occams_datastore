"""
Data Definition Library

Note that the entities defined in this module are mapped to a database.
Therefore, great care should be taken when updating this file, as it may
cause live systems to fall out of sync.
"""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

FIA = declarative_base()
PII = declarative_base()

def _setup_base(base, engine):
    """
    """
    base.metadata.create_all(bind=engine, checkfirst=True) 
     
def setup_fia(engine):
    """
    """
    _setup_base(FIA, engine)
    
def setup_pii(engine):
    """
    """
    _setup_base(PII, engine)
    
# -----------------------------------------------------------------------------
# Personal Information
# -----------------------------------------------------------------------------

class Name(PII):
    """
    """
    __tablename__ = "name"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    first = sa.Column(sa.Unicode, nullable=False, index=True)
    
    middle = sa.Column(sa.Unicode)
    
    last = sa.Column(sa.Unicode, nullable=False, index=True)
    
    sur = sa.Column(sa.Unicode)
        
class Address(PII):
    """
    """
    __tablename__ = "address"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    phone = sa.Column(sa.Unicode, index=True)
    
    address1 = sa.Column(sa.Unicode)
    
    address2 = sa.Column(sa.Unicode)
    
    city = sa.Column(sa.Unicode)

    state_id = sa.Column(sa.Integer, sa.ForeignKey("state.id"))
    
    zip = sa.Column(sa.Integer)

class State(PII):
    """
    """
    __tablename__ = "state"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    country_id = sa.Column(sa.Integer, sa.ForeignKey("country.id"),
                           nullable=False)
    
    abbreviation = sa.Column(sa.Unicode, nullable=False)
    
    name = sa.Column(sa.Unicode, nullable=False)
    
    __table_args__ = (
        sa.UniqueConstraint("country_id", "name"), 
        {})

class Country(PII):
    """
    """
    __tablename__ = "country"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    abbreviation = sa.Column(sa.Unicode, nullable=False, unique=True)
    
    name = sa.Column(sa.Unicode, nullable=False, unique=True)
    
class Phone(PII):
    """
    """
    __tablename__ = "phone"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    location_id = sa.Column(sa.Integer, sa.ForeignKey("location.id"),
                            nullable=False)
    
    location = orm.relation("Location", uselist=False)
    
    value = sa.Column(sa.Unicode, nullable=False)
    
class Email(PII):
    """
    """
    __tablename__ = "email"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    location_id = sa.Column(sa.Integer, sa.ForeignKey("location.id"),
                            nullable=False)
    
    location = orm.relation("Location", uselist=False)
    
    value = sa.Column(sa.Unicode, nullable=False)    
        
class Location(PII):
    """
    """
    __tablename__ = "location"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    title = sa.Column(sa.Unicode, nullable=False)
        
class Demographic(PII):
    """
    """
    __tablename__ = "demographic"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    birth_date = sa.Column(sa.DateTime)
    
class Physique(PII):
    """
    """
    __tablename__ = "physique"
    
    id = sa.Column(sa.Integer, primary_key=True)

# -----------------------------------------------------------------------------
# Visit
# -----------------------------------------------------------------------------

class Curator(FIA):
    """
    """
    __tablename__ = "curator"
    
    id = sa.Column(sa.Integer, primary_key=True)

class Subject(FIA):
    """
    """
    __tablename__ = "subject"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    uid = sa.Column(sa.Integer, nullable=False, unique=True)
    
class Domain(FIA):
    """
    """
    __tablename__ = "domain"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    title = sa.Column(sa.Unicode, nullable=False, unique=True)
    
class Enrollment(FIA): 
    """
    """
    __tablename__ = "enrollment"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    protocol_id = sa.Column(sa.Integer, sa.ForeignKey("protocol.id"), 
                            nullable=False)
    
    protocol = orm.relation("Protocol", uselist=False)
    
    subject_id = sa.Column(sa.Integer, sa.ForeignKey("subject.id"), 
                           nullable=False)
    
    subject = orm.relation("Subject", uselist=False)
    
    start_date = sa.Column(sa.Date, nullable=False)
    
    stop_date = sa.Column(sa.Date)
    
    create_date = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    
    __table_args__ = (
        sa.UniqueConstraint("protocol_id", "subject_id", "start_date"), 
        {})

class Visit(FIA):
    """
    """
    __tablename__ = "visit"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    enrollement_id = sa.Column(sa.Integer, sa.ForeignKey(Enrollment.id),
                               nullable=False)
    
    enrollement = orm.relation("Enrollment", uselist=False)
    
    visit_date = sa.Column(sa.Date, nullable=False)

visit_instance_table = sa.Table("visit_instance", FIA.metadata,
    sa.Column("visit_id", sa.ForeignKey("visit.id"), nullable=False),
    sa.Column("instance_id", sa.ForeignKey("instance.id"), nullable=False),
    sa.PrimaryKeyConstraint("visit_id", "instance_id")
    )
        
domain_schema_table = sa.Table("domain_schema", FIA.metadata,
    sa.Column("domain_id", sa.Integer, sa.ForeignKey("domain.id"), 
              nullable=False),
    sa.Column("schema_id", sa.Integer, sa.ForeignKey("schema.id"), 
              nullable=False),
    sa.PrimaryKeyConstraint("domain_id", "schema_id")
    )
        
# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------

class Keyword(FIA):
    """
    """
    __tablename__ = "keyword"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False)
    
    instance = orm.relation("Instance", uselist=False)
    
    title = sa.Column(sa.Unicode, nullable=False, index=True)
    
    is_synonym = sa.Column(sa.Boolean, nullable=False, default=True)
    
    __table_args__ = (
        sa.UniqueConstraint("instance_id", "title"), 
        {})

class Instance(FIA):
    """
    """
    __tablename__ = "instance"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    schema_id = sa.Column(sa.Integer, sa.ForeignKey("schema.id"), 
                          nullable=False)
    
    schema = orm.relation("Schema", uselist=False)
    
    title = sa.Column(sa.Unicode, nullable=False, unique=True)
    
    description = sa.Column(sa.Unicode)
    
    create_date = sa.Column(sa.DateTime, nullable=False)
    
    modify_date = sa.Column(sa.DateTime, nullable=False)

class Binary(FIA):
    """
    """
    __tablename__ = "binary"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    extension = sa.Column(sa.Unicode)
    
    value = sa.Column(sa.BLOB, nullable=False)

class Datetime(FIA):
    """
    """
    __tablename__ = "datetime"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    value = sa.Column(sa.DateTime, nullable=False)
    
sa.Index("datetime_attribute_value", Datetime.attribute_id, Datetime.value)
    
    
class Integer(FIA):
    """
    """
    __tablename__ ="integer"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    value = sa.Column(sa.Integer, nullable=False)
    
sa.Index("integer_attribute_value", Integer.attribute_id, Integer.value)

class Real(FIA):
    """
    """
    __tablename__ ="real"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    value = sa.Column(sa.Integer, nullable=False)
    
sa.Index("real_attribute_value", Real.attribute_id, Real.value)
        
class Object(FIA):
    """
    """
    __tablename__ ="object"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    value = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                      nullable=False
                      )
    
    order = sa.Column(sa.Integer, nullable=False, default=1)
        
sa.Index("object_attribute_value", Object.attribute_id, Object.value)

class String(FIA):
    """
    """
    __tablename__ ="string"
    
    instance_id = sa.Column(sa.Integer, sa.ForeignKey("instance.id"),
                            nullable=False,
                            primary_key=True)
    
    attribute_id = sa.Column(sa.Integer, sa.ForeignKey("attribute.id"),
                            nullable=False,
                            primary_key=True)
    
    value = sa.Column(sa.Unicode, nullable=False)

sa.Index("string_attribute_value", String.attribute_id, String.value)
  
# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------

class Hierarchy(FIA):
    """
    """
    __tablename__ = "hierarchy"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("specification.id"))

    child_id = sa.Column(sa.Integer, sa.ForeignKey("specification.id"),
                                nullable=False)

class Specifiation(FIA):
    """
    """
    __tablename__ = "specification"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    title = sa.Column(sa.Unicode, nullable=False, unique=True)
    
    description = sa.Column(sa.Text, nullable=False)
    
    is_association = sa.Column(sa.Boolean, nullable=False, default=False)
    
    is_virtual = sa.Column(sa.Boolean, nullable=False, default=False)
    
class Invariant(FIA):
    """
    """
    __tablename__ = "invariant"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    schema_id = sa.Column(sa.Integer, sa.ForeignKey("schema.id"),
                          nullable=False)
    
    title = sa.Column(sa.Unicode, nullable=False)
    
schema_attribute_table = sa.Table("schema_attribute", FIA.metadata,
    sa.Column("schema_id", sa.ForeignKey("schema.id"), nullable=False),
    sa.Column("attribute_id", sa.ForeignKey("attribute.id"), nullable=False),
    sa.PrimaryKeyConstraint("schema_id", "attribute_id")
    )
    
class Schema(FIA):
    """
    """
    __tablename__ = "schema"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    specification_id = sa.Column(sa.Integer, sa.ForeignKey("specification.id"),
                                 nullable=False)
    
    specification = orm.relation("Specification", uselist=False)
    
    attributes = orm.relation("Attribute", 
                              secondary=schema_attribute_table,
                              order_by="order")
    
    create_date = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    
    __table_args = (
        sa.UniqueConstraint("specification_id", "create_date"),
        {})

class Attribute(FIA):
    """
    """
    __tablename__ = "attribute"
    
    id = sa.Column(sa.Integer, primary_key=True) 
    
    name = sa.Column(sa.Unicode, nullable=False)
    
    title = sa.Column(sa.Unicode, nullable=False)
    
    description = sa.Column(sa.Text)
    
    type_id = sa.Column(sa.Integer, sa.ForeignKey("type.id"), nullable=False)
    
    type = orm.relation("Type", uselist=False)
    
    order = sa.Column(sa.Integer, nullable=False, default=1)
    
    hint_id = sa.Column(sa.Integer, sa.ForeignKey("hint.id"))
    
    schema_id = sa.Column(sa.Integer, sa.ForeignKey("schema.id"))
    
    vocabulary_id = sa.Column(sa.Integer, sa.ForeignKey("vocabulary.id"))
    
    is_searchable = sa.Column(sa.Boolean, nullable=False, default=False)
    
    is_required = sa.Column(sa.Boolean, nullable=False, default=False)
    
    is_inline_image = sa.Column(sa.Boolean)
    
    is_repeatable = sa.Column(sa.Boolean)
    
    minimum = sa.Column(sa.Integer)
    
    maximum = sa.Column(sa.Integer)
    
    width = sa.Column(sa.Integer)
    
    height = sa.Column(sa.Integer)
    
    url = sa.Column(sa.Unicode)
    
    comment = sa.Column(sa.Text)
    
    create_date = sa.Column(sa.DateTime, nullable=False, default=datetime.now) 
    
    
class Type(FIA):
    """
    """
    __tablename__ = "type"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    title = sa.Column(sa.Unicode, nullable=False, unique=True)
    
    description = sa.Column(sa.Text)
    
    
class Hint(FIA):
    """
    """
    __tablename__ = "hint"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    namespace = sa.Column(sa.Unicode, nullable=False, unique=True)
    
    
vocabulary_term_table = sa.Table("vocabulary_term", FIA.metadata,
    sa.Column("vocabulary_id", sa.Integer, sa.ForeignKey("vocabulary.id"),
              nullable=False),
    sa.Column("term_id", sa.Integer, sa.ForeignKey("term.id"),
              nullable=False),              
    sa.PrimaryKeyConstraint("vocabulary_id", "term_id")
    )

class Vocabulary(FIA):
    """
    """
    __tablename__ = "vocabulary"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    name = sa.Column(sa.Unicode, nullable=False, index=True)
    
    
class Term(FIA):    
    """
    """
    __tablename__ = "term"
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    label = sa.Column(sa.Unicode)
    
    value = sa.Column(sa.Unicode, nullable=False)
    
    order = sa.Column(sa.Integer, nullable=False, default=1)

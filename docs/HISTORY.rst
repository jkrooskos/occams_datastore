================================================================================
Change Log
================================================================================

--------------------------------------------------------------------------------
0.4.2 (2011-08-25)
--------------------------------------------------------------------------------

- General
    - Fixed ON DELETE settings for value tables to cascade properly.

--------------------------------------------------------------------------------
0.4.1 (2011-08-16)
--------------------------------------------------------------------------------

- General
    - Disabled default values, they were causing complications with data entry.
    - Fixed: base_schema not being imported correctly.
    
     
--------------------------------------------------------------------------------
0.4.0 (2011-07-29)
--------------------------------------------------------------------------------

*Goal*: History support.

- General
    - Rebranded package as *DataStore* (from ``Datastore``)
    - Form/Data history functionality implemented.
    - Now includes comprehensive unit testing suite.
    - All managers now adopt the zope adapter paradigm. This means that
        ``getUtlity`` calls have been removed from the source code. Most notably,
        ``DataStore`` only takes a ``ScopedSession`` instance (as opposed to a
        string)
    - Removed dependency on ``z3c.saconfig``
    - Manager specifications updated with time-based parameters (for history)
    - Removed dependencies on zope/plone UI-specific components such as
        ``z3c.form``, ``plone.dexterity``, ``plone.autoform`` etc. The reason 
        for this change is to  make DataStore it's own stand-alone utility that 
        can be used command line or as a plug-in in to other frameworks. This 
        approach will be further pursued in the coming versions of DataStore.
     
- Extensions
    - Clinical-based components moved to their own packages.
        
- Form
    - New form paradigm adopted: fieldsets are considered inline objects (
        or subforms, whichever way you prefer to look at it). This removes
        the heavy dependence on `plone.autoform` and instead allows for
        rich annotation of the form without the dependence of Zope-specific
        UI elements.
    - Widgets will be deprecated in a later version
    - Created new form directives (rather than using embedded
        ``zope.schema.Attribute`` instances)
    - Added batching facilities
    
- Database
    - Uses ``sqlalchemy.types.Enum`` for simple selection values in tables 
        (such as type or class storage type)
    - Floats have been converted to Decimal type (to control precision)
    - Choices are now direct constraints of the Attribute.
    - Overhauled model structures with standard attributes such as 
        ``name``/``title``/``description``/``create_date``/``modify_date``/
        ``remove_date``
    - ``Instance`` object names renamed to ``Entity``
    - Time-typed values no longer supported (only Datetime or Date)
    - Infrastructure changed to support for user changes (paper-trail)
    - Infrastructure changed to support external resource objects storage type.
    - Infrastructure changed to support external table storage type.
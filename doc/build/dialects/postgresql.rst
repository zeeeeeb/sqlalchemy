.. _postgresql_toplevel:

PostgreSQL
==========

.. automodule:: sqlalchemy.dialects.postgresql.base

PostgreSQL Data Types and Custom SQL Constructs
------------------------------------------------

As with all SQLAlchemy dialects, all UPPERCASE types that are known to be
valid with PostgreSQL are importable from the top level dialect, whether
they originate from :mod:`sqlalchemy.types` or from the local dialect::

    from sqlalchemy.dialects.postgresql import \
        ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
        DOUBLE_PRECISION, ENUM, FLOAT, HSTORE, INET, INTEGER, \
        INTERVAL, JSON, JSONB, MACADDR, MONEY, NUMERIC, OID, REAL, SMALLINT, TEXT, \
        TIME, TIMESTAMP, UUID, VARCHAR, INT4RANGE, INT8RANGE, NUMRANGE, \
        DATERANGE, TSRANGE, TSTZRANGE, TSVECTOR

Types which are specific to PostgreSQL, or have PostgreSQL-specific
construction arguments, are as follows:

.. currentmodule:: sqlalchemy.dialects.postgresql

.. autoclass:: aggregate_order_by

.. autoclass:: array

.. autoclass:: ARRAY
    :members: __init__, Comparator

.. autofunction:: array_agg

.. autofunction:: Any

.. autofunction:: All

.. autoclass:: BIT

.. autoclass:: BYTEA
    :members: __init__

.. autoclass:: CIDR


.. autoclass:: DOUBLE_PRECISION
    :members: __init__


.. autoclass:: ENUM
    :members: __init__, create, drop


.. autoclass:: HSTORE
    :members:


.. autoclass:: hstore
    :members:


.. autoclass:: INET

.. autoclass:: INTERVAL
    :members: __init__

.. autoclass:: JSON
    :members:

.. autoclass:: JSONB
    :members:

.. autoclass:: MACADDR

.. autoclass:: MONEY

.. autoclass:: OID

.. autoclass:: REAL
    :members: __init__

.. autoclass:: REGCLASS

.. autoclass:: TSVECTOR

.. autoclass:: UUID
    :members: __init__


Range Types
~~~~~~~~~~~

The new range column types found in PostgreSQL 9.2 onwards are
catered for by the following types:

.. autoclass:: INT4RANGE


.. autoclass:: INT8RANGE


.. autoclass:: NUMRANGE


.. autoclass:: DATERANGE


.. autoclass:: TSRANGE


.. autoclass:: TSTZRANGE


The types above get most of their functionality from the following
mixin:

.. autoclass:: sqlalchemy.dialects.postgresql.ranges.RangeOperators
    :members:

.. warning::

  The range type DDL support should work with any PostgreSQL DBAPI
  driver, however the data types returned may vary. If you are using
  ``psycopg2``, it's recommended to upgrade to version 2.5 or later
  before using these column types.

When instantiating models that use these column types, you should pass
whatever data type is expected by the DBAPI driver you're using for
the column type. For ``psycopg2`` these are
``psycopg2.extras.NumericRange``,
``psycopg2.extras.DateRange``,
``psycopg2.extras.DateTimeRange`` and
``psycopg2.extras.DateTimeTZRange`` or the class you've
registered with ``psycopg2.extras.register_range``.

For example:

.. code-block:: python

  from psycopg2.extras import DateTimeRange
  from sqlalchemy.dialects.postgresql import TSRANGE

  class RoomBooking(Base):

      __tablename__ = 'room_booking'

      room = Column(Integer(), primary_key=True)
      during = Column(TSRANGE())

  booking = RoomBooking(
      room=101,
      during=DateTimeRange(datetime(2013, 3, 23), None)
  )

MultiRange Types
~~~~~~~~~~~

The new MultiRange column types found in PostgreSQL 14 onwards are
catered for by the following types:

.. autoclass:: INT4MULTIRANGE


.. autoclass:: INT8MULTIRANGE


.. autoclass:: NUMMULTIRANGE


.. autoclass:: DATEMULTIRANGE


.. autoclass:: TSMULTIRANGE


.. autoclass:: TSTZMULTIRANGE


The types above get most of their functionality from the following
mixin:

.. autoclass:: sqlalchemy.dialects.postgresql.ranges.RangeOperators
    :members:

.. warning::

  The multirange type DDL is currently only supported by the
  psycopg (a.k.a psycopg3) PostgreSQL DBAPI driver.

When instantiating models that use these column types, you should pass
whatever data type is expected by the DBAPI driver you're using for
the column type. 

For example:

.. code-block:: python

  from psycopg.types.range import Range
  from pscyopg.types.multirange import Multirange
  from sqlalchemy.dialects.postgresql import TSMULTIRANGE

  class RoomBooking(Base):

      __tablename__ = 'room_booking'

      room = Column(Integer(), primary_key=True)
      during = Column(TSMULTIRANGE())

  booking = RoomBooking(
      room=101,
      during=Multirange([
          Range(datetime(2013, 3, 23), datetime(2014, 3, 22)),
          Range(datetime(2015, 1, 1), None)
      ])


PostgreSQL Constraint Types
---------------------------

SQLAlchemy supports PostgreSQL EXCLUDE constraints via the
:class:`ExcludeConstraint` class:

.. autoclass:: ExcludeConstraint
   :members: __init__

For example::

  from sqlalchemy.dialects.postgresql import ExcludeConstraint, TSRANGE

  class RoomBooking(Base):

      __tablename__ = 'room_booking'

      room = Column(Integer(), primary_key=True)
      during = Column(TSRANGE())

      __table_args__ = (
          ExcludeConstraint(('room', '='), ('during', '&&')),
      )

PostgreSQL DML Constructs
-------------------------

.. autofunction:: sqlalchemy.dialects.postgresql.insert

.. autoclass:: sqlalchemy.dialects.postgresql.Insert
  :members:

.. _postgresql_psycopg2:

psycopg2
--------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg2

.. _postgresql_psycopg:

psycopg
--------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg

pg8000
------

.. automodule:: sqlalchemy.dialects.postgresql.pg8000

.. _dialect-postgresql-asyncpg:

asyncpg
-------

.. automodule:: sqlalchemy.dialects.postgresql.asyncpg

psycopg2cffi
------------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg2cffi

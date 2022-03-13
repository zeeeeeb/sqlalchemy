"""Requirements specific to SQLAlchemy's own unit tests.


"""

from sqlalchemy import exc
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql import text
from sqlalchemy.testing import exclusions
from sqlalchemy.testing.exclusions import against
from sqlalchemy.testing.exclusions import fails_if
from sqlalchemy.testing.exclusions import fails_on
from sqlalchemy.testing.exclusions import fails_on_everything_except
from sqlalchemy.testing.exclusions import LambdaPredicate
from sqlalchemy.testing.exclusions import NotPredicate
from sqlalchemy.testing.exclusions import only_if
from sqlalchemy.testing.exclusions import only_on
from sqlalchemy.testing.exclusions import skip_if
from sqlalchemy.testing.exclusions import SpecPredicate
from sqlalchemy.testing.exclusions import succeeds_if
from sqlalchemy.testing.requirements import SuiteRequirements


def no_support(db, reason):
    return SpecPredicate(db, description=reason)


def exclude(db, op, spec, description=None):
    return SpecPredicate(db, op, spec, description=description)


class DefaultRequirements(SuiteRequirements):
    @property
    def deferrable_or_no_constraints(self):
        """Target database must support deferrable constraints."""

        return skip_if(
            [
                no_support("mysql", "not supported by database"),
                no_support("mariadb", "not supported by database"),
                no_support("mssql", "not supported by database"),
            ]
        )

    @property
    def check_constraints(self):
        """Target database must support check constraints."""

        return exclusions.open()

    @property
    def enforces_check_constraints(self):
        """Target database must also enforce check constraints."""

        return self.check_constraints + fails_on(
            self._mysql_check_constraints_dont_exist,
            "check constraints don't enforce on MySQL, MariaDB<10.2",
        )

    @property
    def named_constraints(self):
        """target database must support names for constraints."""

        return exclusions.open()

    @property
    def implicitly_named_constraints(self):
        """target database must apply names to unnamed constraints."""

        return skip_if([no_support("sqlite", "not supported by database")])

    @property
    def foreign_keys(self):
        """Target database must support foreign keys."""

        return skip_if(no_support("sqlite", "not supported by database"))

    @property
    def foreign_key_constraint_name_reflection(self):
        return fails_if(
            lambda config: against(config, ["mysql", "mariadb"])
            and not self._mysql_80(config)
            and not self._mariadb_105(config)
        )

    @property
    def table_ddl_if_exists(self):
        """target platform supports IF NOT EXISTS / IF EXISTS for tables."""

        return only_on(["postgresql", "mysql", "mariadb", "sqlite"])

    @property
    def index_ddl_if_exists(self):
        """target platform supports IF NOT EXISTS / IF EXISTS for indexes."""

        # mariadb but not mysql, tested up to mysql 8
        return only_on(["postgresql", "mariadb", "sqlite"])

    @property
    def on_update_cascade(self):
        """target database must support ON UPDATE..CASCADE behavior in
        foreign keys."""

        return skip_if(
            ["sqlite", "oracle"],
            "target backend %(doesnt_support)s ON UPDATE CASCADE",
        )

    @property
    def non_updating_cascade(self):
        """target database must *not* support ON UPDATE..CASCADE behavior in
        foreign keys."""

        return fails_on_everything_except("sqlite", "oracle") + skip_if(
            "mssql"
        )

    @property
    def recursive_fk_cascade(self):
        """target database must support ON DELETE CASCADE on a self-referential
        foreign key"""

        return skip_if(["mssql"])

    @property
    def deferrable_fks(self):
        """target database must support deferrable fks"""

        return only_on(["oracle", "postgresql"])

    @property
    def foreign_key_constraint_option_reflection_ondelete(self):
        return only_on(
            ["postgresql", "mysql", "mariadb", "sqlite", "oracle", "mssql"]
        )

    @property
    def fk_constraint_option_reflection_ondelete_restrict(self):
        return only_on(["postgresql", "sqlite", self._mysql_80])

    @property
    def fk_constraint_option_reflection_ondelete_noaction(self):
        return only_on(["postgresql", "mysql", "mariadb", "sqlite", "mssql"])

    @property
    def foreign_key_constraint_option_reflection_onupdate(self):
        return only_on(["postgresql", "mysql", "mariadb", "sqlite", "mssql"])

    @property
    def fk_constraint_option_reflection_onupdate_restrict(self):
        return only_on(["postgresql", "sqlite", self._mysql_80])

    @property
    def comment_reflection(self):
        return only_on(["postgresql", "mysql", "mariadb", "oracle"])

    @property
    def unbounded_varchar(self):
        """Target database must support VARCHAR with no length"""

        return skip_if(
            ["oracle", "mysql", "mariadb"],
            "not supported by database",
        )

    @property
    def boolean_col_expressions(self):
        """Target database must support boolean expressions as columns"""
        return skip_if(
            [
                no_support("oracle", "not supported by database"),
                no_support("mssql", "not supported by database"),
            ]
        )

    @property
    def non_native_boolean_unconstrained(self):
        """target database is not native boolean and allows arbitrary integers
        in it's "bool" column"""

        return skip_if(
            [
                LambdaPredicate(
                    lambda config: against(config, "mssql"),
                    "SQL Server drivers / odbc seem to change "
                    "their mind on this",
                ),
                LambdaPredicate(
                    lambda config: config.db.dialect.supports_native_boolean,
                    "native boolean dialect",
                ),
            ]
        )

    @property
    def qmark_paramstyle(self):
        return only_on(["sqlite", "+pyodbc"])

    @property
    def named_paramstyle(self):
        return only_on(["sqlite", "oracle+cx_oracle"])

    @property
    def format_paramstyle(self):
        return only_on(
            [
                "mysql+mysqldb",
                "mysql+pymysql",
                "mysql+cymysql",
                "mysql+mysqlconnector",
                "mariadb+mysqldb",
                "mariadb+pymysql",
                "mariadb+cymysql",
                "mariadb+mysqlconnector",
                "postgresql+asyncpg",
                "postgresql+pg8000",
            ]
        )

    @property
    def pyformat_paramstyle(self):
        return only_on(
            [
                "postgresql+psycopg",
                "postgresql+psycopg2",
                "postgresql+psycopg2cffi",
                "mysql+mysqlconnector",
                "mysql+pymysql",
                "mysql+cymysql",
                "mariadb+mysqlconnector",
                "mariadb+pymysql",
                "mariadb+cymysql",
                "mssql+pymssql",
            ]
        )

    @property
    def no_quoting_special_bind_names(self):
        """Target database will quote bound parameter names, doesn't support
        EXPANDING"""

        return skip_if(["oracle"])

    @property
    def temporary_tables(self):
        """target database supports temporary tables"""
        return skip_if([self._sqlite_file_db], "not supported (?)")

    @property
    def temp_table_reflection(self):
        return self.temporary_tables

    @property
    def temp_table_reflect_indexes(self):
        return skip_if(["mssql", self._sqlite_file_db], "not supported (?)")

    @property
    def reflectable_autoincrement(self):
        """Target database must support tables that can automatically generate
        PKs assuming they were reflected.

        this is essentially all the DBs in "identity" plus PostgreSQL, which
        has SERIAL support.  Oracle requires the Sequence
        to be explicitly added, including if the table was reflected.
        """
        return skip_if(["oracle"], "not supported by database")

    @property
    def non_broken_binary(self):
        """target DBAPI must work fully with binary values"""

        # see https://github.com/pymssql/pymssql/issues/504
        return skip_if(["mssql+pymssql"])

    @property
    def binary_comparisons(self):
        """target database/driver can allow BLOB/BINARY fields to be compared
        against a bound parameter value.
        """
        return skip_if(["oracle", "mssql"], "not supported by database/driver")

    @property
    def binary_literals(self):
        """target backend supports simple binary literals, e.g. an
        expression like::

            SELECT CAST('foo' AS BINARY)

        Where ``BINARY`` is the type emitted from :class:`.LargeBinary`,
        e.g. it could be ``BLOB`` or similar.

        Basically fails on Oracle.

        """
        # adding mssql here since it doesn't support comparisons either,
        # have observed generally bad behavior with binary / mssql.

        return skip_if(["oracle", "mssql"], "not supported by database/driver")

    @property
    def tuple_in(self):
        def _sqlite_tuple_in(config):
            return against(
                config, "sqlite"
            ) and config.db.dialect.dbapi.sqlite_version_info >= (3, 15, 0)

        return only_on(
            ["mysql", "mariadb", "postgresql", _sqlite_tuple_in, "oracle"]
        )

    @property
    def tuple_in_w_empty(self):
        return self.tuple_in + skip_if(["oracle"])

    @property
    def independent_cursors(self):
        """Target must support simultaneous, independent database cursors
        on a single connection."""

        return skip_if(["mssql", "mysql", "mariadb"], "no driver support")

    @property
    def cursor_works_post_rollback(self):
        """Driver quirk where the cursor.fetchall() will work even if
        the connection has been rolled back.

        This generally refers to buffered cursors but also seems to work
        with cx_oracle, for example.

        """

        return skip_if(["+pyodbc"], "no driver support")

    @property
    def independent_connections(self):
        """
        Target must support simultaneous, independent database connections.
        """

        # This is also true of some configurations of UnixODBC and probably
        # win32 ODBC as well.
        return skip_if(
            [
                no_support(
                    "sqlite",
                    "independent connections disabled "
                    "when :memory: connections are used",
                ),
                exclude(
                    "mssql",
                    "<",
                    (9, 0, 0),
                    "SQL Server 2005+ is required for "
                    "independent connections",
                ),
            ]
        )

    @property
    def memory_process_intensive(self):
        """Driver is able to handle the memory tests which run in a subprocess
        and iterate through hundreds of connections

        """
        return skip_if(
            [
                no_support("oracle", "Oracle XE usually can't handle these"),
                no_support("mssql+pyodbc", "MS ODBC drivers struggle"),
                self._running_on_windows(),
            ]
        )

    @property
    def updateable_autoincrement_pks(self):
        """Target must support UPDATE on autoincrement/integer primary key."""

        return skip_if(["mssql"], "IDENTITY columns can't be updated")

    @property
    def isolation_level(self):
        return only_on(
            ("postgresql", "sqlite", "mysql", "mariadb", "mssql", "oracle"),
            "DBAPI has no isolation level support",
        )

    @property
    def autocommit(self):
        """target dialect supports 'AUTOCOMMIT' as an isolation_level"""

        return self.isolation_level + only_if(
            lambda config: "AUTOCOMMIT"
            in self.get_isolation_levels(config)["supported"]
        )

    @property
    def row_triggers(self):
        """Target must support standard statement-running EACH ROW triggers."""

        return skip_if(
            [
                # no access to same table
                no_support("mysql", "requires SUPER priv"),
                no_support("mariadb", "requires SUPER priv"),
                exclude("mysql", "<", (5, 0, 10), "not supported by database"),
            ]
        )

    @property
    def sequences_as_server_defaults(self):
        """Target database must support SEQUENCE as a server side default."""

        return self.sequences + only_on(
            ["postgresql", "mariadb", "oracle >= 18"],
            "doesn't support sequences as a server side default.",
        )

    @property
    def sql_expressions_inserted_as_primary_key(self):
        return only_if([self.returning, self.sqlite])

    @property
    def computed_columns_on_update_returning(self):
        return self.computed_columns + skip_if("oracle")

    @property
    def correlated_outer_joins(self):
        """Target must support an outer join to a subquery which
        correlates to the parent."""

        return skip_if(
            "oracle",
            'Raises "ORA-01799: a column may not be '
            'outer-joined to a subquery"',
        )

    @property
    def multi_table_update(self):
        return only_on(["mysql", "mariadb"], "Multi table update")

    @property
    def update_from(self):
        """Target must support UPDATE..FROM syntax"""

        return only_on(
            ["postgresql", "mssql", "mysql", "mariadb"],
            "Backend does not support UPDATE..FROM",
        )

    @property
    def delete_from(self):
        """Target must support DELETE FROM..FROM or DELETE..USING syntax"""
        return only_on(
            ["postgresql", "mssql", "mysql", "mariadb"],
            "Backend does not support DELETE..FROM",
        )

    @property
    def update_where_target_in_subquery(self):
        """Target must support UPDATE (or DELETE) where the same table is
        present in a subquery in the WHERE clause.

        This is an ANSI-standard syntax that apparently MySQL can't handle,
        such as::

            UPDATE documents SET flag=1 WHERE documents.title IN
                (SELECT max(documents.title) AS title
                    FROM documents GROUP BY documents.user_id
                )

        """
        return fails_if(
            self._mysql_not_mariadb_103,
            "MySQL error 1093 \"Can't specify target table "
            'for update in FROM clause", resolved by MariaDB 10.3',
        )

    @property
    def savepoints(self):
        """Target database must support savepoints."""

        return skip_if(
            ["sqlite", ("mysql", "<", (5, 0, 3))],
            "savepoints not supported",
        )

    @property
    def savepoints_w_release(self):
        return self.savepoints + skip_if(
            ["oracle", "mssql"],
            "database doesn't support release of savepoint",
        )

    @property
    def schemas(self):
        """Target database must support external schemas, and have one
        named 'test_schema'."""

        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self):
        """target system must support reflection of inter-schema foreign
        keys"""
        return only_on(["postgresql", "mysql", "mariadb", "mssql"])

    @property
    def implicit_default_schema(self):
        """target system has a strong concept of 'default' schema that can
        be referred to implicitly.

        basically, PostgreSQL.

        TODO: what does this mean?  all the backends have a "default"
        schema

        """
        return only_on(["postgresql"])

    @property
    def default_schema_name_switch(self):
        return only_on(["postgresql", "oracle"])

    @property
    def unique_constraint_reflection(self):
        return fails_on_everything_except(
            "postgresql", "mysql", "mariadb", "sqlite", "oracle"
        )

    @property
    def unique_constraint_reflection_no_index_overlap(self):
        return (
            self.unique_constraint_reflection
            + skip_if("mysql")
            + skip_if("mariadb")
            + skip_if("oracle")
        )

    @property
    def check_constraint_reflection(self):
        return fails_on_everything_except(
            "postgresql",
            "sqlite",
            "oracle",
            self._mysql_and_check_constraints_exist,
        )

    @property
    def indexes_with_expressions(self):
        return only_on(["postgresql", "sqlite>=3.9.0"])

    @property
    def temp_table_names(self):
        """target dialect supports listing of temporary table names"""

        return only_on(["sqlite", "oracle"]) + skip_if(self._sqlite_file_db)

    @property
    def temporary_views(self):
        """target database supports temporary views"""
        return only_on(["sqlite", "postgresql"]) + skip_if(
            self._sqlite_file_db
        )

    @property
    def table_value_constructor(self):
        return only_on(["postgresql", "mssql"])

    @property
    def update_nowait(self):
        """Target database must support SELECT...FOR UPDATE NOWAIT"""
        return skip_if(
            ["mssql", "mysql", "mariadb<10.3", "sqlite"],
            "no FOR UPDATE NOWAIT support",
        )

    @property
    def subqueries(self):
        """Target database must support subqueries."""
        return exclusions.open()

    @property
    def ctes(self):
        """Target database supports CTEs"""
        return only_on(
            [
                lambda config: against(config, "mysql")
                and (
                    (
                        config.db.dialect._is_mariadb
                        and config.db.dialect._mariadb_normalized_version_info
                        >= (10, 2)
                    )
                    or (
                        not config.db.dialect._is_mariadb
                        and config.db.dialect.server_version_info >= (8,)
                    )
                ),
                "mariadb>10.2",
                "postgresql",
                "mssql",
                "oracle",
                "sqlite>=3.8.3",
            ]
        )

    @property
    def ctes_with_update_delete(self):
        """target database supports CTES that ride on top of a normal UPDATE
        or DELETE statement which refers to the CTE in a correlated subquery.

        """
        return only_on(
            [
                "postgresql",
                "mssql",
                # "oracle" - oracle can do this but SQLAlchemy doesn't support
                # their syntax yet
            ]
        )

    @property
    def ctes_on_dml(self):
        """target database supports CTES which consist of INSERT, UPDATE
        or DELETE *within* the CTE, e.g. WITH x AS (UPDATE....)"""

        return only_if(["postgresql"])

    @property
    def mod_operator_as_percent_sign(self):
        """target database must use a plain percent '%' as the 'modulus'
        operator."""

        return only_if(
            ["mysql", "mariadb", "sqlite", "postgresql+psycopg2", "mssql"]
        )

    @property
    def intersect(self):
        """Target database must support INTERSECT or equivalent."""

        return fails_if(
            [self._mysql_not_mariadb_103],
            "no support for INTERSECT",
        )

    @property
    def except_(self):
        """Target database must support EXCEPT or equivalent (i.e. MINUS)."""
        return fails_if([self._mysql_not_mariadb_103], "no support for EXCEPT")

    @property
    def dupe_order_by_ok(self):
        """target db won't choke if ORDER BY specifies the same expression
        more than once

        """

        return skip_if("mssql")

    @property
    def order_by_col_from_union(self):
        """target database supports ordering by a column from a SELECT
        inside of a UNION

        E.g.  (SELECT id, ...) UNION (SELECT id, ...) ORDER BY id

        Fails on SQL Server

        """
        return fails_if("mssql")

    @property
    def parens_in_union_contained_select_w_limit_offset(self):
        """Target database must support parenthesized SELECT in UNION
        when LIMIT/OFFSET is specifically present.

        E.g. (SELECT ... LIMIT ..) UNION (SELECT .. OFFSET ..)

        This is known to fail on SQLite.

        """
        return fails_if("sqlite")

    @property
    def parens_in_union_contained_select_wo_limit_offset(self):
        """Target database must support parenthesized SELECT in UNION
        when OFFSET/LIMIT is specifically not present.

        E.g. (SELECT ...) UNION (SELECT ..)

        This is known to fail on SQLite.  It also fails on Oracle
        because without LIMIT/OFFSET, there is currently no step that
        creates an additional subquery.

        """
        return fails_if(["sqlite", "oracle"])

    @property
    def sql_expression_limit_offset(self):
        return (
            fails_if(
                ["mysql", "mariadb"],
                "Target backend can't accommodate full expressions in "
                "OFFSET or LIMIT",
            )
            + self.offset
        )

    @property
    def window_functions(self):
        return only_if(
            [
                "postgresql>=8.4",
                "mssql",
                "oracle",
                "sqlite>=3.25.0",
                "mysql>=8",
                "mariadb>=10.2",
            ],
            "Backend does not support window functions",
        )

    @property
    def two_phase_transactions(self):
        """Target database must support two-phase transactions."""

        def pg_prepared_transaction(config):
            if not against(config, "postgresql"):
                return True

            with config.db.connect() as conn:
                try:
                    num = conn.scalar(
                        text(
                            "select cast(setting AS integer) from pg_settings "
                            "where name = 'max_prepared_transactions'"
                        )
                    )
                except exc.OperationalError:
                    return False
                else:
                    return num > 0

        return skip_if(
            [
                no_support("mssql", "two-phase xact not supported by drivers"),
                no_support(
                    "sqlite", "two-phase xact not supported by database"
                ),
                # in Ia3cbbf56d4882fcc7980f90519412f1711fae74d
                # we are evaluating which modern MySQL / MariaDB versions
                # can handle two-phase testing without too many problems
                # no_support(
                #     "mysql",
                #    "recent MySQL communiity editions have too many issues "
                #    "(late 2016), disabling for now",
                # ),
                NotPredicate(
                    LambdaPredicate(
                        pg_prepared_transaction,
                        "max_prepared_transactions not available or zero",
                    )
                ),
            ]
        )

    @property
    def two_phase_recovery(self):
        return self.two_phase_transactions + (
            skip_if(
                ["mysql", "mariadb"],
                "still can't get recover to work w/ MariaDB / MySQL",
            )
            + skip_if("oracle", "recovery not functional")
        )

    @property
    def views(self):
        """Target database must support VIEWs."""

        return skip_if("drizzle", "no VIEW support")

    @property
    def empty_strings_varchar(self):
        """
        target database can persist/return an empty string with a varchar.
        """

        return fails_if(
            ["oracle"], "oracle converts empty strings to a blank space"
        )

    @property
    def empty_strings_text(self):
        """target database can persist/return an empty string with an
        unbounded text."""

        return fails_if(
            ["oracle"], "oracle converts empty strings to a blank space"
        )

    @property
    def string_type_isnt_subtype(self):
        """target dialect does not have a dialect-specific subtype for String.

        This is used for a special type expression test which wants to
        test the compiler with a subclass of String, where we don't want
        the dialect changing that type when we grab the 'impl'.

        """

        def go(config):
            return (
                sqltypes.String().dialect_impl(config.db.dialect).__class__
                is sqltypes.String
            )

        return only_if(go)

    @property
    def empty_inserts_executemany(self):
        # waiting on https://jira.mariadb.org/browse/CONPY-152
        return skip_if(["mariadb+mariadbconnector"]) + self.empty_inserts

    @property
    def expressions_against_unbounded_text(self):
        """target database supports use of an unbounded textual field in a
        WHERE clause."""

        return fails_if(
            ["oracle"],
            "ORA-00932: inconsistent datatypes: expected - got CLOB",
        )

    @property
    def unicode_connections(self):
        """
        Target driver must support some encoding of Unicode across the wire.

        """
        return exclusions.open()

    @property
    def unicode_ddl(self):
        """Target driver must support some degree of non-ascii symbol names."""

        return skip_if(
            [
                no_support("mssql+pymssql", "no FreeTDS support"),
            ]
        )

    @property
    def symbol_names_w_double_quote(self):
        """Target driver can create tables with a name like 'some " table'"""

        return skip_if(
            [no_support("oracle", "ORA-03001: unimplemented feature")]
        )

    @property
    def emulated_lastrowid(self):
        """ "target dialect retrieves cursor.lastrowid or an equivalent
        after an insert() construct executes.
        """
        return fails_on_everything_except(
            "mysql",
            "mariadb",
            "sqlite+aiosqlite",
            "sqlite+pysqlite",
            "sqlite+pysqlcipher",
            "mssql",
        )

    @property
    def emulated_lastrowid_even_with_sequences(self):
        """ "target dialect retrieves cursor.lastrowid or an equivalent
        after an insert() construct executes, even if the table has a
        Sequence on it.
        """
        return fails_on_everything_except(
            "mysql",
            "mariadb",
            "sqlite+pysqlite",
            "sqlite+pysqlcipher",
        )

    @property
    def dbapi_lastrowid(self):
        """ "target backend includes a 'lastrowid' accessor on the DBAPI
        cursor object.

        """
        return skip_if("mssql+pymssql", "crashes on pymssql") + only_on(
            [
                "mysql",
                "mariadb",
                "sqlite+pysqlite",
                "sqlite+aiosqlite",
                "sqlite+pysqlcipher",
                "mssql",
            ]
        )

    @property
    def nullsordering(self):
        """Target backends that support nulls ordering."""
        return fails_on_everything_except(
            "postgresql", "oracle", "sqlite >= 3.30.0"
        )

    @property
    def reflects_pk_names(self):
        """Target driver reflects the name of primary key constraints."""

        return fails_on_everything_except(
            "postgresql", "oracle", "mssql", "sqlite"
        )

    @property
    def nested_aggregates(self):
        """target database can select an aggregate from a subquery that's
        also using an aggregate"""

        return skip_if(["mssql", "sqlite"])

    @property
    def tuple_valued_builtin_functions(self):
        return only_on(
            lambda config: self._sqlite_json(config)
            or against(config, "postgresql")
        )

    @property
    def array_type(self):
        return only_on(
            [
                lambda config: against(config, "postgresql")
                and not against(config, "+pg8000")
            ]
        )

    @property
    def json_type(self):
        return only_on(
            [
                lambda config: against(config, "mysql")
                and (
                    (
                        not config.db.dialect._is_mariadb
                        and against(config, "mysql >= 5.7")
                    )
                    or (
                        config.db.dialect._mariadb_normalized_version_info
                        >= (10, 2, 7)
                    )
                ),
                "mariadb>=10.2.7",
                "postgresql >= 9.3",
                self._sqlite_json,
                "mssql",
            ]
        )

    @property
    def json_index_supplementary_unicode_element(self):
        # for sqlite see https://bugs.python.org/issue38749
        return skip_if(
            [
                lambda config: against(config, "mysql")
                and config.db.dialect._is_mariadb,
                "mariadb",
                "sqlite",
            ]
        )

    @property
    def legacy_unconditional_json_extract(self):
        """Backend has a JSON_EXTRACT or similar function that returns a
        valid JSON string in all cases.

        Used to test a legacy feature and is not needed.

        """
        return self.json_type + only_on(
            ["postgresql", "mysql", "mariadb", "sqlite"]
        )

    def _sqlite_file_db(self, config):
        return against(config, "sqlite") and config.db.dialect._is_url_file_db(
            config.db.url
        )

    def _sqlite_memory_db(self, config):
        return against(
            config, "sqlite"
        ) and not config.db.dialect._is_url_file_db(config.db.url)

    def _sqlite_json(self, config):
        if not against(config, "sqlite >= 3.9"):
            return False
        else:
            with config.db.connect() as conn:
                try:
                    return (
                        conn.exec_driver_sql(
                            """select json_extract('{"foo": "bar"}', """
                            """'$."foo"')"""
                        ).scalar()
                        == "bar"
                    )
                except exc.DBAPIError:
                    return False

    @property
    def sqlite_memory(self):
        return only_on(self._sqlite_memory_db)

    @property
    def reflects_json_type(self):
        return only_on(
            [
                lambda config: against(config, "mysql >= 5.7")
                and not config.db.dialect._is_mariadb,
                "postgresql >= 9.3",
                "sqlite >= 3.9",
            ]
        )

    @property
    def json_array_indexes(self):
        return self.json_type

    @property
    def datetime_literals(self):
        """target dialect supports rendering of a date, time, or datetime as a
        literal string, e.g. via the TypeEngine.literal_processor() method.

        """

        return fails_on_everything_except("sqlite")

    @property
    def datetime(self):
        """target dialect supports representation of Python
        datetime.datetime() objects."""

        return exclusions.open()

    @property
    def datetime_implicit_bound(self):
        """target dialect when given a datetime object will bind it such
        that the database server knows the object is a datetime, and not
        a plain string.

        """

        # mariadbconnector works.  pyodbc we dont know, not supported in
        # testing.
        return exclusions.fails_on(
            [
                "+mysqldb",
                "+pymysql",
                "+asyncmy",
                "+mysqlconnector",
                "+cymysql",
                "+aiomysql",
            ]
        )

    @property
    def datetime_timezone(self):
        return exclusions.only_on("postgresql")

    @property
    def time_timezone(self):
        return exclusions.only_on("postgresql") + exclusions.skip_if("+pg8000")

    @property
    def datetime_microseconds(self):
        """target dialect supports representation of Python
        datetime.datetime() with microsecond objects."""

        return skip_if(["mssql", "mysql", "mariadb", "oracle"])

    @property
    def timestamp_microseconds(self):
        """target dialect supports representation of Python
        datetime.datetime() with microsecond objects but only
        if TIMESTAMP is used."""

        return only_on(["oracle"])

    @property
    def timestamp_microseconds_implicit_bound(self):
        return self.timestamp_microseconds + exclusions.fails_on(["oracle"])

    @property
    def datetime_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1900) values."""

        return succeeds_if(["sqlite", "postgresql"])

    @property
    def date(self):
        """target dialect supports representation of Python
        datetime.date() objects."""

        return exclusions.open()

    @property
    def date_coerces_from_datetime(self):
        """target dialect accepts a datetime object as the target
        of a date column."""

        # does not work as of pyodbc 4.0.22
        return fails_on("mysql+mysqlconnector") + skip_if("mssql+pyodbc")

    @property
    def date_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1900) values."""

        return succeeds_if(["sqlite", "postgresql"])

    @property
    def time(self):
        """target dialect supports representation of Python
        datetime.time() objects."""

        return skip_if(["oracle"])

    @property
    def time_microseconds(self):
        """target dialect supports representation of Python
        datetime.time() with microsecond objects."""

        return skip_if(["mssql", "mysql", "mariadb", "oracle"])

    @property
    def precision_numerics_general(self):
        """target backend has general support for moderately high-precision
        numerics."""
        return exclusions.open()

    @property
    def precision_numerics_enotation_small(self):
        """target backend supports Decimal() objects using E notation
        to represent very small values."""
        # NOTE: this exclusion isn't used in current tests.
        return exclusions.open()

    @property
    def precision_numerics_many_significant_digits(self):
        """target backend supports values with many digits on both sides,
        such as 319438950232418390.273596, 87673.594069654243

        """

        return fails_if(
            [
                ("sqlite", None, None, "SQLite numeric limitation"),
            ]
        )

    @property
    def cast_precision_numerics_many_significant_digits(self):
        """same as precision_numerics_many_significant_digits but within the
        context of a CAST statement (hello MySQL)

        """
        return self.precision_numerics_many_significant_digits + fails_if(
            "mysql"
        )

    @property
    def precision_numerics_retains_significant_digits(self):
        """A precision numeric type will return empty significant digits,
        i.e. a value such as 10.000 will come back in Decimal form with
        the .000 maintained."""

        return fails_if(
            [
                ("oracle", None, None, "driver doesn't do this automatically"),
            ]
        )

    @property
    def numeric_received_as_decimal_untyped(self):
        return fails_on(
            "sqlite",
            "sqlite doesn't return Decimal objects without special handlers",
        )

    @property
    def infinity_floats(self):
        return fails_on_everything_except(
            "sqlite",
            "postgresql+psycopg2",
            "postgresql+asyncpg",
            "postgresql+psycopg",
        ) + skip_if(
            "postgresql+pg8000", "seems to work on pg14 only, not earlier?"
        )

    @property
    def precision_generic_float_type(self):
        """target backend will return native floating point numbers with at
        least seven decimal places when using the generic Float type."""

        return fails_if(
            [
                (
                    "mysql",
                    None,
                    None,
                    "mysql FLOAT type only returns 4 decimals",
                ),
                (
                    "mariadb",
                    None,
                    None,
                    "mysql FLOAT type only returns 4 decimals",
                ),
            ]
        )

    @property
    def implicit_decimal_binds(self):
        """target backend will return a selected Decimal as a Decimal, not
        a string.

        e.g.::

            expr = decimal.Decimal("15.7563")

            value = e.scalar(
                select(literal(expr))
            )

            assert value == expr

        See :ticket:`4036`

        """

        return exclusions.open()

    @property
    def fetch_null_from_numeric(self):
        return skip_if(("mssql+pyodbc", None, None, "crashes due to bug #351"))

    @property
    def duplicate_key_raises_integrity_error(self):
        return exclusions.open()

    def _has_pg_extension(self, name):
        def check(config):
            if not against(config, "postgresql"):
                return False
            with config.db.connect() as conn:
                count = conn.exec_driver_sql(
                    "SELECT count(*) FROM pg_extension "
                    "WHERE extname='%s'" % name
                ).scalar()
            return bool(count)

        return only_if(check, "needs %s extension" % name)

    @property
    def hstore(self):
        return self._has_pg_extension("hstore")

    @property
    def btree_gist(self):
        return self._has_pg_extension("btree_gist")

    @property
    def range_types(self):
        def check_range_types(config):
            if not self.psycopg_compatibility.enabled:
                return False
            try:
                with config.db.connect() as conn:
                    conn.exec_driver_sql("select '[1,2)'::int4range;").scalar()
                return True
            except Exception:
                return False

        return only_if(check_range_types)

    @property
    def async_dialect(self):
        """dialect makes use of await_() to invoke operations on the DBAPI."""

        return only_on(
            LambdaPredicate(
                lambda config: config.db.dialect.is_async,
                "Async dialect required",
            )
        )

    @property
    def oracle_test_dblink(self):
        return skip_if(
            lambda config: not config.file_config.has_option(
                "sqla_testing", "oracle_db_link"
            ),
            "oracle_db_link option not specified in config",
        )

    @property
    def postgresql_test_dblink(self):
        return skip_if(
            lambda config: not config.file_config.has_option(
                "sqla_testing", "postgres_test_db_link"
            ),
            "postgres_test_db_link option not specified in config",
        )

    @property
    def postgresql_jsonb(self):
        return only_on("postgresql >= 9.4") + skip_if(
            lambda config: config.db.dialect.driver == "pg8000"
            and config.db.dialect._dbapi_version <= (1, 10, 1)
        )

    @property
    def native_hstore(self):
        return self.psycopg_compatibility

    @property
    def psycopg2_compatibility(self):
        return only_on(["postgresql+psycopg2", "postgresql+psycopg2cffi"])

    @property
    def psycopg_compatibility(self):
        return only_on(
            [
                "postgresql+psycopg2",
                "postgresql+psycopg2cffi",
                "postgresql+psycopg",
            ]
        )

    @property
    def psycopg_only_compatibility(self):
        return only_on(["postgresql+psycopg"])

    @property
    def psycopg_or_pg8000_compatibility(self):
        return only_on([self.psycopg_compatibility, "postgresql+pg8000"])

    @property
    def percent_schema_names(self):
        return skip_if(
            ["mysql+aiomysql", "mariadb+aiomysql"],
            "see pr https://github.com/aio-libs/aiomysql/pull/545",
        )

    @property
    def order_by_label_with_expression(self):
        return fails_if(
            [
                ("postgresql", None, None, "only simple labels allowed"),
                ("mssql", None, None, "only simple labels allowed"),
            ]
        )

    def get_order_by_collation(self, config):
        lookup = {
            # will raise without quoting
            "postgresql": "POSIX",
            # note MySQL databases need to be created w/ utf8mb4 charset
            # for the test suite
            "mysql": "utf8mb4_bin",
            "mariadb": "utf8mb4_bin",
            "sqlite": "NOCASE",
            # will raise *with* quoting
            "mssql": "Latin1_General_CI_AS",
        }
        try:
            return lookup[config.db.name]
        except KeyError:
            raise NotImplementedError()

    @property
    def skip_mysql_on_windows(self):
        """Catchall for a large variety of MySQL on Windows failures"""

        return skip_if(
            self._has_mysql_on_windows, "Not supported on MySQL + Windows"
        )

    @property
    def mssql_freetds(self):
        return only_on(["mssql+pymssql"])

    @property
    def ad_hoc_engines(self):
        return skip_if(self._sqlite_file_db)

    @property
    def no_asyncio(self):
        def go(config):
            return config.db.dialect.is_async

        return skip_if(go)

    @property
    def no_mssql_freetds(self):
        return self.mssql_freetds.not_()

    @property
    def pyodbc_fast_executemany(self):
        def has_fastexecutemany(config):
            if not against(config, "mssql+pyodbc"):
                return False
            if config.db.dialect._dbapi_version() < (4, 0, 19):
                return False
            with config.db.connect() as conn:
                drivername = conn.connection.connection.getinfo(
                    config.db.dialect.dbapi.SQL_DRIVER_NAME
                )
                # on linux this is something like 'libmsodbcsql-13.1.so.9.2'.
                # on Windows this is something like 'msodbcsql17.dll'.
                return "msodbc" in drivername

        return only_if(
            has_fastexecutemany, "only on pyodbc > 4.0.19 w/ msodbc driver"
        )

    @property
    def selectone(self):
        """target driver must support the literal statement 'select 1'"""
        return skip_if(["oracle"], "non-standard SELECT scalar syntax")

    @property
    def mysql_for_update(self):
        return skip_if(
            "mysql+mysqlconnector",
            "lock-sensitive operations crash on mysqlconnector",
        )

    @property
    def mysql_fsp(self):
        return only_if(["mysql >= 5.6.4", "mariadb"])

    @property
    def mysql_fully_case_sensitive(self):
        return only_if(self._has_mysql_fully_case_sensitive)

    @property
    def mysql_zero_date(self):
        def check(config):
            if not against(config, "mysql"):
                return False

            with config.db.connect() as conn:
                row = conn.exec_driver_sql(
                    "show variables like 'sql_mode'"
                ).first()
            return not row or "NO_ZERO_DATE" not in row[1]

        return only_if(check)

    @property
    def mysql_non_strict(self):
        def check(config):
            if not against(config, "mysql"):
                return False

            with config.db.connect() as conn:
                row = conn.exec_driver_sql(
                    "show variables like 'sql_mode'"
                ).first()
            return not row or "STRICT_TRANS_TABLES" not in row[1]

        return only_if(check)

    @property
    def mysql_ngram_fulltext(self):
        def check(config):
            return (
                against(config, "mysql")
                and not config.db.dialect._is_mariadb
                and config.db.dialect.server_version_info >= (5, 7)
            )

        return only_if(check)

    def _mysql_80(self, config):
        return (
            against(config, "mysql")
            and config.db.dialect._is_mysql
            and config.db.dialect.server_version_info >= (8,)
        )

    def _mariadb_102(self, config):
        return (
            against(config, ["mysql", "mariadb"])
            and config.db.dialect._is_mariadb
            and config.db.dialect._mariadb_normalized_version_info >= (10, 2)
        )

    def _mariadb_105(self, config):
        return (
            against(config, ["mysql", "mariadb"])
            and config.db.dialect._is_mariadb
            and config.db.dialect._mariadb_normalized_version_info >= (10, 5)
        )

    def _mysql_and_check_constraints_exist(self, config):
        # 1. we have mysql / mariadb and
        # 2. it enforces check constraints
        if exclusions.against(config, ["mysql", "mariadb"]):
            if config.db.dialect._is_mariadb:
                norm_version_info = (
                    config.db.dialect._mariadb_normalized_version_info
                )
                return norm_version_info >= (10, 2)
            else:
                norm_version_info = config.db.dialect.server_version_info
                return norm_version_info >= (8, 0, 16)
        else:
            return False

    def _mysql_check_constraints_exist(self, config):
        # 1. we dont have mysql / mariadb or
        # 2. we have mysql / mariadb that enforces check constraints
        return not exclusions.against(
            config, ["mysql", "mariadb"]
        ) or self._mysql_and_check_constraints_exist(config)

    def _mysql_check_constraints_dont_exist(self, config):
        # 1. we have mysql / mariadb and
        # 2. they dont enforce check constraints
        return not self._mysql_check_constraints_exist(config)

    def _mysql_not_mariadb_102(self, config):
        return (against(config, ["mysql", "mariadb"])) and (
            not config.db.dialect._is_mariadb
            or config.db.dialect._mariadb_normalized_version_info < (10, 2)
        )

    def _mysql_not_mariadb_103(self, config):
        return (against(config, ["mysql", "mariadb"])) and (
            not config.db.dialect._is_mariadb
            or config.db.dialect._mariadb_normalized_version_info < (10, 3)
        )

    def _mysql_not_mariadb_104(self, config):
        return (against(config, ["mysql", "mariadb"])) and (
            not config.db.dialect._is_mariadb
            or config.db.dialect._mariadb_normalized_version_info < (10, 4)
        )

    def _has_mysql_on_windows(self, config):
        with config.db.connect() as conn:
            return (
                against(config, ["mysql", "mariadb"])
            ) and config.db.dialect._detect_casing(conn) == 1

    def _has_mysql_fully_case_sensitive(self, config):
        with config.db.connect() as conn:
            return (
                against(config, "mysql")
                and config.db.dialect._detect_casing(conn) == 0
            )

    @property
    def postgresql_utf8_server_encoding(self):
        def go(config):
            if not against(config, "postgresql"):
                return False

            with config.db.connect() as conn:
                enc = conn.exec_driver_sql("show server_encoding").scalar()
                return enc.lower() == "utf8"

        return only_if(go)

    @property
    def cxoracle6_or_greater(self):
        return only_if(
            lambda config: against(config, "oracle+cx_oracle")
            and config.db.dialect.cx_oracle_ver >= (6,)
        )

    @property
    def oracle5x(self):
        return only_if(
            lambda config: against(config, "oracle+cx_oracle")
            and config.db.dialect.cx_oracle_ver < (6,)
        )

    @property
    def computed_columns(self):
        return skip_if(["postgresql < 12", "sqlite < 3.31", "mysql < 5.7"])

    @property
    def python_profiling_backend(self):
        return only_on([self._sqlite_memory_db])

    @property
    def computed_columns_stored(self):
        return self.computed_columns + skip_if(["oracle"])

    @property
    def computed_columns_virtual(self):
        return self.computed_columns + skip_if(["postgresql"])

    @property
    def computed_columns_default_persisted(self):
        return self.computed_columns + only_if("postgresql")

    @property
    def computed_columns_reflect_persisted(self):
        return self.computed_columns + skip_if("oracle")

    @property
    def regexp_match(self):
        return only_on(["postgresql", "mysql", "mariadb", "oracle", "sqlite"])

    @property
    def regexp_replace(self):
        return only_on(["postgresql", "mysql>=8", "mariadb", "oracle"])

    @property
    def supports_distinct_on(self):
        """If a backend supports the DISTINCT ON in a select"""
        return only_if(["postgresql"])

    @property
    def supports_for_update_of(self):
        return only_if(lambda config: config.db.dialect.supports_for_update_of)

    @property
    def sequences_in_other_clauses(self):
        """sequences allowed in WHERE, GROUP BY, HAVING, etc."""
        return skip_if(["mssql", "oracle"])

    @property
    def supports_lastrowid_for_expressions(self):
        """cursor.lastrowid works if an explicit SQL expression was used."""
        return only_on(["sqlite", "mysql", "mariadb"])

    @property
    def supports_sequence_for_autoincrement_column(self):
        """for mssql, autoincrement means IDENTITY, not sequence"""
        return skip_if("mssql")

    @property
    def supports_autoincrement_w_composite_pk(self):
        """integer autoincrement works for tables with composite primary
        keys"""
        return fails_if("sqlite")

    @property
    def identity_columns(self):
        return only_if(["postgresql >= 10", "oracle >= 12", "mssql"])

    @property
    def identity_columns_standard(self):
        return self.identity_columns + skip_if("mssql")

    @property
    def index_reflects_included_columns(self):
        return only_on(["postgresql >= 11", "mssql"])

    # mssql>= 11 -> >= MS_2012_VERSION

    @property
    def fetch_first(self):
        return only_on(
            ["postgresql", "mssql >= 11", "oracle >= 12", "mariadb >= 10.6"]
        )

    @property
    def fetch_percent(self):
        return only_on(["mssql >= 11", "oracle >= 12"])

    @property
    def fetch_ties(self):
        return only_on(
            [
                "postgresql >= 13",
                "mssql >= 11",
                "oracle >= 12",
                "mariadb >= 10.6",
            ]
        )

    @property
    def fetch_no_order_by(self):
        return only_on(["postgresql", "oracle >= 12", "mariadb >= 10.6"])

    @property
    def fetch_offset_with_options(self):
        # use together with fetch_first
        return skip_if("mssql")

    @property
    def fetch_expression(self):
        # use together with fetch_first
        return skip_if("mariadb")

    @property
    def autoincrement_without_sequence(self):
        return skip_if("oracle")

    @property
    def reflect_tables_no_columns(self):
        # so far sqlite, mariadb, mysql don't support this
        return only_on(["postgresql"])

    @property
    def json_deserializer_binary(self):
        "indicates if the json_deserializer function is called with bytes"
        return only_on(["postgresql+psycopg"])

    @property
    def mssql_filestream(self):
        "returns if mssql supports filestream"

        def check(config):
            with config.db.connect() as conn:
                res = conn.exec_driver_sql(
                    "SELECT [type] FROM sys.master_files WHERE "
                    "database_id = DB_ID() AND [type] = 2"
                ).scalar()
                return res is not None

        return only_on(["mssql"]) + only_if(check)

# -*- coding: utf-8 -*-

class Sqls():

    SELECT_GRANT_SCHEMAS = r"""
    select schema_name from v_grants_schemas order by schema_name
    """

    SELECT_GRANTS4DOWNLOAD = r"""
    select grant_command
    from v_grants_commands a
    where     1 = 1
      and grant_schema_name = :SOURCE_SCHEMA
      and target_schema_name like :TARGET_SCHEMA
    order by grant_objekt_name, target_schema_name
    """
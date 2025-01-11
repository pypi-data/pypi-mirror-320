# ext/declarative/__init__.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


from .extensions import AbstractConcreteBase
from .extensions import ConcreteBase
from .extensions import DeferredReflection
from ... import util
from ...orm.decl_api import as_declarative as _as_declarative
from ...orm.decl_api import declarative_base as _declarative_base
from ...orm.decl_api import DeclarativeMeta
from ...orm.decl_api import declared_attr
from ...orm.decl_api import has_inherited_table as _has_inherited_table
from ...orm.decl_api import synonym_for as _synonym_for


@util.moved_20(
    "The ``declarative_base()`` function is now available as "
    ":func:`sqlalchemy.orm.declarative_base`."
)
def declarative_base(*arg, **kw):
    return _declarative_base(*arg, **kw)


@util.moved_20(
    "The ``as_declarative()`` function is now available as "
    ":func:`sqlalchemy.orm.as_declarative`"
)
def as_declarative(*arg, **kw):
    return _as_declarative(*arg, **kw)


@util.moved_20(
    "The ``has_inherited_table()`` function is now available as "
    ":func:`sqlalchemy.orm.has_inherited_table`."
)
def has_inherited_table(*arg, **kw):
    return _has_inherited_table(*arg, **kw)


@util.moved_20(
    "The ``synonym_for()`` function is now available as "
    ":func:`sqlalchemy.orm.synonym_for`"
)
def synonym_for(*arg, **kw):
    return _synonym_for(*arg, **kw)


__all__ = [
    "declarative_base",
    "synonym_for",
    "has_inherited_table",
    "instrument_declarative",
    "declared_attr",
    "as_declarative",
    "ConcreteBase",
    "AbstractConcreteBase",
    "DeclarativeMeta",
    "DeferredReflection",
]

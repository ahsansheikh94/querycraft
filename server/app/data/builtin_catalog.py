"""
Hard-coded demo projects and schemas visible to every authenticated user.

Project IDs are fixed ObjectId hex strings so URLs stay stable and routes can
detect builtins without Mongo lookups.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from ..models.schema import Schema

# Reserve two fixed 24-char ObjectIds — unlikely to collide with random inserts.
PROJECT_ECOMMERCE = "f00000000000000000000001"
PROJECT_BLOG = "f00000000000000000000002"

BUILTIN_PROJECT_IDS = frozenset({PROJECT_ECOMMERCE, PROJECT_BLOG})

_FIXED_DT = datetime(2024, 1, 15, 12, 0, 0)
_FIXED_ISO = _FIXED_DT.isoformat() + "Z"


def _validate_oid(hex_str: str) -> str:
    ObjectId(hex_str)
    return hex_str


def is_builtin_project_id(project_id: str) -> bool:
    if not project_id:
        return False
    return project_id in BUILTIN_PROJECT_IDS


def _project_row(project_id: str, name: str, description: str) -> Dict[str, Any]:
    return {
        "id": project_id,
        "name": name,
        "description": description,
        "user_id": "__builtin__",
        "created_at": _FIXED_ISO,
        "updated_at": _FIXED_ISO,
    }


_PROJECT_DEFS: List[Dict[str, Any]] = [
    _project_row(
        PROJECT_ECOMMERCE,
        "Demo: E‑Commerce",
        "Sample orders, products, and customers — try natural language queries across multiple tables.",
    ),
    _project_row(
        PROJECT_BLOG,
        "Demo: Blog & CMS",
        "Posts, authors, and comments — good for joins and aggregations.",
    ),
]

_SCHEMA_ROWS: Dict[str, List[Dict[str, Any]]] = {
    PROJECT_ECOMMERCE: [
        {
            "id": _validate_oid("f10000000000000000000001"),
            "table_name": "customers",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "email", "type": "VARCHAR(255)", "unique": True, "not_null": True},
                    {"name": "name", "type": "VARCHAR(100)", "not_null": True},
                    {"name": "created_at", "type": "TIMESTAMP", "not_null": True},
                ]
            },
        },
        {
            "id": _validate_oid("f10000000000000000000002"),
            "table_name": "products",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "sku", "type": "VARCHAR(64)", "unique": True, "not_null": True},
                    {"name": "title", "type": "VARCHAR(200)", "not_null": True},
                    {"name": "price_cents", "type": "INTEGER", "not_null": True},
                    {"name": "stock", "type": "INTEGER", "not_null": True},
                ]
            },
        },
        {
            "id": _validate_oid("f10000000000000000000003"),
            "table_name": "orders",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "customer_id", "type": "INTEGER", "not_null": True},
                    {"name": "status", "type": "VARCHAR(32)", "not_null": True},
                    {"name": "placed_at", "type": "TIMESTAMP", "not_null": True},
                    {"name": "total_cents", "type": "INTEGER", "not_null": True},
                ]
            },
        },
        {
            "id": _validate_oid("f10000000000000000000004"),
            "table_name": "order_items",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "order_id", "type": "INTEGER", "not_null": True},
                    {"name": "product_id", "type": "INTEGER", "not_null": True},
                    {"name": "quantity", "type": "INTEGER", "not_null": True},
                    {"name": "unit_price_cents", "type": "INTEGER", "not_null": True},
                ]
            },
        },
    ],
    PROJECT_BLOG: [
        {
            "id": _validate_oid("f10000000000000000000011"),
            "table_name": "authors",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "display_name", "type": "VARCHAR(120)", "not_null": True},
                    {"name": "bio", "type": "TEXT"},
                ]
            },
        },
        {
            "id": _validate_oid("f10000000000000000000012"),
            "table_name": "posts",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "author_id", "type": "INTEGER", "not_null": True},
                    {"name": "slug", "type": "VARCHAR(160)", "unique": True, "not_null": True},
                    {"name": "title", "type": "VARCHAR(200)", "not_null": True},
                    {"name": "body", "type": "TEXT"},
                    {"name": "published_at", "type": "TIMESTAMP"},
                ]
            },
        },
        {
            "id": _validate_oid("f10000000000000000000013"),
            "table_name": "comments",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "post_id", "type": "INTEGER", "not_null": True},
                    {"name": "author_name", "type": "VARCHAR(120)", "not_null": True},
                    {"name": "body", "type": "TEXT", "not_null": True},
                    {"name": "created_at", "type": "TIMESTAMP", "not_null": True},
                ]
            },
        },
    ],
}


def builtin_project_count() -> int:
    return len(_PROJECT_DEFS)


def get_builtin_projects_public() -> List[Dict[str, Any]]:
    return [dict(p) for p in _PROJECT_DEFS]


def try_get_builtin_project_public(project_id: str) -> Optional[Dict[str, Any]]:
    for p in _PROJECT_DEFS:
        if p["id"] == project_id:
            return dict(p)
    return None


def get_builtin_project_stats(project_id: str) -> Dict[str, int]:
    rows = _SCHEMA_ROWS.get(project_id, [])
    return {
        "schema_count": len(rows),
        "query_count": 0,
    }


def attach_stats(project_public: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(project_public)
    out["stats"] = get_builtin_project_stats(out["id"])
    return out


def list_builtin_projects_with_stats() -> List[Dict[str, Any]]:
    return [attach_stats(p) for p in _PROJECT_DEFS]


def _materialize_schema(project_id: str, row: Dict[str, Any]) -> Schema:
    return Schema(
        project_id=project_id,
        table_name=row["table_name"],
        table_schema=row["table_schema"],
        _id=ObjectId(row["id"]),
        created_at=_FIXED_DT,
    )


def builtin_schema_instances(project_id: str) -> List[Schema]:
    rows = _SCHEMA_ROWS.get(project_id, [])
    return [_materialize_schema(project_id, row) for row in rows]


def merged_schema_instances(project_id: str) -> List[Schema]:
    """DB schemas plus builtin schemas when project id is a builtin."""
    db_schemas = Schema.find_by_project(project_id)
    if is_builtin_project_id(project_id):
        return builtin_schema_instances(project_id) + db_schemas
    return db_schemas


def merged_schema_public_dicts(project_id: str) -> List[Dict[str, Any]]:
    return [s.get_public_data() for s in merged_schema_instances(project_id)]


def merged_schema_summary(project_id: str) -> Dict[str, Any]:
    schemas = merged_schema_instances(project_id)
    tables = []
    for schema in schemas:
        cols = schema.table_schema.get("columns", [])
        tables.append(
            {
                "table_name": schema.table_name,
                "column_count": len(cols),
                "columns": [c["name"] for c in cols],
            }
        )
    return {"total_tables": len(schemas), "tables": tables}


def is_builtin_schema_id(schema_id: str) -> bool:
    if not schema_id:
        return False
    for rows in _SCHEMA_ROWS.values():
        for row in rows:
            if row["id"] == schema_id:
                return True
    return False


READONLY_MESSAGE = "Demo projects are read-only; duplicate them into your own project to edit."


def user_has_project_access(project_id: str, user_id: str) -> bool:
    """Builtin demos are readable by everyone; normal projects require ownership."""
    from ..models.project import Project

    if is_builtin_project_id(project_id):
        return True
    return Project.find_by_id(project_id, user_id) is not None


def find_schema_merged(schema_id: str, project_id: str) -> Optional[Schema]:
    for schema in merged_schema_instances(project_id):
        if str(schema._id) == schema_id:
            return schema
    return None

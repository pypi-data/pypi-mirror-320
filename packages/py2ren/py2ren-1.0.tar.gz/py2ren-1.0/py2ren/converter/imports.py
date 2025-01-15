from ast import ImportFrom, Import

from ..utils.iter import itermap


def _alias_as_expression(alias):
    if not alias.asname:
        return alias.name
    return "{} as {}".format(alias.name, alias.asname)


def as_expression(node):
    offset = " " * node.col_offset
    source = "import {}".format(
        ", ".join(itermap(_alias_as_expression, node.names))
    )
    if isinstance(node, ImportFrom):
        return offset + "from {}{} {}".format(
            "." * node.level,
            node.module if node.module else "",
            source
        )

    return offset + source


def create_store_import(names, lineno, col_offset=0):
    return ImportFrom(
        module="store",
        names=names,
        lineno=lineno,
        col_offset=col_offset,
        level=0,
    )


def as_store_import(imp, parent_module=None):
    store = "store"
    if parent_module:
        store += ".{}".format(parent_module)
    if isinstance(imp, ImportFrom):
        imp = ImportFrom(
            module="{}.{}".format(store, imp.module) if imp.module else store,
            names=imp.names,
            lineno=imp.lineno,
            level=0,
            col_offset=imp.col_offset,
        )
        return imp
    elif isinstance(imp, Import):
        return ImportFrom(
            module=store,
            names=imp.names,
            lineno=imp.lineno,
            level=0,
            col_offset=imp.col_offset,
        )
    return imp

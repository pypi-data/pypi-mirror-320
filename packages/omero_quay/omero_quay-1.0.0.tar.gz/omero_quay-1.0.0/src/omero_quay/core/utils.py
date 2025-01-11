from __future__ import annotations

from urllib.parse import urlparse

from jinja2 import Template

from ..schema import view


def get_path(isaobject, scheme):
    """Returns the **last** url with scheme 'scheme' found in
    isaobject.urls, or None
    """
    for url in isaobject.urls[::-1]:
        url_ = urlparse(url)
        if url_.scheme == scheme:
            return url_.path
    return None


def path_mapping(input_path, conf, user):
    mappings = conf["ingest"]["mappings"]
    for srce, trgt in mappings.items():
        srce_ = Template(srce).render(user=user)
        if srce_ in input_path:
            trgt_ = Template(trgt).render(user=user)
            return input_path.replace(srce_, trgt_)

    msg = f"No mapping found for {input_path}"
    raise ValueError(msg)


def get_identifiers(isaobject):
    """
    Check for attributes of the isaobject whose slot_uri
    in the manifest schema is 'schema:identifier', with the exclusion
    of the `id` slot, which

    returns a dict {atrr: isaobject.attr}
    """
    ids = [
        k
        for k, s in view.all_slots().items()
        if (s.slot_uri == "schema:identifier")
        and hasattr(isaobject, k)
        and getattr(isaobject, k) is not None
        and k != "id"
    ]
    ids = {id_: getattr(isaobject, id_) for id_ in ids}
    ids["quay_id"] = isaobject.id
    return ids


def get_class_mappings(suffix):
    mappings = {}
    for kls in view.all_classes():
        for mpg in view.get_mappings(kls)["narrow"]:
            if mpg.startswith(f"{suffix}:"):
                mappings[kls] = ":".join(mpg.split(":")[1:])
            break
    return mappings


def find_by_id(id_, seq):
    """Finds an object in a sequence such that the object `id` attribute is equal to id"""
    try:
        return next(iter(filter(lambda e: e.id == id_, seq)))
    except StopIteration:
        return None


def find_by_name(name, seq):
    """Finds an object in a sequence such that the object `name` attribute is equal to name"""
    try:
        return next(iter(filter(lambda e: e.name == name, seq)))
    except StopIteration:
        return None


def expand_ids(id_seq, full_seq):
    """Replace  ids in id_seq with the corresponding object in full_seq"""
    return (item for item in full_seq if item.id in id_seq)


def get_depth(isaobject):
    """Returns 2 for Investigation, 1 for Study and 0 for Assay"""
    depths = {
        "Investigation": 2,
        "Study": 1,
        "Assay": 0,
    }

    return depths.get(isaobject.__class__.__name__)

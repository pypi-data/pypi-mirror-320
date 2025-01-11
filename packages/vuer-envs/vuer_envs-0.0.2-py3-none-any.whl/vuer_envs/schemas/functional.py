from vuer_envs.schemas.base import Xml

def chain(first: Xml, *rest: Xml):
    last = first
    for child in rest:
        last._children.append(child)
        last = child
    return first
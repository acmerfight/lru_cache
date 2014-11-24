# coding=utf-8


class OmittedType(object):
    """
    Omitted represents a Do Not Care value, useful when None won't work
    because it's a valid value.
    """
    __slots__ = tuple()

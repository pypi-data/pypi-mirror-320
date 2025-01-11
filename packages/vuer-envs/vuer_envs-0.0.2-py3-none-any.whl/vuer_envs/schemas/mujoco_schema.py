from typing import Union

from .base import XmlTemplate, Xml


class MjNode(XmlTemplate):
    template = """
    <{tag} {attributes}>
    {children}
    </{tag}>
    """

    def __init__(self, *args, preamble: Union[str, Xml] = "", **rest):
        self._preamble = preamble
        super().__init__(*args, **rest)

    @property
    def preamble(self):
        if self._preamble:
            gathered = [self._preamble]
        else:
            gathered = []

        for child in self._children:
            try:
                gathered.append(child.preamble)
            except AttributeError:
                continue

        return "\n".join(gathered)


class Mjcf(MjNode):
    """
    This is the root element of the MuJoCo XML file.

    """

    tag = "mujoco"
    template = """
    <mujoco {attributes}>
        {preamble}
        <worldbody>
            {children}
        </worldbody>
    </mujoco>
    """


class BoxExample(MjNode):
    name = "box-1"
    """this is a placeholder name."""

    @property
    def preamble(self):
        return f"""
        <asset>
            <texture name="{self.name}" type="2d" builtin="checker" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" mark="cross" width="200" height="200"/>
            <material name="matplane" reflectance="0.5" texture="texplane" texrepeat="1 1" texuniform="true"/>
        </asset>
        """

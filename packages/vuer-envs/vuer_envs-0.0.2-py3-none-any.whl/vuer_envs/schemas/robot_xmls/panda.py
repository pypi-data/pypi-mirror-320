from .robot_schema import Link, XmlTemplate
from vuer_envs.schemas import chain


class PandaLink7(Link):
    """Link 7 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link7" file="panda/meshes/link7.stl"/>
            <material name="panda_Part__Mirroring001_004_002" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring002_004_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring003_004_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring004_004_002" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Mirroring005_004_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring006_004_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring007_004_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Mirroring_004_001" specular="0.5" shininess="0.45" rgba="0.898039 0.917647 0.929412 1.000000"/>
            <mesh name="panda_link7_vis_0" file="panda/obj_meshes/link7_vis/link7_vis_0.obj"/>
            <mesh name="panda_link7_vis_1" file="panda/obj_meshes/link7_vis/link7_vis_1.obj"/>
            <mesh name="panda_link7_vis_2" file="panda/obj_meshes/link7_vis/link7_vis_2.obj"/>
            <mesh name="panda_link7_vis_3" file="panda/obj_meshes/link7_vis/link7_vis_3.obj"/>
            <mesh name="panda_link7_vis_4" file="panda/obj_meshes/link7_vis/link7_vis_4.obj"/>
            <mesh name="panda_link7_vis_5" file="panda/obj_meshes/link7_vis/link7_vis_5.obj"/>
            <mesh name="panda_link7_vis_6" file="panda/obj_meshes/link7_vis/link7_vis_6.obj"/>
            <mesh name="panda_link7_vis_7" file="panda/obj_meshes/link7_vis/link7_vis_7.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0 0 0.08" mass="0.5" diaginertia="0.05 0.05 0.05"/>
        <joint name="{name}_joint7" pos="0 0 0" axis="0 0 1" limited="true" range="-2.8973 2.8973" damping="0.01"/>
        <geom mesh="panda_link7_vis_0" material="panda_Part__Mirroring004_004_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_1" material="panda_Part__Mirroring001_004_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_2" material="panda_Part__Mirroring007_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_3" material="panda_Part__Mirroring006_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_4" material="panda_Part__Mirroring005_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_5" material="panda_Part__Mirroring003_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_6" material="panda_Part__Mirroring002_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link7_vis_7" material="panda_Part__Mirroring_004_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <!-- rotate 135deg to align physically to the tool-->
        <geom type="mesh" group="0" mesh="panda_link7" name="{name}_link7_collision"/>
        <body name="{name}_right_hand" pos="0 0 0.1065" quat="0.924 0 0 -0.383">
            <inertial pos="0 0 0" mass="0.5" diaginertia="0.05 0.05 0.05"/>
            <!-- This camera points out from the eef. -->
            <camera mode="fixed" name="{name}_eye_in_hand" pos="0.05 0 0" quat="0 0.707108 0.707108 0" fovy="75"/>
            <!-- to add gripper -->
        </body>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0.088 0 0", quat="0.707107 0.707107 0 0",
                         **rest)


class PandaLink6(Link):
    """Link 6 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link6" file="panda/meshes/link6.stl"/>
            <material name="panda_Face064_002_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 0.000000 0.000000 1.000000"/>
            <material name="panda_Face065_002_001_002_001" specular="0.5" shininess="0.45" rgba="0.000000 1.000000 0.000000 1.000000"/>
            <material name="panda_Face374_002_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Face539_002_001_002_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Feature001_009_001_002_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Feature002_006_001_002_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Shell002_002_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell003_002_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell004_001_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell005_001_001_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell006_003_002_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1.000000"/>
            <material name="panda_Shell007_002_002_001" specular="0.5" shininess="0.45" rgba="0.250000 0.250000 0.250000 1.000000"/>
            <material name="panda_Shell011_002_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell012_002_002_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell_003_001_002_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Union001_001_001_002_001" specular="0.5" shininess="0.45" rgba="0.039216 0.541176 0.780392 1.000000"/>
            <material name="panda_Union_001_001_002_001" specular="0.5" shininess="0.45" rgba="0.039216 0.541176 0.780392 1.000000"/>
            <mesh name="panda_link6_vis_0" file="panda/obj_meshes/link6_vis/link6_vis_0.obj"/>
            <mesh name="panda_link6_vis_1" file="panda/obj_meshes/link6_vis/link6_vis_1.obj"/>
            <mesh name="panda_link6_vis_2" file="panda/obj_meshes/link6_vis/link6_vis_2.obj"/>
            <mesh name="panda_link6_vis_3" file="panda/obj_meshes/link6_vis/link6_vis_3.obj"/>
            <mesh name="panda_link6_vis_4" file="panda/obj_meshes/link6_vis/link6_vis_4.obj"/>
            <mesh name="panda_link6_vis_5" file="panda/obj_meshes/link6_vis/link6_vis_5.obj"/>
            <mesh name="panda_link6_vis_6" file="panda/obj_meshes/link6_vis/link6_vis_6.obj"/>
            <mesh name="panda_link6_vis_7" file="panda/obj_meshes/link6_vis/link6_vis_7.obj"/>
            <mesh name="panda_link6_vis_8" file="panda/obj_meshes/link6_vis/link6_vis_8.obj"/>
            <mesh name="panda_link6_vis_9" file="panda/obj_meshes/link6_vis/link6_vis_9.obj"/>
            <mesh name="panda_link6_vis_10" file="panda/obj_meshes/link6_vis/link6_vis_10.obj"/>
            <mesh name="panda_link6_vis_11" file="panda/obj_meshes/link6_vis/link6_vis_11.obj"/>
            <mesh name="panda_link6_vis_12" file="panda/obj_meshes/link6_vis/link6_vis_12.obj"/>
            <mesh name="panda_link6_vis_13" file="panda/obj_meshes/link6_vis/link6_vis_13.obj"/>
            <mesh name="panda_link6_vis_14" file="panda/obj_meshes/link6_vis/link6_vis_14.obj"/>
            <mesh name="panda_link6_vis_15" file="panda/obj_meshes/link6_vis/link6_vis_15.obj"/>
            <mesh name="panda_link6_vis_16" file="panda/obj_meshes/link6_vis/link6_vis_16.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0.06 0 0" mass="1.5" diaginertia="0.1 0.1 0.1"/>
        <joint name="{name}_joint6" pos="0 0 0" axis="0 0 1" limited="true" range="-0.0175 3.7525" damping="0.01"/>
        <geom mesh="panda_link6_vis_0" material="panda_Shell006_003_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_1" material="panda_Shell011_002_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_2" material="panda_Shell007_002_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_3" material="panda_Shell005_001_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_4" material="panda_Shell004_001_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_5" material="panda_Shell003_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_6" material="panda_Shell002_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_7" material="panda_Union001_001_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_8" material="panda_Union_001_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_9" material="panda_Face539_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_10" material="panda_Shell_003_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_11" material="panda_Face374_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_12" material="panda_Face065_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_13" material="panda_Face064_002_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_14" material="panda_Part__Feature002_006_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_15" material="panda_Part__Feature001_009_001_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link6_vis_16" material="panda_Shell012_002_002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link6" name="{name}_link6_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0 0 0", quat="0.707107 0.707107 0 0", **rest)


class PandaLink5(Link):
    """Link 5 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link5" file="panda/meshes/link5.stl"/>
            <material name="panda_Part__Feature_002_004_003" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Shell001_001_001_003" specular="0.5" shininess="0.45" rgba="0.250000 0.250000 0.250000 1.000000"/>
            <material name="panda_Shell_001_001_003" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <mesh name="panda_link5_vis_0" file="panda/obj_meshes/link5_vis/link5_vis_0.obj"/>
            <mesh name="panda_link5_vis_1" file="panda/obj_meshes/link5_vis/link5_vis_1.obj"/>
            <mesh name="panda_link5_vis_2" file="panda/obj_meshes/link5_vis/link5_vis_2.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0 0 -0.15" mass="2" diaginertia="0.2 0.2 0.2"/>
        <joint name="{name}_joint5" pos="0 0 0" axis="0 0 1" limited="true" range="-2.8973 2.8973" damping="0.1"/>
        <geom mesh="panda_link5_vis_0" material="panda_Shell001_001_001_003" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link5_vis_1" material="panda_Shell_001_001_003" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link5_vis_2" material="panda_Part__Feature_002_004_003" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link5" name="{name}_link5_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="-0.0825 0.384 0", quat="0.707107 -0.707107 0 0",
                         **rest)


class PandaLink4(Link):
    """Link 4 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link4" file="panda/meshes/link4.stl"/>
            <material name="panda_Part__Feature001_001_003_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Feature002_001_003_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <material name="panda_Part__Feature003_001_003_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Feature_002_003_001" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <mesh name="panda_link4_vis_0" file="panda/obj_meshes/link4_vis/link4_vis_0.obj"/>
            <mesh name="panda_link4_vis_1" file="panda/obj_meshes/link4_vis/link4_vis_1.obj"/>
            <mesh name="panda_link4_vis_2" file="panda/obj_meshes/link4_vis/link4_vis_2.obj"/>
            <mesh name="panda_link4_vis_3" file="panda/obj_meshes/link4_vis/link4_vis_3.obj"/>
        </asset>
        """

    content = """
        <inertial pos="-0.04 0.05 0" mass="2" diaginertia="0.2 0.2 0.2"/>
        <joint name="{name}_joint4" pos="0 0 0" axis="0 0 1" limited="true" range="-3.0718 -0.0698" damping="0.1"/>
        <geom mesh="panda_link4_vis_0" material="panda_Part__Feature001_001_003_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link4_vis_1" material="panda_Part__Feature003_001_003_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link4_vis_2" material="panda_Part__Feature002_001_003_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link4_vis_3" material="panda_Part__Feature_002_003_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link4" name="{name}_link4_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0.0825 0 0", quat="0.707107 0.707107 0 0",
                         **rest)


class PandaLink3(Link):
    """Link 3 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link3" file="panda/meshes/link3.stl"/>
            <material name="panda_Part__Feature001_010_001_002" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Feature002_007_001_002" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Feature003_004_001_002" specular="0.5" shininess="0.45" rgba="1.000000 1.000000 1.000000 1.000000"/>
            <material name="panda_Part__Feature_001_001_001_002" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1.000000"/>
            <mesh name="panda_link3_vis_0" file="panda/obj_meshes/link3_vis/link3_vis_0.obj"/>
            <mesh name="panda_link3_vis_1" file="panda/obj_meshes/link3_vis/link3_vis_1.obj"/>
            <mesh name="panda_link3_vis_2" file="panda/obj_meshes/link3_vis/link3_vis_2.obj"/>
            <mesh name="panda_link3_vis_3" file="panda/obj_meshes/link3_vis/link3_vis_3.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0.04 0 -0.05" mass="2" diaginertia="0.2 0.2 0.2"/>
        <joint name="{name}_joint3" pos="0 0 0" axis="0 0 1" limited="true" range="-2.8973 2.8973" damping="0.1"/>
        <geom mesh="panda_link3_vis_0" material="panda_Part__Feature003_004_001_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link3_vis_1" material="panda_Part__Feature002_007_001_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link3_vis_2" material="panda_Part__Feature001_010_001_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link3_vis_3" material="panda_Part__Feature_001_001_001_002" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link3" name="{name}_link3_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0 -0.316 0", quat="0.707107 0.707107 0 0",
                         **rest)


class PandaLink2(Link):
    """Link 2 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link2" file="panda/meshes/link2.stl"/>
            <material name="panda_Part__Feature024" specular="0.5" shininess="0.45" rgba="1 1 1 1"/>
            <mesh name="panda_link2_vis" file="panda/obj_meshes/link2_vis/link2_vis.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0 0 -0.1" mass="3" diaginertia="0.3 0.3 0.3"/>
        <joint name="{name}_joint2" pos="0 0 0" axis="0 0 1" limited="true" range="-1.7628 1.7628" damping="0.1"/>
        <geom mesh="panda_link2_vis" material="panda_Part__Feature024" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link2" name="{name}_link2_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0 0 0", quat="0.707107 -0.707107 0 0", **rest)


class PandaLink1(Link):
    """Link 1 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link1" file="panda/meshes/link1.stl"/>
            <material name="panda_Part__Feature_001" specular="0.5" shininess="0.45" rgba="1 1 1 1"/>
            <mesh name="panda_link1_vis" file="panda/obj_meshes/link1_vis/link1_vis.obj"/>
        </asset>
        """

    content = """
        <inertial pos="0 0 -0.07" mass="3" diaginertia="0.3 0.3 0.3"/>
        <joint name="{name}_joint1" pos="0 0 0" axis="0 0 1" limited="true" range="-2.8973 2.8973" damping="0.1"/>
        <geom mesh="panda_link1_vis" material="panda_Part__Feature_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link1" name="{name}_link1_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0 0 0.333", **rest)


class PandaLink0(Link):
    """Link 0 of the Panda robot."""

    asset = """
        <asset>
            <mesh name="panda_link0" file="panda/meshes/link0.stl"/>
            <material name="panda_Face636_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1.000000"/>
            <material name="panda_Part__Feature017_001" specular="0.5" shininess="0.45" rgba="1 1 1 1"/>
            <material name="panda_Part__Feature018_001" specular="0.5" shininess="0.45" rgba="1 1 1 1"/>
            <material name="panda_Part__Feature019_001" specular="0.5" shininess="0.45" rgba="1 1 1 1"/>
            <material name="panda_Part__Feature022_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1"/>
            <material name="panda_Part__Feature023_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1"/>
            <material name="panda_Shell001_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1"/>
            <material name="panda_Shell002_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1"/>
            <material name="panda_Shell003_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1"/>
            <material name="panda_Shell009_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1"/>
            <material name="panda_Shell010_001" specular="0.5" shininess="0.45" rgba="0.901961 0.921569 0.929412 1"/>
            <material name="panda_Shell_001" specular="0.5" shininess="0.45" rgba="0.250980 0.250980 0.250980 1"/>
            <mesh name="panda_link0_vis_0" file="panda/obj_meshes/link0_vis/link0_vis_0.obj"/>
            <mesh name="panda_link0_vis_1" file="panda/obj_meshes/link0_vis/link0_vis_1.obj"/>
            <mesh name="panda_link0_vis_2" file="panda/obj_meshes/link0_vis/link0_vis_2.obj"/>
            <mesh name="panda_link0_vis_3" file="panda/obj_meshes/link0_vis/link0_vis_3.obj"/>
            <mesh name="panda_link0_vis_4" file="panda/obj_meshes/link0_vis/link0_vis_4.obj"/>
            <mesh name="panda_link0_vis_5" file="panda/obj_meshes/link0_vis/link0_vis_5.obj"/>
            <mesh name="panda_link0_vis_6" file="panda/obj_meshes/link0_vis/link0_vis_6.obj"/>
            <mesh name="panda_link0_vis_7" file="panda/obj_meshes/link0_vis/link0_vis_7.obj"/>
            <mesh name="panda_link0_vis_8" file="panda/obj_meshes/link0_vis/link0_vis_8.obj"/>
            <mesh name="panda_link0_vis_9" file="panda/obj_meshes/link0_vis/link0_vis_9.obj"/>
            <mesh name="panda_link0_vis_10" file="panda/obj_meshes/link0_vis/link0_vis_10.obj"/>
            <mesh name="panda_link0_vis_11" file="panda/obj_meshes/link0_vis/link0_vis_11.obj"/>
        </asset>
        """

    content = """
        <site name="{name}_right_center" pos="0 0 0" size="0.01" rgba="1 0.3 0.3 1" group="2"/>
        <inertial pos="0 0 0" mass="4" diaginertia="0.4 0.4 0.4"/>
        <geom mesh="panda_link0_vis_0" material="panda_Shell010_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_1" material="panda_Shell009_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_2" material="panda_Shell003_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_3" material="panda_Shell_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_4" material="panda_Shell002_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_5" material="panda_Shell001_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_6" material="panda_Face636_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_7" material="panda_Part__Feature018_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_8" material="panda_Part__Feature019_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_9" material="panda_Part__Feature023_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_10" material="panda_Part__Feature022_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom mesh="panda_link0_vis_11" material="panda_Part__Feature017_001" type="mesh" contype="0" conaffinity="0" group="1"/>
        <geom type="mesh" group="0" mesh="panda_link0" name="{name}_link0_collision"/>
        """

    def __init__(self, *_children, name, children=[], **rest):
        super().__init__(*_children, name=name, children=children, pos="0 0 0", **rest)


class Panda(XmlTemplate):
    """
    This is the Panda robot.
    
    By default, it will use 7 links defined here.
    
    efChildren is optional and can be used to add end effector to the robot.
    name is optional, if provided it will be used as the name of the robot and should be unique.
    If not provided, "panada<robot_id> will be used instead, where robot_id is unique.
    """

    key = 0

    template = """
        <body {attributes}>
            <!-- robot view -->
            <camera mode="fixed" name="{name}_robotview" pos="1.0 0 0.4" quat="0.653 0.271 0.271 0.653"/>
            <inertial diaginertia="0 0 0" mass="0" pos="0 0 0"/>
            {children}
        </body>
        """

    @property
    def preamble(self):
        name = self.name

        return f"""
        <actuator>
            <!-- Physical limits of the actuator. -->
            <motor ctrllimited="true" ctrlrange="-80.0 80.0" joint="{name}_link1_joint1" name="{name}_torq_j1"/>
            <motor ctrllimited="true" ctrlrange="-80.0 80.0" joint="{name}_link2_joint2" name="{name}_torq_j2"/>
            <motor ctrllimited="true" ctrlrange="-80.0 80.0" joint="{name}_link3_joint3" name="{name}_torq_j3"/>
            <motor ctrllimited="true" ctrlrange="-80.0 80.0" joint="{name}_link4_joint4" name="{name}_torq_j4"/>
            <motor ctrllimited="true" ctrlrange="-80.0 80.0" joint="{name}_link5_joint5" name="{name}_torq_j5"/>
            <motor ctrllimited="true" ctrlrange="-12.0 12.0" joint="{name}_link6_joint6" name="{name}_torq_j6"/>
            <motor ctrllimited="true" ctrlrange="-12.0 12.0" joint="{name}_link7_joint7" name="{name}_torq_j7"/>
        </actuator>
        {''.join([p.preamble for p in self._children])}
        """

    def __init__(self, *_children, name, efChildren=None, pos="0 0 0", quat="1 0 0 0", **rest):
        if name:
            self.name = name
        else:
            self.name = f"panda{self.key}"
        self.key = Panda.key
        Panda.key += 1

        link = chain(
            PandaLink0(name=name + "_link0"),
            PandaLink1(name=name + "_link1"),
            PandaLink2(name=name + "_link2"),
            PandaLink3(name=name + "_link3"),
            PandaLink4(name=name + "_link4"),
            PandaLink5(name=name + "_link5"),
            PandaLink6(name=name + "_link6"),
            PandaLink7(name=name + "_link7", children=efChildren),
        )

        super().__init__(link, *_children, name=self.name, pos=pos, quat=quat, **rest)

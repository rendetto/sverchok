# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from sverchok.ui.nodeview_rclick_menu import get_verts_edge_poly_output_sockets
from sverchok.utils.sv_node_utils import frame_adjust

sv_tree_types = {'SverchCustomTreeType', 'SverchGroupTreeType'}

def offset_node_location(existing_node, new_node, offset):
    new_node.location = existing_node.location.x + offset[0] + existing_node.width, existing_node.location.y  + offset[1]


def add_temporal_viewer(tree, nodes, links, output_map, existing_node):
    bl_idname_new_node = 'SvVDExperimental'
    try:
        new_node = nodes['Temporal Viewer']
        if 'verts' in output_map and 'faces' in output_map:
            for i in range(4):
                for link in new_node.inputs[i].links:
                    links.remove(link)

    except KeyError:
        new_node = nodes.new(bl_idname_new_node)
        new_node.name = 'Temporal Viewer'
        new_node.label = 'Temporal Viewer'
        new_node.color = (0.666141, 0.203022, 0)

    offset_node_location(existing_node, new_node, [100, 250])
    frame_adjust(existing_node, new_node)

    outputs = existing_node.outputs
    inputs = new_node.inputs
    if 'verts' in output_map:
        links.new(outputs[output_map['verts']], inputs[0])
        if 'faces' in output_map:
            links.new(outputs[output_map['faces']], inputs[2])
        if 'edges' in output_map:
            links.new(outputs[output_map['edges']], inputs[1])
    else:
        for socket in outputs:
            if socket.bl_idname == "SvVerticesSocket":
                links.new(socket, inputs[0])
                break
            if socket.bl_idname == "SvMatrixSocket":
                links.new(socket, inputs[3])
                break
    tree.update()

def add_temporal_stethoscope(tree, nodes, links, output_map, existing_node):
    bl_idname_new_node = 'SvStethoscopeNodeMK2'
    try:
        new_node = nodes['Temporal Stethoscope']

    except KeyError:
        new_node = nodes.new(bl_idname_new_node)
        new_node.name = 'Temporal Stethoscope'
        new_node.label = 'Temporal Stethoscope'
        new_node.color = (0.336045, 0.336045, 0.666654)

    offset_node_location(existing_node, new_node, [30,-200])
    frame_adjust(existing_node, new_node)

    outputs = existing_node.outputs
    inputs = new_node.inputs
    connected_to = 0
    for i, socket in enumerate(outputs):
        if inputs[0].other == socket:
            connected_to = i +1
            break

    for i in range(len(outputs)):
        socket = outputs[(i + connected_to)%len(outputs)]
        if socket.hide:
            continue
        links.new(socket, inputs[0])
        break

    tree.update()

def add_temporal_connection(operator, context, force_stetoscope):
    space = context.space_data
    tree = space.node_tree
    nodes = tree.nodes
    links = tree.links

    existing_node = nodes.active
    output_map = get_verts_edge_poly_output_sockets(existing_node)

    if len(existing_node.outputs) == 0:
        return

    # is_matrix_node = any([socket.bl_idname == 'SvMatrixSocket' for socket in existing_node.outputs])
    is_drawable = any([socket.bl_idname in ['SvMatrixSocket', 'SvVerticesSocket'] for socket in existing_node.outputs])

    if  not force_stetoscope and is_drawable:

        add_temporal_viewer(tree, nodes, links, output_map, existing_node)
        return

    add_temporal_stethoscope(tree, nodes, links, output_map, existing_node)
    return


class SvTemporalViewerOperator(bpy.types.Operator):
    """Connect to temporal Viewer"""
    bl_idname = "node.sv_temporal_viewer"
    bl_label = "Sverchok Temporal Viewer"
    cut_links: bpy.props.BoolProperty(name="cut_links", default=False)
    @classmethod
    def poll(cls, context):

        space = context.space_data
        tree_type = space.tree_type
        return space.type == 'NODE_EDITOR' and tree_type in sv_tree_types

    def execute(self, context):

        add_temporal_connection(self, context, False)

        return {'FINISHED'}

class SvTemporalSthetoscopeOperator(bpy.types.Operator):
    """Connect to temporal Sthetoscope"""
    bl_idname = "node.sv_temporal_sthetoscope"
    bl_label = "Sverchok Temporal Sthetoscope"

    @classmethod
    def poll(cls, context):

        space = context.space_data
        tree_type = space.tree_type
        return space.type == 'NODE_EDITOR' and tree_type in sv_tree_types

    def execute(self, context):

        add_temporal_connection(self, context, True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SvTemporalViewerOperator)
    bpy.utils.register_class(SvTemporalSthetoscopeOperator)


def unregister():
    bpy.utils.unregister_class(SvTemporalViewerOperator)
    bpy.utils.unregister_class(SvTemporalSthetoscopeOperator)

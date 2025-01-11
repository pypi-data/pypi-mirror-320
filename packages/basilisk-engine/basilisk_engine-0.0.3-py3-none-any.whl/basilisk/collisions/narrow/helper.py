import glm
from ...nodes.node import Node


def get_support_point(node1: Node, node2: Node, dir_vec: glm.vec3) -> tuple[glm.vec3, glm.vec3, glm.vec3]:
    """
    Outputs the best support point to be added to the polytop based on the direction vector.
    """
    vertex1 = get_furthest_point(node1, dir_vec)
    vertex2 = get_furthest_point(node2, -dir_vec)
    return (vertex1 - vertex2, vertex1, vertex2)
    
def get_furthest_point(node: Node, dir_vec: glm.vec3) -> glm.vec3:
    """
    Determines the furthest point in a given direction
    """
    # determine furthest point by using untransformed mesh
    node_dir_vec = node.rotation * dir_vec # rotate the world space vector to node space
    vertex = node.mesh.get_best_dot(node_dir_vec)
    vertex = node.model_matrix * glm.vec4(vertex, 1.0)
    
    # transform point to world space
    return glm.vec3(vertex)
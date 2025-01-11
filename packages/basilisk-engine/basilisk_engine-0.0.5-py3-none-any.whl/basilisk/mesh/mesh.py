import numpy as np
import glm
import os
# from pyobjloader import load_model
from .model import load_model
from .narrow_bvh import NarrowBVH
from ..generic.matrices import compute_inertia_moment, compute_inertia_product
from ..generic.meshes import get_extreme_points_np, moller_trumbore
from .mesh_from_data import from_data


class Mesh():
    data: np.ndarray
    """The mesh vertex data stored as a 4-byte float numpy array. Format will be [position.xyz, uv.xy, normal.xyz, tangent.xyz, bitangent.xyz]"""
    points: np.ndarray
    """All the unique points of the mesh given by the model file"""  
    indices: np.ndarray
    """Indices of the triangles corresponding to the points array"""  
    bvh: any
    """Data structure allowing the access of closest points more efficiently"""
    volume: float
    """The volume of the unscaled mesh"""
    geometric_center: glm.vec3
    """The geometric center of the mesh"""
    center_of_mass: glm.vec3
    """The center of mass of the mesh calculated from the inertia tensor algorithm"""
    half_dimensions: glm.vec3
    """The aligned half dimensions to the untransformed mesh"""
    bvh: NarrowBVH
    """BVH for accessing triangle intersections with a line"""

    def __init__(self, data: str | os.PathLike | np.ndarray) -> None:
        """
        Mesh object containing all the data needed to render an object and perform physics/collisions on it
        Args:
            data: str
                path to the .obj file of the model or an array of the mesh data
        """
        
        # Verify the path type
        if isinstance(data, str) or isinstance(data, os.PathLike):  # Load the model from file
            model = load_model(data, calculate_tangents=True)
        elif isinstance(data, np.ndarray):                          # Load the model from array of data
            model = from_data(data)
        else:                                                       # Invalid data type
            raise TypeError(f'Invalid path type: {type(data)}. Expected a string or os.path')

        # Get the vertex data
        if len(model.vertex_data[0]) == 8:
            self.data = model.vertex_data.copy()
        else:
            self.data = np.zeros(shape=(len(model.vertex_data), 8))
            self.data[:,:3] = model.vertex_data[:,:3]
            self.data[:,5:] = model.vertex_data[:,3:]
        
        # Get tangent data
        if len(model.tangent_data[0]) == 6:
            self.data = np.hstack([self.data, model.tangent_data])
        else:
            tangents = np.zeros(shape=(len(self.data), 6))
            tangents[:,:] += [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
            self.data = np.hstack([self.data, tangents])

        # Mesh points and triangles used for physics/collisions
        self.points = model.vertex_points.copy()
        self.indices = model.point_indices.copy()

        # Model will no longer be used
        del model
        
        # generate geometric data
        maximum, minimum = get_extreme_points_np(self.points)
        self.geometric_center = (glm.vec3(maximum) + glm.vec3(minimum)) / 2
        self.half_dimensions  = maximum - self.geometric_center
        
        # volume and center of mass
        self.volume = 0
        self.center_of_mass = glm.vec3(0.0)
        for triangle in self.indices:
            pts = [glm.vec3(self.points[t]) for t in triangle]
            det_j = glm.dot(pts[0], glm.cross(pts[1], pts[2]))
            tet_volume = det_j / 6
            self.volume += tet_volume
            self.center_of_mass += tet_volume * (pts[0] + pts[1] + pts[2]) / 4
        self.center_of_mass /= self.volume
        
        # data structrues
        self.bvh = NarrowBVH(self)
        
    def get_inertia_tensor(self, scale: glm.vec3) -> glm.mat3x3:
        """
        Gets the inertia tensor of the mesh with the given scale and mass 1
        """
        # scale variables
        center_of_mass = self.center_of_mass * scale
        volume = self.volume * scale.x * scale.y * scale.z
        
        # uses density = 1 to calculate variables, should be the same for mass = 1 since they are only spatial variables
        points = self.points.copy()
        points[:, 0] *= scale.x
        points[:, 1] *= scale.y
        points[:, 2] *= scale.z
        
        ia = ib = ic = iap = ibp = icp = 0
        for triangle in self.indices:
            pts = [points[t] for t in triangle]
            det_j = glm.dot(pts[0], glm.cross(pts[1], pts[2]))
            
            ia += det_j * (compute_inertia_moment(pts, 1) + compute_inertia_moment(pts, 2))
            ib += det_j * (compute_inertia_moment(pts, 0) + compute_inertia_moment(pts, 2))
            ic += det_j * (compute_inertia_moment(pts, 0) + compute_inertia_moment(pts, 1))
            iap += det_j * compute_inertia_product(pts, 1, 2)
            ibp += det_j * compute_inertia_product(pts, 0, 1)
            icp += det_j * compute_inertia_product(pts, 0, 2)
            
        # since tensor was calc with density = 1. we say mass = density / volume = 1 / volume
        ia = ia / volume / 60 - volume * (center_of_mass[1] ** 2 + center_of_mass[2] ** 2)
        ib = ib / volume / 60 - volume * (center_of_mass[0] ** 2 + center_of_mass[2] ** 2)
        ic = ic / volume / 60 - volume * (center_of_mass[0] ** 2 + center_of_mass[1] ** 2)
        iap = iap / volume / 120 - volume * center_of_mass[1] * center_of_mass[2]
        ibp = ibp / volume / 120 - volume * center_of_mass[0] * center_of_mass[1]
        icp = icp / volume / 120 - volume * center_of_mass[0] * center_of_mass[2]
        
        return glm.mat3x3(
            ia, -ibp, -icp,
            -ibp, ib, -iap,
            -icp, -iap, ic
        )
        
    def get_best_triangle(self, point: glm.vec3, vec: glm.vec3) -> int:
        """
        Gets the triangle with the closest intersection, -1 if no intersection is found
        """
        indices = self.bvh.get_possible_triangles(point, vec)
        best_distance = -1
        best_index = -1
        
        point = glm.vec3(point)
        vec = glm.vec3(vec)

        for triangle in indices:
            
            # check if triangle intersects
            intersection = moller_trumbore(point, vec, [self.points[t] for t in self.indices[triangle]])
            if not intersection: continue
            
            # check if triangle is on correct side of line
            difference = intersection - self.geometric_center
            if glm.dot(difference, vec) < 0: continue
            
            # determine best distance
            distance = glm.length(difference)
            if best_distance < 0 or distance < best_distance: 
                best_distance = distance
                best_index = triangle
                
        return best_index
    
    def get_best_triangle_brute(self, point: glm.vec3, vec: glm.vec3) -> int:
        """
        Gets the triangle with the closest intersection, -1 if no intersection is found. Uses a brute force method
        """
        best_distance = -1
        best_index = -1
        
        point = glm.vec3(point)
        vec = glm.vec3(vec)
        
        for index, triangle in enumerate(self.indices):
            
            # check if triangle intersects
            intersection = moller_trumbore(point, vec, [self.points[t] for t in triangle])
            if not intersection: continue
            
            # check if triangle is on correct side of line
            difference = intersection - self.geometric_center
            if glm.dot(difference, vec) < 0: continue
            
            # determine best distance
            distance = glm.length(difference)
            if best_distance < 0 or distance < best_distance: 
                best_distance = distance
                best_index = index
                
        return best_index
        
    def get_best_dot(self, vec: glm.vec3) -> glm.vec3:
        """
        Gets the point with the highest normalized dot product to the given vector
        """
        triangle = self.bvh.get_best_dot(vec)
        if triangle == -1: return None
        index = max(self.indices[triangle], key=lambda t: glm.dot(glm.normalize(self.points[t]), vec))
        return glm.vec3(self.points[index])
    
    def get_best_dot_old(self, vec):
        best_dot = -1e10
        best = None
        for point in self.points:
            dot = glm.dot(glm.normalize(point), vec)
            if dot > best_dot: best_dot, best = dot, glm.vec3(point)
        return best

    def __repr__(self) -> str:
        size = (self.data.nbytes + self.points.nbytes + self.indices.nbytes) / 1024 / 1024
        return f'<Basilisk Mesh | {len(self.data)} vertices, {size:.2} mb>'
    
    @property
    def top_right(self): return self.bvh.root.top_right
    @property
    def bottom_left(self): return self.bvh.root.bottom_left
    @property
    def aabb_points(self): 
        x1, y1, z1 = self.top_right
        x2, y2, z2 = self.bottom_left
        return [glm.vec3(x, y, z) for z in (z1, z2) for y in (y1, y2) for x in (x1, x2)]

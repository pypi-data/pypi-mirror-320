import numpy as np

from ._mapping import map_to_local_bb_2d, map_to_local_bb_3d
from ._antonietti import integrateMonomialsPolyhedron
from ._antonietti import integrateMonomialsPolygon
from ._moment_matching_2d import moment_matching as mm2d
from ._moment_matching_3d import moment_matching as mm3d

def get_quadrature_2d(order:int,
                      vertices: np.ndarray,
                      face: np.ndarray,
                      mapping = False,
                      get_residual = False)-> (np.ndarray, np.ndarray):
    """generates quadrature points and weights for a specified order for a polygon

    Parameters
    ----------
    order : int
        total polynomial order of the integrand
    vertices : np.ndarray
        coordinates of vertices, shape = (numver of vertices, 2)
    face : np.ndarray
        declaration of the planar face with ordered vertices indices.
    mapping: bool (default: False)
        if False assumes that your poly lies in [-1,1]^2 already, integration points will be in [-1,1]^2
        if true it will map (behind the scene)your poly to [-1,1]^2, integration points will be in the unmapped space
    get_residual : bool
        if true returns the residual as defined in Eq.17 of the paper.
        It is the direct measure of the L2-norm error on the
        integration of each monomial.

    Returns
    -------
    (np.ndarray, np.ndarray)
        points, weights

    """
    # perform matrix transfomation to fit in the local bounding box = [-1, 1]^2
    if mapping:
        verts, jacobian, transfo = map_to_local_bb_2d(vertices)
    else:
        verts = vertices
        jacobian = 1
    # call antonietti's algorithm
    tmp = np.pad(verts,((0,0),(0,1)))
    integrated_monomials = integrateMonomialsPolygon(order, face, tmp)
    # perform moment matching
    if get_residual:
        points, weights, resiadual = mm2d(order, integrated_monomials, residual = True)
        weights = weights/jacobian
        if mapping:
            points = (points + transfo[1]) @ np.linalg.inv(transfo[0])
        return points, weights, resiadual
    else:
        points, weights = mm2d(order, integrated_monomials, residual = False)
        weights = weights/jacobian
        if mapping:
            points = (points + transfo[1]) @ np.linalg.inv(transfo[0])
        return points, weights

def get_quadrature_3d(order:int,
                      vertices: np.ndarray,
                      faces: np.ndarray,
                      mapping = False,
                      get_residual = False)-> (np.ndarray, np.ndarray):
    """generates quadrature points and weights for a specified order for a polyhedron

    Parameters
    ----------
    order : int
        total polynomial order of the integrand
    vertices : np.ndarray
        coordinates of vertices, shape = (numver of vertices, 3)
    faces : np.ndarray
        declaration of planar faces with ordered vertices indices. If
        all faces have the save number of vertices then "faces" can be
        a np.ndarray of shape (number of faces, number of vertices per
        face)
    mapping: bool (default: False)
        if False assumes that your poly lies in [-1,1]^3 already, integration points will be in [-1,1]^3
        if true it will map (behind the scene)your poly to [-1,1]^3, integration points will be in the unmapped space
    get_residual : bool
        if true returns the residual as defined in Eq.17 of the paper.
        It is the direct measure of the L2-norm error on the
        integration of each monomial.

    Returns
    -------
    (np.ndarray, np.ndarray)
        points, weights

    """
    # perform matrix transfomation to fit in the local bounding box = [-1, 1]^3
    verts, jacobian, transfo = map_to_local_bb_3d(vertices)
    # call antonietti's algorithm
    integrated_monomials = integrateMonomialsPolyhedron(order, faces, verts)
    # perform moment matching
    if get_residual:
        points, weights, resiadual = mm3d(order, integrated_monomials, residual = True)
        weights = weights/jacobian
        if mapping:
            points = (points + transfo[1]) @ np.linalg.inv(transfo[0])
        return points, weights, resiadual
    else:
        points, weights = mm3d(order, integrated_monomials, residual = False)
        weights = weights/jacobian
        if mapping:
            points = (points + transfo[1]) @ np.linalg.inv(transfo[0])
        return points, weights

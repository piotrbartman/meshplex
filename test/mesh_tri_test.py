# -*- coding: utf-8 -*-
#
import numpy
import pytest
import meshio

import meshplex

from helpers import download_mesh, near_equal, run


def test_regular_tri():
    points = numpy.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-14

    assert (mesh.local_idx.T == [[1, 2], [2, 0], [0, 1]]).all()
    assert mesh.local_idx_inv == [[(0, 2), (1, 1)], [(0, 0), (1, 2)], [(0, 1), (1, 0)]]

    # ce_ratios
    assert near_equal(mesh.get_ce_ratios().T, [0.0, 0.5, 0.5], tol)

    # control volumes
    assert near_equal(mesh.get_control_volumes(), [0.25, 0.125, 0.125], tol)

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5], tol)

    # circumcenters
    assert near_equal(mesh.get_cell_circumcenters(), [0.5, 0.5, 0.0], tol)

    # centroids
    assert near_equal(
        mesh.get_control_volume_centroids(),
        [[0.25, 0.25, 0.0], [2.0 / 3.0, 1.0 / 6.0, 0.0], [1.0 / 6.0, 2.0 / 3.0, 0.0]],
        tol,
    )

    assert mesh.num_delaunay_violations() == 0

    mesh.get_cell_mask()
    mesh.get_edge_mask()
    mesh.get_vertex_mask()

    # dummy subdomain marker test
    # pylint: disable=too-few-public-methods
    class Subdomain(object):
        is_boundary_only = False

        # pylint: disable=no-self-use
        def is_inside(self, X):
            return numpy.ones(X.shape[1:], dtype=bool)

    cell_mask = mesh.get_cell_mask(Subdomain())
    assert sum(cell_mask) == 1

    return


def test_regular_tri_order():
    points = numpy.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])

    mesh = meshplex.MeshTri(points, cells)
    assert all((mesh.cells["nodes"] == [0, 1, 2]).flat)

    tol = 1.0e-14

    # ce_ratios
    assert near_equal(mesh.get_ce_ratios().T, [0.5, 0.0, 0.5], tol)

    # control volumes
    assert near_equal(mesh.get_control_volumes(), [0.125, 0.25, 0.125], tol)

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5], tol)

    # circumcenters
    assert near_equal(mesh.get_cell_circumcenters(), [0.5, 0.5, 0.0], tol)

    # centroids
    assert near_equal(
        mesh.get_control_volume_centroids(),
        [[1.0 / 6.0, 2.0 / 3.0, 0.0], [0.25, 0.25, 0.0], [2.0 / 3.0, 1.0 / 6.0, 0.0]],
        tol,
    )

    assert mesh.num_delaunay_violations() == 0

    return


@pytest.mark.parametrize("a", [1.0, 2.0])
def test_regular_tri2(a):
    points = (
        numpy.array(
            [
                [-0.5, -0.5 * numpy.sqrt(3.0), 0],
                [-0.5, +0.5 * numpy.sqrt(3.0), 0],
                [1, 0, 0],
            ]
        )
        / numpy.sqrt(3)
        * a
    )
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-14

    # ce_ratios
    val = 0.5 / numpy.sqrt(3.0)
    assert near_equal(mesh.get_ce_ratios(), [val, val, val], tol)

    # control volumes
    vol = numpy.sqrt(3.0) / 4 * a ** 2
    assert near_equal(
        mesh.get_control_volumes(), [vol / 3.0, vol / 3.0, vol / 3.0], tol
    )

    # cell volumes
    assert near_equal(mesh.cell_volumes, [vol], tol)

    # circumcenters
    assert near_equal(mesh.get_cell_circumcenters(), [0.0, 0.0, 0.0], tol)

    return


# def test_degenerate_small0():
#     h = 1.0e-3
#     points = numpy.array([
#         [0, 0, 0],
#         [1, 0, 0],
#         [0.5, h, 0.0],
#         ])
#     cells = numpy.array([[0, 1, 2]])
#     mesh = meshplex.MeshTri(
#             points,
#             cells,
#             allow_negative_volumes=True
#             )

#     tol = 1.0e-14

#     # ce_ratios
#     alpha = 0.5 * h - 1.0 / (8*h)
#     beta = 1.0 / (4*h)
#     assertAlmostEqual(mesh.get_ce_ratios_per_edge()[0], alpha, delta=tol)
#     self.assertAlmostEqual(mesh.get_ce_ratios_per_edge()[1], beta, delta=tol)
#     self.assertAlmostEqual(mesh.get_ce_ratios_per_edge()[2], beta, delta=tol)

#     # control volumes
#     alpha1 = 0.0625 * (3*h - 1.0/(4*h))
#     alpha2 = 0.125 * (h + 1.0 / (4*h))
#     assert near_equal(
#         mesh.get_control_volumes(),
#         [alpha1, alpha1, alpha2],
#         tol
#         )

#     # cell volumes
#     self.assertAlmostEqual(mesh.cell_volumes[0], 0.5 * h, delta=tol)

#     # surface areas
#     edge_length = numpy.sqrt(0.5**2 + h**2)
#     # circumference = 1.0 + 2 * edge_length
#     alpha = 0.5 * (1.0 + edge_length)
#     self.assertAlmostEqual(mesh.surface_areas[0], alpha, delta=tol)
#     self.assertAlmostEqual(mesh.surface_areas[1], alpha, delta=tol)
#     self.assertAlmostEqual(mesh.surface_areas[2], edge_length, delta=tol)

#     # centroids
#     alpha = -41.666666669333345
#     beta = 0.58333199998399976
#      self.assertAlmostEqual(
#              mesh.centroids[0][0],
#              0.416668000016,
#              delta=tol
#              )
#     self.assertAlmostEqual(mesh.centroids[0][1], alpha, delta=tol)
#     self.assertAlmostEqual(mesh.centroids[0][2], 0.0, delta=tol)

#     self.assertAlmostEqual(mesh.centroids[1][0], beta, delta=tol)
#     self.assertAlmostEqual(mesh.centroids[1][1], alpha, delta=tol)
#     self.assertAlmostEqual(mesh.centroids[1][2], 0.0, delta=tol)

#     self.assertAlmostEqual(mesh.centroids[2][0], 0.5, delta=tol)
#     self.assertAlmostEqual(mesh.centroids[2][1], -41.666, delta=tol)
#     self.assertAlmostEqual(mesh.centroids[2][2], 0.0, delta=tol)

#     self.assertEqual(mesh.num_delaunay_violations(), 0)
#     return


@pytest.mark.parametrize(
    "h",
    # TODO [1.0e0, 1.0e-1]
    [1.0e0],
)
def test_degenerate_small0b(h):
    points = numpy.array([[0, 0, 0], [1, 0, 0], [0.5, h, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells, flat_cell_correction=None)

    tol = 1.0e-14

    # edge lengths
    el = numpy.sqrt(0.5 ** 2 + h ** 2)
    assert near_equal(mesh.get_edge_lengths().T, [el, el, 1.0], tol)

    # ce_ratios
    ce0 = 0.5 / h * (h ** 2 - 0.25)
    ce12 = 0.25 / h
    assert near_equal(mesh.get_ce_ratios().T, [ce12, ce12, ce0], tol)

    # control volumes
    cv12 = 0.25 * (1.0 ** 2 * ce0 + (0.25 + h ** 2) * ce12)
    cv0 = 0.5 * (0.25 + h ** 2) * ce12
    assert near_equal(mesh.get_control_volumes(), [cv12, cv12, cv0], tol)

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5 * h], tol)

    # circumcenters
    assert near_equal(mesh.get_cell_circumcenters(), [0.5, 0.375, 0.0], tol)

    # surface areas
    ids, vals = mesh.get_surface_areas()
    assert numpy.all(ids == [[0, 1, 2], [0, 1, 2], [0, 1, 2]])
    assert near_equal(
        vals,
        [[0.0, 0.5 * el, 0.5 * el], [0.5 * el, 0.0, 0.5 * el], [0.5, 0.5, 0.0]],
        tol,
    )

    assert mesh.num_delaunay_violations() == 0
    return


# TODO parametrize with flat boundary correction
def test_degenerate_small0b_fcc():
    h = 1.0e-3
    points = numpy.array([[0, 0, 0], [1, 0, 0], [0.5, h, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells, flat_cell_correction="full")

    tol = 1.0e-14

    # edge lengths
    el = numpy.sqrt(0.5 ** 2 + h ** 2)
    assert near_equal(mesh.get_edge_lengths().T, [el, el, 1.0], tol)

    # ce_ratios
    ce = h
    assert near_equal(mesh.get_ce_ratios().T, [ce, ce, 0.0], tol)

    # control volumes
    cv = ce * el
    alpha = 0.25 * el * cv
    beta = 0.5 * h - 2 * alpha
    assert near_equal(mesh.get_control_volumes(), [alpha, alpha, beta], tol)

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5 * h], tol)

    # surface areas
    g = numpy.sqrt((0.5 * el) ** 2 + (ce * el) ** 2)
    alpha = 0.5 * el + g
    beta = el + (1.0 - 2 * g)
    assert near_equal(mesh.get_surface_areas(), [alpha, alpha, beta], tol)

    # centroids
    centroids = mesh.get_control_volume_centroids()
    alpha = 1.0 / 6000.0
    gamma = 0.00038888918518558031
    assert near_equal(centroids[0], [0.166667, alpha, 0.0], tol)
    assert near_equal(centroids[1], [0.833333, alpha, 0.0], tol)
    assert near_equal(centroids[2], [0.5, gamma, 0.0], tol)

    assert mesh.num_delaunay_violations() == 0
    return


@pytest.mark.parametrize("h, a", [(1.0e-3, 0.3)])
def test_degenerate_small1(h, a):
    points = numpy.array([[0, 0, 0], [1, 0, 0], [a, h, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells, flat_cell_correction="full")

    tol = 1.0e-14

    # edge lengths
    el1 = numpy.sqrt(a ** 2 + h ** 2)
    el2 = numpy.sqrt((1.0 - a) ** 2 + h ** 2)
    assert near_equal(mesh.get_edge_lengths().T, [[el2, el1, 1.0]], tol)

    # ce_ratios
    ce1 = 0.5 * h / a
    ce2 = 0.5 * h / (1.0 - a)
    assert near_equal(mesh.get_ce_ratios().T, [ce2, ce1, 0.0], tol)

    # control volumes
    cv1 = ce1 * el1
    alpha1 = 0.25 * el1 * cv1
    cv2 = ce2 * el2
    alpha2 = 0.25 * el2 * cv2
    beta = 0.5 * h - (alpha1 + alpha2)
    assert near_equal(mesh.get_control_volumes(), [alpha1, alpha2, beta], tol)
    assert abs(sum(mesh.get_control_volumes()) - 0.5 * h) < tol

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5 * h], tol)

    # surface areas
    b1 = numpy.sqrt((0.5 * el1) ** 2 + cv1 ** 2)
    alpha0 = b1 + 0.5 * el1
    b2 = numpy.sqrt((0.5 * el2) ** 2 + cv2 ** 2)
    alpha1 = b2 + 0.5 * el2
    total = 1.0 + el1 + el2
    alpha2 = total - alpha0 - alpha1
    surf = mesh.get_surface_areas()
    assert near_equal(surf, [alpha0, alpha1, alpha2], tol)

    assert mesh.num_delaunay_violations() == 0
    return


@pytest.mark.parametrize("h", [1.0e-2])
def test_degenerate_small2(h):
    points = numpy.array([[0, 0, 0], [1, 0, 0], [0.5, h, 0.0], [0.5, -h, 0.0]])
    cells = numpy.array([[0, 1, 2], [0, 1, 3]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-11

    # ce_ratios
    alpha = h - 1.0 / (4 * h)
    beta = 1.0 / (4 * h)
    assert near_equal(mesh.get_ce_ratios_per_interior_edge(), [alpha], tol)

    alpha2 = (h - 1.0 / (4 * h)) / 2
    assert near_equal(
        mesh.get_ce_ratios(), [[beta, beta], [beta, beta], [alpha2, alpha2]], tol
    )

    # control volumes
    alpha1 = 0.125 * (3 * h - 1.0 / (4 * h))
    alpha2 = 0.125 * (h + 1.0 / (4 * h))
    assert near_equal(mesh.get_control_volumes(), [alpha1, alpha1, alpha2, alpha2], tol)

    # circumcenters
    assert near_equal(
        mesh.get_cell_circumcenters(), [[0.5, -12.495, 0.0], [0.5, +12.495, 0.0]], tol
    )

    # cell volumes
    assert near_equal(mesh.cell_volumes, [0.5 * h, 0.5 * h], tol)

    assert mesh.num_delaunay_violations() == 1

    return


def test_rectanglesmall():
    points = numpy.array(
        [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [10.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    )
    cells = numpy.array([[0, 1, 2], [0, 2, 3]])

    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-14

    assert near_equal(mesh.get_ce_ratios_per_interior_edge(), [0.0], tol)

    print(mesh.get_ce_ratios())
    assert near_equal(mesh.get_ce_ratios(), [[5.0, 0.05], [0.0, 5.0], [0.05, 0.0]], tol)
    assert near_equal(mesh.get_control_volumes(), [2.5, 2.5, 2.5, 2.5], tol)
    assert near_equal(mesh.cell_volumes, [5.0, 5.0], tol)
    assert mesh.num_delaunay_violations() == 0

    return


def test_pacman():
    filename = download_mesh("pacman.msh", "2da8ff96537f844a95a83abb48471b6a")
    mesh, _, _, _ = meshplex.read(filename, flat_cell_correction="boundary")

    run(
        mesh,
        73.64573933105898,
        [3.5908322974649631, 0.26638548094154707],
        [354.8184824409405, 0.94690319745399243],
        [2.6213234038171014, 0.13841739494523228],
    )

    assert mesh.num_delaunay_violations() == 0

    return


def test_shell():
    points = numpy.array(
        [
            [+0.0, +0.0, +1.0],
            [+1.0, +0.0, +0.0],
            [+0.0, +1.0, +0.0],
            [-1.0, +0.0, +0.0],
            [+0.0, -1.0, +0.0],
        ]
    )
    cells = numpy.array([[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 1, 4]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-14
    ce_ratios = 0.5 / numpy.sqrt(3.0) * numpy.ones((4, 3))
    assert near_equal(mesh.get_ce_ratios().T, ce_ratios, tol)

    cv = numpy.array([2.0, 1.0, 1.0, 1.0, 1.0]) / numpy.sqrt(3.0)
    assert near_equal(mesh.get_control_volumes(), cv, tol)

    cell_vols = numpy.sqrt(3.0) / 2.0 * numpy.ones(4)
    assert near_equal(mesh.cell_volumes, cell_vols, tol)

    assert mesh.num_delaunay_violations() == 0

    return


def test_sphere():
    filename = download_mesh("sphere.msh", "70a5dbf79c3b259ed993458ff4aa2e93")
    mesh, _, _, _ = meshplex.read(filename)
    run(
        mesh,
        12.273645818711595,
        [1.0177358705967492, 0.10419690304323895],
        [366.3982135866799, 1.7062353589387327],
        [0.72653362732751214, 0.05350373815413411],
    )

    # assertEqual(mesh.num_delaunay_violations(), 60)
    return


def test_signed_area():
    filename = download_mesh("pacman.msh", "2da8ff96537f844a95a83abb48471b6a")
    mesh = meshio.read(filename)
    assert numpy.all(numpy.abs(mesh.points[:, 2]) < 1.0e-15)
    X = mesh.points[:, :2]

    mesh = meshplex.MeshTri(X, mesh.cells["triangle"], flat_cell_correction=None)

    vols = mesh.get_signed_tri_areas()
    assert numpy.all(abs(abs(vols) - mesh.cell_volumes) < 1.0e-12 * mesh.cell_volumes)
    return


def test_update_node_coordinates():
    filename = download_mesh("pacman.msh", "2da8ff96537f844a95a83abb48471b6a")
    mesh = meshio.read(filename)
    assert numpy.all(numpy.abs(mesh.points[:, 2]) < 1.0e-15)

    mesh1 = meshplex.MeshTri(
        mesh.points, mesh.cells["triangle"], flat_cell_correction=None
    )

    numpy.random.seed(123)
    X2 = mesh.points + 1.0e-2 * numpy.random.rand(*mesh.points.shape)
    mesh2 = meshplex.MeshTri(
        X2, mesh.cells["triangle"], flat_cell_correction=None
    )

    mesh1.update_node_coordinates(X2)

    tol = 1.0e-12
    assert near_equal(mesh1.ei_dot_ej, mesh2.ei_dot_ej, tol)
    assert near_equal(mesh1.cell_volumes, mesh2.cell_volumes, tol)
    return


def test_flip_delaunay():
    filename = download_mesh("pacman.msh", "2da8ff96537f844a95a83abb48471b6a")
    mesh = meshio.read(filename)

    numpy.random.seed(123)
    mesh.points[:, :2] += 5.0e-2 * numpy.random.rand(*mesh.points[:, :2].shape)

    mesh = meshplex.MeshTri(
        mesh.points, mesh.cells["triangle"], flat_cell_correction=None
    )

    assert mesh.num_delaunay_violations() == 16

    mesh.flip_until_delaunay()
    assert mesh.num_delaunay_violations() == 0

    # Assert edges_cells integrity
    for cell_gid, edge_gids in enumerate(mesh.cells["edges"]):
        for edge_gid in edge_gids:
            num_adj_cells, edge_id = mesh._edge_gid_to_edge_list[edge_gid]
            assert cell_gid in mesh._edges_cells[num_adj_cells][edge_id]

    new_cells = mesh.cells["nodes"].copy()
    new_coords = mesh.node_coords.copy()

    # Assert that some key values are updated properly
    mesh2 = meshplex.MeshTri(new_coords, new_cells, flat_cell_correction=None)
    assert numpy.all(mesh.idx_hierarchy == mesh2.idx_hierarchy)
    tol = 1.0e-15
    assert near_equal(mesh.half_edge_coords, mesh2.half_edge_coords, tol)
    assert near_equal(mesh.cell_volumes, mesh2.cell_volumes, tol)
    assert near_equal(mesh.ei_dot_ej, mesh2.ei_dot_ej, tol)

    return


def test_flip_delaunay_near_boundary():
    points = numpy.array(
        [[0.0, +0.0, 0.0], [0.5, -0.1, 0.0], [1.0, +0.0, 0.0], [0.5, +0.1, 0.0]]
    )
    cells = numpy.array([[0, 1, 2], [0, 2, 3]])
    mesh = meshplex.MeshTri(points, cells, flat_cell_correction=None)

    mesh.create_edges()
    assert mesh.num_delaunay_violations() == 1
    assert numpy.array_equal(mesh.cells["nodes"], [[0, 1, 2], [0, 2, 3]])
    assert numpy.array_equal(mesh.cells["edges"], [[3, 1, 0], [4, 2, 1]])

    mesh.flip_until_delaunay()

    assert mesh.num_delaunay_violations() == 0
    assert numpy.array_equal(mesh.cells["nodes"], [[1, 3, 2], [1, 3, 0]])
    assert numpy.array_equal(mesh.cells["edges"], [[4, 3, 1], [2, 0, 1]])
    return


def test_flip_same_edge_twice():
    points = numpy.array(
        [[0.0, +0.0, 0.0], [0.5, -0.1, 0.0], [1.0, +0.0, 0.0], [0.5, +0.1, 0.0]]
    )
    cells = numpy.array([[0, 1, 2], [0, 2, 3]])
    mesh = meshplex.MeshTri(points, cells, flat_cell_correction=None)
    assert mesh.num_delaunay_violations() == 1

    mesh.flip_until_delaunay()
    assert mesh.num_delaunay_violations() == 0

    # Assert edges_cells integrity
    for cell_gid, edge_gids in enumerate(mesh.cells["edges"]):
        for edge_gid in edge_gids:
            num_adj_cells, edge_id = mesh._edge_gid_to_edge_list[edge_gid]
            assert cell_gid in mesh._edges_cells[num_adj_cells][edge_id]

    new_points = numpy.array(
        [[0.0, +0.0, 0.0], [0.1, -0.5, 0.0], [0.2, +0.0, 0.0], [0.1, +0.5, 0.0]]
    )
    mesh.update_node_coordinates(new_points)
    assert mesh.num_delaunay_violations() == 1

    mesh.flip_until_delaunay()
    assert mesh.num_delaunay_violations() == 0
    mesh.show()

    return


def test_inradius():
    # 3-4-5 triangle
    points = numpy.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-15

    ic = mesh.get_inradius()
    assert near_equal(ic, [1.0], tol)

    # 30-60-90 triangle
    a = 1.0
    points = numpy.array(
        [[0.0, 0.0, 0.0], [a / 2, 0.0, 0.0], [0.0, a / 2 * numpy.sqrt(3.0), 0.0]]
    )
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    ic = mesh.get_inradius()
    assert near_equal(ic, [a / 4 * (numpy.sqrt(3) - 1)], tol)
    return


def test_circumradius():
    # 3-4-5 triangle
    points = numpy.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-15

    ic = mesh.get_circumradius()
    assert near_equal(ic, [2.5], tol)

    # 30-60-90 triangle
    a = 1.0
    points = numpy.array(
        [[0.0, 0.0, 0.0], [a / 2, 0.0, 0.0], [0.0, a / 2 * numpy.sqrt(3.0), 0.0]]
    )
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    ic = mesh.get_circumradius()
    assert near_equal(ic, [a / 2], tol)
    return


def test_quality():
    # 3-4-5 triangle
    points = numpy.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-15

    ic = mesh.get_quality()
    assert near_equal(ic, 2 * mesh.get_inradius() / mesh.get_circumradius(), tol)

    # 30-60-90 triangle
    a = 1.0
    points = numpy.array(
        [[0.0, 0.0, 0.0], [a / 2, 0.0, 0.0], [0.0, a / 2 * numpy.sqrt(3.0), 0.0]]
    )
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    ic = mesh.get_quality()
    assert near_equal(ic, 2 * mesh.get_inradius() / mesh.get_circumradius(), tol)
    return


def test_angles():
    # 3-4-5 triangle
    points = numpy.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 4.0, 0.0]])
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    tol = 1.0e-14

    ic = mesh.get_angles()
    assert near_equal(
        ic, [[numpy.pi / 2], [numpy.arcsin(4.0 / 5.0)], [numpy.arcsin(3.0 / 5.0)]], tol
    )

    # 30-60-90 triangle
    a = 1.0
    points = numpy.array(
        [[0.0, 0.0, 0.0], [a / 2, 0.0, 0.0], [0.0, a / 2 * numpy.sqrt(3.0), 0.0]]
    )
    cells = numpy.array([[0, 1, 2]])
    mesh = meshplex.MeshTri(points, cells)

    ic = mesh.get_angles() / numpy.pi * 180
    assert near_equal(ic, [[90], [60], [30]], tol)
    return


if __name__ == "__main__":
    # test_signed_area()
    # test_flip_delaunay_near_boundary()
    test_flip_same_edge_twice()

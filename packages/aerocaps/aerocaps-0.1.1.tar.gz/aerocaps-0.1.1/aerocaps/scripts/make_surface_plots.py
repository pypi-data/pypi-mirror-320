import os

import numpy as np
import pyvista as pv

import aerocaps as ac
import aerocaps.examples.bezier_surface
import aerocaps.examples.fill_surface


def plot_bezier_surf_2x3(image_dir: str = None):
    r"""
    Plots an :math:`(n \times m)=(2 \times 3)` Bézier surface along with the control point net.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf = aerocaps.examples.bezier_surface.bezier_surface_2x3()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5)
    surf.plot_control_points(plot, render_points_as_spheres=True, point_size=20, color="black")
    surf.plot_control_point_mesh_lines(plot, color="#d6693a")
    plot.camera.position = [-0.5, -0.7, 0.5]
    plot.camera.focal_point = [0.6, 0.5, -0.05]

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "bezier_surf_2x3.png"), scale=1)
    else:
        plot.show()


def plot_bezier_surf_2x3_mesh_only(image_dir: str = None):
    r"""
    Plots an :math:`(n \times m)=(2 \times 3)` Bézier surface with the isoparametric curves.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf = aerocaps.examples.bezier_surface.bezier_surface_2x3()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5, show_edges=True)
    plot.add_arrows(np.array([[0.1, 0.1, 0.05], [0.1, 0.1, 0.05]]), np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
                    mag=0.2, color="black")
    plot.add_point_labels(np.array([[0.1, 0.32, 0.05], [0.32, 0.1, 0.05]]), ["u", "v"], font_size=32)
    plot.camera.position = [-0.5, -0.7, 0.5]
    plot.camera.focal_point = [0.6, 0.5, -0.05]

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "bezier_surf_2x3_mesh_only.png"), scale=1)
    else:
        plot.show()


def plot_bezier_surf_2x3_uv_labels(image_dir: str = None):
    r"""
    Plots an :math:`(n \times m)=(2 \times 3)` Bézier surface along with the control point net.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf = aerocaps.examples.bezier_surface.bezier_surface_2x3()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5)
    surf.plot_control_points(plot, render_points_as_spheres=True, point_size=20, color="black")
    surf.plot_control_point_mesh_lines(plot, color="#d6693a")
    plot.add_arrows(np.array([[0.05, 0.05, 0.05], [0.05, 0.05, 0.05]]), np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
                    mag=0.2, color="black")
    plot.add_point_labels(np.array([[0.1, 0.32, 0.05], [0.32, 0.1, 0.05]]), ["u", "v"], font_size=32)
    plot.camera.position = [-0.5, -0.7, 0.5]
    plot.camera.focal_point = [0.6, 0.5, -0.05]

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "bezier_surf_2x3_uv_labels.png"), scale=1)
    else:
        plot.show()


def plot_bezier_surf_2x3_u_elevated(image_dir: str = None):
    r"""
    Plots an :math:`(n \times m)=(3 \times 3)` Bézier surface created by degree elevation from a
    :math:`2 \times 3` surface.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf = aerocaps.examples.bezier_surface.bezier_surface_2x3()
    surf = surf.elevate_degree_u()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5)
    surf.plot_control_points(plot, render_points_as_spheres=True, point_size=20, color="black")
    surf.plot_control_point_mesh_lines(plot, color="#d6693a")
    plot.add_arrows(np.array([[0.05, 0.05, 0.05], [0.05, 0.05, 0.05]]), np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
                    mag=0.2, color="black")
    plot.add_point_labels(np.array([[0.1, 0.32, 0.05], [0.32, 0.1, 0.05]]), ["u", "v"], font_size=32)
    plot.camera.position = [-0.5, -0.7, 0.5]
    plot.camera.focal_point = [0.6, 0.5, -0.05]

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "bezier_surf_3x3_from_u_elevation.png"), scale=1)
    else:
        plot.show()


def plot_bezier_surf_2x3_v_elevated(image_dir: str = None):
    r"""
    Plots an :math:`(n \times m)=(2 \times 4)` Bézier surface created by degree elevation from a
    :math:`2 \times 3` surface.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf = aerocaps.examples.bezier_surface.bezier_surface_2x3()
    surf = surf.elevate_degree_v()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5)
    surf.plot_control_points(plot, render_points_as_spheres=True, point_size=20, color="black")
    surf.plot_control_point_mesh_lines(plot, color="#d6693a")
    plot.add_arrows(np.array([[0.05, 0.05, 0.05], [0.05, 0.05, 0.05]]), np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
                    mag=0.2, color="black")
    plot.add_point_labels(np.array([[0.1, 0.32, 0.05], [0.32, 0.1, 0.05]]), ["u", "v"], font_size=32)
    plot.camera.position = [-0.5, -0.7, 0.5]
    plot.camera.focal_point = [0.6, 0.5, -0.05]

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "bezier_surf_2x4_from_v_elevation.png"), scale=1)
    else:
        plot.show()


def plot_fill_surface(image_dir: str = None):
    r"""
    Plots a fill surface along with its boundary curves.

    Parameters
    ----------
    image_dir: str or None
        Where to store the output image. If no location is specified, the image file will not be saved, and the
        plot will be displayed on-screen instead. Default: ``None``
    """
    plot = pv.Plotter(off_screen=True if image_dir else False, window_size=[1024, 600])

    # Load the example surface
    surf, boundaries = aerocaps.examples.fill_surface.fill_surface_four_sided()

    surf.plot_surface(plot, color="#4d86b8", opacity=0.5)
    for curve in boundaries:
        curve.plot(plot, color="black")
    # surf.plot_control_points(plot, render_points_as_spheres=True, point_size=20, color="black")
    # surf.plot_control_point_mesh_lines(plot, color="#d6693a")
    plot.camera.position = [-1.2, -0.9, 1.0]
    plot.camera.focal_point = [0.6, 0.5, -0.05]
    plot.camera.zoom(1.2)

    if image_dir is not None:
        plot.screenshot(os.path.join(image_dir, "fill_surface.png"), scale=1)
    else:
        plot.show()


def main(*args, **kwargs):
    # plot_bezier_surf_2x3(*args, **kwargs)
    # plot_bezier_surf_2x3_uv_labels(*args, **kwargs)
    # plot_bezier_surf_2x3_mesh_only(*args, **kwargs)
    # plot_bezier_surf_2x3_u_elevated(*args, **kwargs)
    # plot_bezier_surf_2x3_v_elevated(*args, **kwargs)
    plot_fill_surface(*args, **kwargs)


if __name__ == "__main__":
    # main()
    main(image_dir=r"C:\Users\mlaue\Documents\aerocaps\docs\source\images")

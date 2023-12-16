"""This module generates a 3D model of a lithophane from an given image."""
import os

import matplotlib.image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from skimage.transform import resize
from stl import mesh

from lithophane.metadata import __author__  # noqa: F401
from lithophane.metadata import __authors__  # noqa: F401
from lithophane.metadata import __classifiers__  # noqa: F401
from lithophane.metadata import __email__  # noqa: F401
from lithophane.metadata import __keywords__  # noqa: F401
from lithophane.metadata import __license__  # noqa: F401
from lithophane.metadata import __maintainer__  # noqa: F401
from lithophane.metadata import __url__  # noqa: F401
from lithophane.metadata import __version__  # noqa: F401

RESOLUTION = 0.1  # mm/pixel


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    """Convert rgb image to grayscale image in range 0-1.

    Args:
        rgb (numpy array): RGB image

    Returns:
        numpy array: Grayscale image

    """
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def scale_image(img: np.ndarray, width_mm: int = 40) -> np.ndarray:
    """Scale image to given width in mm with given resolution in mm/pixel.

    Args:
        img (numpy array): Image to scale
        width_mm (int, optional): Width of image in mm. Defaults to 40.

    Returns:
        numpy array: Scaled image

    For example the following:

    >>> im_scaled = scaleim(im, width_mm = 100)

    Will make an image with 1000 pixels wide, if RESOLUTION is 0.1 mm/pixel.
    The height will be scale proportionally.
    """

    y_dim = img.shape[0]
    x_dim = img.shape[1]

    scale = width_mm / RESOLUTION / x_dim
    new_shape = (int(y_dim * scale), int(x_dim * scale), 3)
    img = resize(img, new_shape)
    return img


def jpg_to_stl(
    img_path: os.PathLike,
    width_mm: float = None,
    depth_mm: float = 3.0,
    offset_mm: float = 0.5,
    frame_mm: float = 0.0,
    show: bool = True,
):
    """Function to convert filename to stl with given width.

    Args:
        img_path (os.PathLike): Path to image file
        width_mm (int, optional): Width of image in mm. Defaults to None.
        depth_mm (float, optional): Depth of image in mm. Defaults to 3.0.
        offset_mm (float, optional): Offset of image in mm. Defaults to 0.5.
        frame_mm (float, optional): Frame around image in mm. Defaults to 0.0.
        show (bool, optional): Show image. Defaults to True.

    """

    img = matplotlib.image.imread(img_path)

    if not width_mm:
        width_mm = img.shape[1]

    img = scale_image(img, width_mm=width_mm)

    # Normalize image
    img = img / np.max(img)

    # Convert to grayscale
    if len(img.shape) == 3:
        img = rgb_to_gray(img)

    if show:
        plt.imshow(img, cmap=plt.get_cmap("gray"))

    # Invert threshold for z matrix
    img = 1 - np.double(img)

    # Scale z matrix to desired max depth and add base height
    z = img * depth_mm + offset_mm

    # Add a frame around the image
    if frame_mm > 0:
        frame_pxl = int(frame_mm / RESOLUTION)
        framed_z = np.full(
            [z.shape[0] + 2 * frame_pxl, z.shape[1] + 2 * frame_pxl],
            depth_mm + offset_mm,
        )
        framed_z[frame_pxl:-frame_pxl, frame_pxl:-frame_pxl] = z
        z = framed_z

    # Add border of zeros to help with back.
    z_with_back = np.zeros([z.shape[0] + 2, z.shape[1] + 2])
    z_with_back[1:-1, 1:-1] = z
    z = z_with_back

    x1 = np.linspace(1, z.shape[1] * RESOLUTION, z.shape[1])
    y1 = np.linspace(1, z.shape[0] * RESOLUTION, z.shape[0])

    x, y = np.meshgrid(x1, y1)

    x = np.fliplr(x)

    return x, y, z


def make_cylinder(x, y, z):
    """Convert flat point cloud to Cylinder"""
    newx = x.copy()
    newz = z.copy()
    radius = (np.max(x) - np.min(x)) / (2 * np.pi)
    print(f"Cylinder Radius {radius}mm")
    for r in range(0, x.shape[0]):
        for c in range(0, x.shape[1]):
            t = (c / (x.shape[1] - 10)) * 2 * np.pi
            rad = radius + z[r, c]
            newx[r, c] = rad * np.cos(t)
            newz[r, c] = rad * np.sin(t)
    return newx, y.copy(), newz


# Construct polygons from grid data


def make_mesh(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> mesh:
    """Convert point cloud grid to mesh.

    Args:
        x (numpy array): x coordinates
        y (numpy array): y coordinates
        z (numpy array): z coordinates

    Returns:
        mesh: mesh object

    """
    count = 0
    points = []
    triangles = []
    for i in range(z.shape[0] - 1):
        for j in range(z.shape[1] - 1):
            # Triangle 1
            points.append([x[i][j], y[i][j], z[i][j]])
            points.append([x[i][j + 1], y[i][j + 1], z[i][j + 1]])
            points.append([x[i + 1][j], y[i + 1][j], z[i + 1][j]])

            triangles.append([count, count + 1, count + 2])

            # Triangle 2
            points.append([x[i][j + 1], y[i][j + 1], z[i][j + 1]])
            points.append([x[i + 1][j + 1], y[i + 1][j + 1], z[i + 1][j + 1]])
            points.append([x[i + 1][j], y[i + 1][j], z[i + 1][j]])

            triangles.append([count + 3, count + 4, count + 5])

            count += 6

    # BACK
    for j in range(x.shape[1] - 1):
        bot = x.shape[0] - 1

        # Back Triangle 1
        points.append([x[bot][j], y[bot][j], z[bot][j]])
        points.append([x[0][j + 1], y[0][j + 1], z[0][j + 1]])
        points.append([x[0][j], y[0][j], z[0][j]])

        triangles.append([count, count + 1, count + 2])

        # Triangle 2
        points.append([x[bot][j], y[bot][j], z[bot][j]])
        points.append([x[bot][j + 1], y[bot][j + 1], z[bot][j + 1]])
        points.append([x[0][j + 1], y[0][j + 1], z[0][j + 1]])

        triangles.append([count + 3, count + 4, count + 5])

        count += 6

    # Create the mesh
    model = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(triangles):
        for j in range(3):
            model.vectors[i][j] = points[f[j]]

    return model


def show_stl(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> None:
    """
    Demonstrates plotting a 3D surface colored with the coolwarm color map.
    The surface is made opaque by using antialiased=False.

    Also demonstrates using the LinearLocator and custom formatting for the
    z axis tick labels.

    Args:
        x (numpy array): x coordinates
        y (numpy array): y coordinates
        z (numpy array): z coordinates
    """

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # Plot the surface.
    ax.plot_surface(x, y, z, cmap=cm.coolwarm, linewidth=0, antialiased=False)

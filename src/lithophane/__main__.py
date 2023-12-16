"""Command line interface for lithophane."""
import argparse
from pathlib import Path

import lithophane as li

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create lithophane from image.")
    parser.add_argument("image_path", type=Path, help="Path to image file.")
    parser.add_argument(
        "--width",
        "-w",
        type=float,
        help=(
            "Width of image in mm. Defaults to image width. "
            "Height is calculated to maintain aspect ratio."
        ),
        default=None,
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=float,
        help="Depth of image in mm. Defaults to 3.0 mm.",
        default=3.0,
    )
    parser.add_argument(
        "--offset",
        "-o",
        type=float,
        help="Offset of image in mm. Defaults to 0.5 mm.",
        default=0.5,
    )
    parser.add_argument(
        "--frame",
        "-f",
        type=float,
        help="Frame around image in mm. Defaults to 0.0 mm.",
        default=0.0,
    )
    parser.add_argument(
        "--show", action="store_true", help="Show image and point cloud"
    )
    args = parser.parse_args()

    # Generate xyz point cloud
    print(f"Generating point cloud from {args.image_path}...")
    x, y, z = li.jpg_to_stl(
        img_path=args.image_path,
        width_mm=args.width,
        depth_mm=args.depth,
        offset_mm=args.offset,
        frame_mm=args.frame,
        show=args.show,
    )

    # Show the point cloud
    if args.show:
        li.show_stl(x, y, z)

    # Generate stl model from point cloud
    print("Generating stl from point cloud...")
    model = li.make_mesh(x, y, z)

    # Save stl
    flat_stl_path = args.image_path.with_suffix(".stl")
    print(f"Saving stl to {flat_stl_path}...")
    model.save(flat_stl_path)

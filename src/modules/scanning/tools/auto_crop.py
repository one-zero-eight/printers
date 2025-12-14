"""Auto-crop and rotate scanned PDF documents using DocAligner."""

import argparse
import io
import sys
import time
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pymupdf
from docaligner import DocAligner
from PIL import Image

doc_aligner_model = DocAligner()


def draw_corners(img_array: np.ndarray, corners: np.ndarray, color=(0, 255, 0), thickness=7) -> np.ndarray:
    """Draw detected corners on the image for visualization."""
    img_copy = img_array.copy()
    corners_int = corners.astype(int)

    # Draw lines connecting corners using polylines
    if len(corners_int) == 4:
        pts = np.array(corners_int, dtype=np.int32)
        cv2.polylines(img_copy, [pts], True, color, thickness)

    # Draw corner points - make them more noticeable
    for corner in corners_int:
        x, y = int(corner[0]), int(corner[1])
        cv2.circle(img_copy, (x, y), 20, color, thickness)
        cv2.circle(img_copy, (x, y), 35, color, thickness // 2)

    return img_copy


def apply_perspective_transform(img_array: np.ndarray, corners: np.ndarray) -> np.ndarray:
    """
    Rotate and crop the image to straighten the document without perspective warping.
    corners: 4x2 array of corner coordinates in order [top-left, top-right, bottom-right, bottom-left]
    """
    H, W = img_array.shape[:2]

    # Calculate rotation angle from the top edge
    top_edge = corners[1] - corners[0]  # top-right - top-left
    angle_rad = np.arctan2(top_edge[1], top_edge[0])
    angle_deg = np.degrees(angle_rad)

    # Get rotation center (center of image)
    center = (W / 2, H / 2)

    # Get rotation matrix
    M_rotate = cv2.getRotationMatrix2D(center, angle_deg, 1.0)

    # Calculate bounding box of rotated image
    cos = np.abs(M_rotate[0, 0])
    sin = np.abs(M_rotate[0, 1])
    new_W = int((H * sin) + (W * cos))
    new_H = int((H * cos) + (W * sin))

    # Adjust rotation matrix for new image size
    M_rotate[0, 2] += (new_W / 2) - center[0]
    M_rotate[1, 2] += (new_H / 2) - center[1]

    # Rotate the image
    rotated = cv2.warpAffine(img_array, M_rotate, (new_W, new_H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    # Transform corners to rotated coordinate system
    corners_homogeneous = np.hstack([corners, np.ones((4, 1))])
    rotated_corners = (M_rotate @ corners_homogeneous.T).T

    # Find bounding box of rotated corners
    x_min = int(np.min(rotated_corners[:, 0]))
    y_min = int(np.min(rotated_corners[:, 1]))
    x_max = int(np.max(rotated_corners[:, 0]))
    y_max = int(np.max(rotated_corners[:, 1]))

    # Crop to bounding box
    cropped = rotated[y_min:y_max, x_min:x_max]

    return cropped


def save_debug_figures(img_original: np.ndarray, corners: np.ndarray | None, img_cropped: np.ndarray, output_path: Path, page_index: int) -> None:
    """Save debug figures showing original, detected corners, and cropped images."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Original image
    axes[0].imshow(img_original)
    axes[0].set_title("Original", fontsize=14, fontweight="bold")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    # Add border
    for spine in axes[0].spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("black")
        spine.set_linewidth(2)

    # Detected corners
    if corners is not None and len(corners) == 4:
        img_with_corners = draw_corners(img_original, corners)
        axes[1].imshow(img_with_corners)
        axes[1].set_title("Detected Corners", fontsize=14, fontweight="bold")
    else:
        axes[1].imshow(img_original)
        axes[1].set_title("Detected Corners (None)", fontsize=14, fontweight="bold")
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    # Add border
    for spine in axes[1].spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("black")
        spine.set_linewidth(2)

    # Cropped result
    axes[2].imshow(img_cropped)
    axes[2].set_title("Cropped", fontsize=14, fontweight="bold")
    axes[2].set_xticks([])
    axes[2].set_yticks([])
    # Add border
    for spine in axes[2].spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("black")
        spine.set_linewidth(2)

    plt.tight_layout()
    debug_path = output_path.parent / f"{output_path.stem}_debug_page{page_index}.png"
    plt.savefig(debug_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Debug figure saved: {debug_path}", flush=True)


def autocrop_pdf_bytes(pdf_bytes: bytes, debug: bool = False, debug_output_path: Path | None = None) -> bytes:
    """Convert each page to image, auto-crop and rotate, then rebuild a PDF."""
    src = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(src)
    very_start_time = time.perf_counter()

    dpi = 300  # default fallback

    # Create new PDF for output
    out_pdf = pymupdf.open()

    for page_index, page in enumerate(src, start=1):
        page_rect = page.rect
        page_width_pp = page_rect.width
        page_height_pp = page_rect.height
        image_list = page.get_images()
        if image_list:
            # Use the first image found on the page
            xref = image_list[0][0]
            pix = pymupdf.Pixmap(src, xref)
            if pix.n - pix.alpha > 3:  # CMYK to RGB
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

            # Get DPI from the first image on the page by comparing image size to page size
            dpi_x = (pix.width / page_width_pp) * 72 if page_width_pp > 0 else dpi
            dpi_y = (pix.height / page_height_pp) * 72 if page_height_pp > 0 else dpi
            dpi = int((dpi_x + dpi_y) / 2)  # average of x and y DPI
        else:
            raise ValueError("No images found on page")
        img_array = np.frombuffer(pix.samples_mv, dtype=np.uint8).reshape((pix.height, pix.width, 3))

        # Time the detection
        start_time = time.perf_counter()
        corners = doc_aligner_model(img_array)  # 4x2 array: [[x,y], ...]
        elapsed = time.perf_counter() - start_time

        if corners is not None and len(corners) == 4:
            # print(f"Page {page_index}/{total_pages}: Detection took {elapsed:.3f}s", flush=True)
            # Apply perspective transformation
            img_processed = apply_perspective_transform(img_array, corners)
        else:
            # print(
            #     f"Page {page_index}/{total_pages}: Detection took {elapsed:.3f}s ({len(corners) if corners is not None else 0} corners != 4 detected, using original)",
            #     flush=True,
            # )
            img_processed = img_array

        # Save debug figures if enabled
        if debug and debug_output_path:
            save_debug_figures(img_array, corners, img_processed, debug_output_path, page_index)

        # Create PDF page from processed image
        img_processed = Image.fromarray(img_processed)
        buffer = io.BytesIO()
        img_processed.save(buffer, format="JPEG")
        buffer.seek(0)

        # Page size in points (72 DPI)
        scale = 72.0 / dpi
        page_width = img_processed.width * scale
        page_height = img_processed.height * scale

        new_page = out_pdf.new_page(width=page_width, height=page_height)
        new_page.insert_image(new_page.rect, stream=buffer.getvalue())

    src.close()
    # total_time = time.perf_counter() - very_start_time
    # print(f"Total processing time: {total_time:.3f}s (average: {total_time / total_pages:.3f}s per page)")

    out = io.BytesIO()
    out_pdf.save(out, garbage=4, deflate=True)
    out_pdf.close()
    return out.getvalue()


def image_to_pdf_bytes(image_path: Path) -> bytes:
    """Convert an image file to PDF bytes."""
    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Create PDF from image
    pdf_doc = pymupdf.open()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Use image dimensions directly (1 pixel = 1 point)
    page = pdf_doc.new_page(width=img.width, height=img.height)
    page.insert_image(page.rect, stream=img_bytes.getvalue())

    out = io.BytesIO()
    pdf_doc.save(out, garbage=4, deflate=True)

    pdf_doc.close()
    return out.getvalue()


def autocrop_pdf(input_path: Path, output_path: Path | None = None, debug: bool = False) -> None:
    """Auto-crop and rotate all pages in a scanned PDF document."""
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix.lower() == ".pdf":
        print(f"Error: Input file must be a PDF: {input_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_cropped{input_path.suffix}"

    print(f"Processing PDF: {input_path}")
    pdf_bytes = input_path.read_bytes()
    cropped_pdf_bytes = autocrop_pdf_bytes(pdf_bytes, debug=debug, debug_output_path=output_path)

    print(f"Saving cropped PDF to: {output_path}")
    output_path.write_bytes(cropped_pdf_bytes)

    print(f"Successfully created cropped PDF: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto-crop and rotate scanned PDF documents or images using DocAligner"
    )
    parser.add_argument("input", type=Path, help="Path to input PDF file or image file")
    parser.add_argument("-o", "--output", type=Path, help="Path to output PDF file (default: input_cropped.pdf)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to save visualization figures")
    args = parser.parse_args()

    # Check if input is PDF or image
    input_ext = args.input.suffix.lower()
    if input_ext == ".pdf":
        autocrop_pdf(args.input, args.output, debug=args.debug)
    elif input_ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"]:
        # Convert image to PDF first, then process
        print(f"Converting image to PDF: {args.input}")
        pdf_bytes = image_to_pdf_bytes(args.input)

        debug_output_path = None
        if args.debug:
            debug_output_path = args.output if args.output else args.input.parent / f"{args.input.stem}_cropped.pdf"

        cropped_pdf_bytes = autocrop_pdf_bytes(pdf_bytes, debug=args.debug, debug_output_path=debug_output_path)

        if args.output is None:
            args.output = args.input.parent / f"{args.input.stem}_cropped.pdf"

        print(f"Saving cropped PDF to: {args.output}")
        args.output.write_bytes(cropped_pdf_bytes)
        print(f"Successfully created cropped PDF: {args.output}")
    else:
        print(
            f"Error: Unsupported file type: {input_ext}. Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF, TIF, WEBP",
            file=sys.stderr,
        )
        sys.exit(1)

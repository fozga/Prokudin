"""
Image alignment utilities for RGB channel processing.
Aligns green and blue channels to the red channel using ORB feature matching and affine transformation.
"""

from typing import List, Tuple

import cv2  # type: ignore
import numpy as np


class AlignmentError(Exception):
    """Custom exception for alignment errors."""


def align_images(
    grayscale_images: List[np.ndarray], rgb_images: List[np.ndarray]
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Aligns green and blue channels to the red channel using ORB feature matching
    and affine transformation. Uses grayscale images for feature detection and
    applies the same transformations to both grayscale and RGB images.

    Args:
        grayscale_images (list of numpy.ndarray): List of three grayscale images (R, G, B), each as a 2D numpy array.
        rgb_images (list of numpy.ndarray): List of three RGB images corresponding to the grayscale images.

    Returns:
        tuple: A tuple containing:
            - list of numpy.ndarray: List of aligned grayscale images [R, G, B]
            - list of numpy.ndarray: List of aligned RGB images [R, G, B]

    Raises:
        AlignmentError: If alignment fails due to insufficient matches or transformation errors.

    Cross-references:
        - handlers.channels.load_channel
    """
    # Start with copies of the originals
    aligned_grayscale = [img.copy() for img in grayscale_images]

    # Initialize aligned RGB with copies of original RGB images
    aligned_rgb = [img.copy() for img in rgb_images]

    # ORB detector with increased features for better matching
    # 1000 features balances performance/accuracy
    orb = cv2.ORB_create(1000)  # type: ignore[attr-defined]  # pylint: disable=E1101
    keypoints = []
    descriptors = []

    # Detect features for all channels using grayscale images
    for img in grayscale_images:
        kp, des = orb.detectAndCompute(img, None)
        keypoints.append(kp)
        descriptors.append(des)

    # Align G (1) and B (2) to R (0)
    for i in range(1, 3):
        if (
            descriptors[0] is not None
            and descriptors[i] is not None
            and descriptors[0].size > 0
            and descriptors[i].size > 0
        ):

            # Brute-force matching with Hamming distance
            matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(  # pylint: disable=E1101
                descriptors[0], descriptors[i]
            )

            min_matches = 50  # Minimum matches for reliable alignment
            if len(matches) < min_matches:
                raise AlignmentError(f"Insufficient matches ({len(matches)}/{min_matches})")
            # Convert match points to numpy arrays
            # Estimate partial affine transform (rotation, translation, scaling)
            matrix, _ = cv2.estimateAffinePartial2D(  # pylint: disable=E1101
                np.array([keypoints[i][m.trainIdx].pt for m in matches], dtype=np.float32).reshape((-1, 1, 2)),
                np.array([keypoints[0][m.queryIdx].pt for m in matches], dtype=np.float32).reshape((-1, 1, 2)),
            )
            if matrix is None:
                raise AlignmentError(f"Failed to estimate transformation for channel {i}")

            # Apply transformation to grayscale image
            aligned_grayscale[i] = cv2.warpAffine(  # pylint: disable=E1101
                grayscale_images[i], matrix, (grayscale_images[0].shape[1], grayscale_images[0].shape[0])
            )

            # Apply the same transformation to RGB image - no need to check for None
            aligned_rgb[i] = cv2.warpAffine(  # pylint: disable=E1101
                rgb_images[i], matrix, (rgb_images[0].shape[1], rgb_images[0].shape[0])
            )

    return aligned_grayscale, aligned_rgb

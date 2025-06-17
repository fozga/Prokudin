"""
Image alignment utilities for RGB channel processing.
Aligns green and blue channels to the red channel using ORB feature matching and affine transformation.
"""

import cv2  # type: ignore
import numpy as np


class AlignmentError(Exception):
    """Custom exception for alignment errors."""


def align_images(original_images: list) -> list:
    """
    Aligns green and blue channels to the red channel using ORB feature matching
    and affine transformation.

    Args:
        original_images (list of numpy.ndarray): List of three grayscale images (R, G, B), each as a 2D numpy array.

    Returns:
        list of numpy.ndarray: List of aligned images [R, G, B].

    Raises:
        AlignmentError: If alignment fails due to insufficient matches or transformation errors.

    Cross-references:
        - handlers.channels.load_channel
    """

    # Start with copies of the originals
    aligned = [img.copy() for img in original_images]

    # ORB detector with increased features for better matching
    # 1000 features balances performance/accuracy
    orb = cv2.ORB_create(1000)  # type: ignore[attr-defined]  # pylint: disable=E1101
    keypoints = []
    descriptors = []

    # Detect features for all channels
    for img in original_images:
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
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # pylint: disable=E1101
            matches = bf.match(descriptors[0], descriptors[i])

            min_matches = 50  # Minimum matches for reliable alignment
            if len(matches) < min_matches:
                raise AlignmentError(f"Insufficient matches ({len(matches)}/{min_matches})")
            # Convert match points to numpy arrays
            src_pts = np.array([keypoints[0][m.queryIdx].pt for m in matches], dtype=np.float32).reshape((-1, 1, 2))
            dst_pts = np.array([keypoints[i][m.trainIdx].pt for m in matches], dtype=np.float32).reshape((-1, 1, 2))

            # Estimate partial affine transform (rotation, translation, scaling)
            matrix, _ = cv2.estimateAffinePartial2D(dst_pts, src_pts)  # pylint: disable=E1101
            if matrix is None:
                raise AlignmentError(f"Failed to estimate transformation for channel {i}")
            # Apply transformation using reference channel dimensions
            aligned[i] = cv2.warpAffine(  # pylint: disable=E1101
                original_images[i], matrix, (original_images[0].shape[1], original_images[0].shape[0])
            )
    return aligned

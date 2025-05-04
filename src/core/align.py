import cv2
import numpy as np

def align_images(original_images):
    """
    Aligns green and blue channels to the red channel using ORB features and affine transformation.
    :param original_images: list of 3 grayscale numpy arrays [R, G, B]
    :return: list of aligned images [R, G_aligned, B_aligned]
    """
    # Start with copies of the originals
    aligned = [img.copy() for img in original_images]

    orb = cv2.ORB_create(1000)
    keypoints = []
    descriptors = []

    # Detect features for all images
    for img in original_images:
        kp, des = orb.detectAndCompute(img, None)
        keypoints.append(kp)
        descriptors.append(des)

    # Align G and B to R (index 0)
    for i in range(1, 3):
        if (descriptors[0] is not None and descriptors[i] is not None and
            descriptors[0].size > 0 and descriptors[i].size > 0):

            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(descriptors[0], descriptors[i])

            if len(matches) > 10:
                src_pts = np.float32([keypoints[0][m.queryIdx].pt for m in matches]).reshape(-1,1,2)
                dst_pts = np.float32([keypoints[i][m.trainIdx].pt for m in matches]).reshape(-1,1,2)

                # Estimate affine transform from G/B to R
                M, _ = cv2.estimateAffinePartial2D(dst_pts, src_pts)
                if M is not None:
                    aligned[i] = cv2.warpAffine(
                        original_images[i], M,
                        (original_images[0].shape[1], original_images[0].shape[0])
                    )
    return aligned

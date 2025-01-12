from pathlib import Path
from skimage.io import imread, imsave
from skimage.measure import regionprops_table
import numpy as np
import pandas as pd
import SimpleITK as sitk
from natsort import natsorted
from carde.io import (
    local_data_path,
    image_path,
    label_path,
    read_image_pair,
    get_image_number,
    calculate_matching_image_number,
)
from warnings import warn

pixel_size_um = 1 / 180


def get_metadata_index(image):
    """
    Get the index of the metadata in the image so that we can crop the metadata away for further processing.

    This function finds the large bright object containing the metadata in the image and returns the index of the row just before the first row of the object.

    Parameters:
    image (numpy.ndarray): The input image as a NumPy array.

    Returns:
    int: The index of the row just before the first occurrence of 255 in the image.
    """
    mask = sitk.OtsuThreshold(sitk.GetImageFromArray(image), 0, 1)
    mask = sitk.ConnectedComponent(mask)
    mask = sitk.RelabelComponent(mask, minimumObjectSize=10 * image.shape[1])
    label_stats = sitk.LabelShapeStatisticsImageFilter()
    label_stats.Execute(mask)

    largest_label = 0
    largest_label_size = 0
    for label in label_stats.GetLabels():
        if label_stats.GetNumberOfPixels(label) > largest_label_size:
            largest_label = label
            largest_label_size = label_stats.GetNumberOfPixels(label)
    mask = sitk.BinaryThreshold(mask, largest_label, largest_label, 1, 0)
    mask = sitk.GetArrayFromImage(mask)
    return min(np.where(mask)[0]) - 1


def crop_away_metadata(image: np.ndarray, metadata_index: int = None) -> np.ndarray:
    """
    Crops the metadata away from the given image.

    Parameters
    ----------
    image: np.ndarray
        The image to crop.
    metadata_index: int (optional)
        The row index at which the metadata starts in the image. Everything before this index will be cropped away. Defult is to determine the index automatically using get_metadata_index.

    Returns
    -------
    np.ndarray
        The cropped image.
    """
    if metadata_index is None:
        metadata_index = get_metadata_index(image)
    if metadata_index == -1:
        warn("No metadata found in the image. Returning the original image.")
        return image
    return image[:metadata_index, ...]


def preprocess_image(image_path: Path) -> np.ndarray:
    """
    Preprocesses an image by cropping away metadata and optionally processing a corresponding label image.

    Args:
        image_path (Path): The path to the image file to be processed.

    Returns:
        Tuple[np.ndarray, Optional[np.ndarray]]: A tuple containing the cropped image and the cropped label image.
            The cropped label image is None if the corresponding label image file does not exist.
    """
    image = imread(image_path)
    # crop off the metadata
    metadata_index = get_metadata_index(image)
    cropped_image = crop_away_metadata(image, metadata_index)
    label_image_path = image_path.parent.parent.glob("*Image_All.bmp").__next__()
    if label_image_path.exists():
        # crop off the metadata
        cropped_label_image = crop_away_metadata(imread(label_image_path), metadata_index)[:, :, 2] == 255
        assert (
            cropped_image.shape == cropped_label_image.shape
        ), f"Image and label image must have the same shape. Got image shape: {cropped_image.shape} and label image shape: {cropped_label_image.shape}."
    else:
        cropped_label_image = None
    return cropped_image, cropped_label_image


def preprocess_images(
    data_path: Path = local_data_path, target_image_path: Path = image_path, target_label_path: Path = label_path
):
    """
    Preprocess images from the specified data path and save the preprocessed images and labels to the target paths.

    Args:
        data_path (Path): The path to the directory containing the original images.
        target_image_path (Path): The path to the directory where the preprocessed images will be saved.
        target_label_path (Path): The path to the directory where the preprocessed label images will be saved.

    Returns:
        None

    Notes:
        - The function expects the images to be in subdirectories named with digits and containing 'Original' in their names.
        - The preprocessed images are saved in the target_image_path directory with the same name as the original images.
        - If a preprocessed label image is generated, it is saved in the target_label_path directory with '_label.png' appended to the original image name.
    """

    # load the images
    image_paths = data_path.glob("[0-9]*/Original*/*.tif")

    # preprocess the images
    for image_path in image_paths:
        cropped_image, cropped_label_image = preprocess_image(image_path)
        # save the preprocessed image
        target_image_path.mkdir(exist_ok=True, parents=True)
        cropped_image_path = target_image_path / image_path.name
        imsave(cropped_image_path, cropped_image)
        if cropped_label_image is not None:
            # save the preprocessed label image
            target_label_path.mkdir(exist_ok=True, parents=True)
            cropped_label_image_path = target_label_path / (image_path.stem + "_label.png")
            imsave(cropped_label_image_path, np.uint8(cropped_label_image * 255))
        print(f"Preprocessed {image_path.name}")


def segment_otsu(image: np.ndarray, sigma: float = 1.0, radius: float = 30.0, minimum_size: int = 3) -> np.ndarray:
    """
    Segments the given image using Otsu's method.

    Parameters
    ----------
    image: np.ndarray
        The image to segment.
    sigma: float
        The standard deviation of the Gaussian filter.
    radius: float
        The radius of the white tophat background removal operation.
    minimum_size: int
        The minimum size of the objects to keep.

    Returns
    -------
    np.ndarray
        The segmented image.
    """
    # denoise the image

    segmented = sitk.GetImageFromArray(image)
    segmented = sitk.DiscreteGaussian(segmented, variance=[sigma, sigma])
    # subtract the background
    if radius > 0:
        segmented = sitk.WhiteTopHat(segmented, kernelRadius=[30, 30])
    # threshold the image
    segmented = sitk.OtsuThreshold(segmented, 0, 1)
    segmented = sitk.BinaryFillhole(segmented)
    segmented = sitk.ConnectedComponent(segmented)
    segmented = sitk.RelabelComponent(segmented, minimumObjectSize=minimum_size)
    return sitk.GetArrayFromImage(segmented)


def segment_combined(image_SE2: np.ndarray, image_inlens: np.ndarray, *args, **kwargs) -> np.ndarray:
    """
    Segments the average of two images using Otsu's method.

    Parameters
    ----------
    image_SE2: np.ndarray
        The SE2 image.
    image_inlens: np.ndarray
        The inlens image.
    *args
        Additional arguments for [segment_otsu](#segment_otsu).
    **kwargs
        Additional keyword arguments for [segment_otsu](#segment_otsu).

    Returns
    -------
    np.ndarray
        The segmented image.
    """
    # combine the images
    combined = (image_SE2 // 2) + (image_inlens // 2)
    return segment_otsu(combined, *args, **kwargs)


def evaluate_segmentation(
    label_image: np.ndarray,
    properties: tuple[str] = (
        "label",
        "area",
        "axis_major_length",
        "axis_minor_length",
        "centroid",
        "orientation",
    ),
) -> pd.DataFrame:
    """
    Evaluates the given segmentation.

    Parameters
    ----------
    label_image: np.ndarray
        The label image.
    properties: tuple[str]
        The properties to evaluate. See [skimage.measure.regionprops](https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops) for details.

    Returns
    -------
    pd.DataFrame
        The evaluation results.
    """
    # evaluate the segmentation
    props = regionprops_table(label_image=label_image, properties=properties, spacing=(pixel_size_um, pixel_size_um))
    return pd.DataFrame(props)


def process_folder(image_folder: Path, output_folder: Path):
    """
    Preprocesses the images in the given folder and saves the preprocessed images and labels to the output folder.

    Parameters
    ----------
    image_folder: Path
        The path to the folder containing the original images.
    output_folder: Path
        The path to the folder where the preprocessed images and labels will be saved.

    Returns
    -------
    None
    """
    last_processed = Path("dummy_00.tif")
    for path_to_image in natsorted(image_folder.glob("*.tif")):
        matching_image_number = calculate_matching_image_number(get_image_number(path_to_image))
        if matching_image_number == get_image_number(last_processed):
            continue
        print(f"Processing {path_to_image}")
        inlens_image, se_image = read_image_pair(path_to_image)
        inlens_image = crop_away_metadata(inlens_image)
        se_image = crop_away_metadata(se_image)
        segmented = segment_combined(se_image, inlens_image)
        output_name = path_to_image.stem + f"-{matching_image_number:02d}"
        imsave(output_folder / (output_name + "_label.tif"), segmented, check_contrast=False)
        df = evaluate_segmentation(segmented)
        df.to_csv(output_folder / (output_name + "_table.csv"))
        last_processed = path_to_image

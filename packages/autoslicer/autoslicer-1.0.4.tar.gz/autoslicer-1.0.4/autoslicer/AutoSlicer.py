import os
import SimpleITK as sitk
import nibabel as nib
import numpy as np
import torch
from totalsegmentator.python_api import totalsegmentator
from totalsegmentator.nifti_ext_header import load_multilabel_nifti

# Global or class-level density map (if per-instance densities are needed, move it inside the __init__ method)
DENSITY_MAP = {
    1: 1.05, 2: 1.06, 3: 1.06, 4: 1.02, 5: 1.05, 6: 1.04, 7: 1.04, 8: 1.04, 9: 1.04,
    10: 0.3, 11: 0.3, 12: 0.3, 13: 0.3, 14: 0.3, 15: 1.04, 16: 0.8, 17: 1.04, 18: 1.04,
    19: 1.04, 20: 1.04, 21: 1.05, 22: 1.04, 23: 1.01, 24: 1.01, 25: 1.9, 26: 1.9,
    27: 1.9, 28: 1.9, 29: 1.9, 30: 1.9, 31: 1.9, 32: 1.9, 33: 1.9, 34: 1.9, 35: 1.9,
    36: 1.9, 37: 1.9, 38: 1.9, 39: 1.9, 40: 1.9, 41: 1.9, 42: 1.9, 43: 1.9, 44: 1.9,
    45: 1.9, 46: 1.9, 47: 1.9, 48: 1.9, 49: 1.9, 50: 1.9, 51: 1.06, 52: 1.05, 53: 1.05,
    54: 1.05, 55: 1.05, 56: 1.05, 57: 1.05, 58: 1.05, 59: 1.05, 60: 1.05, 61: 1.06,
    62: 1.05, 63: 1.05, 64: 1.05, 65: 1.05, 66: 1.05, 67: 1.05, 68: 1.05, 69: 1.85,
    70: 1.85, 71: 1.85, 72: 1.85, 73: 1.85, 74: 1.85, 75: 1.85, 76: 1.85, 77: 1.85,
    78: 1.85, 79: 1.04, 80: 1.06, 81: 1.06, 82: 1.06, 83: 1.06, 84: 1.06, 85: 1.06,
    86: 1.06, 87: 1.06, 88: 1.06, 89: 1.06, 90: 1.04, 91: 1.9, 92: 1.85, 93: 1.85,
    94: 1.85, 95: 1.85, 96: 1.85, 97: 1.85, 98: 1.85, 99: 1.1, 100: 1.1, 101: 1.85,
    102: 1.85, 103: 1.85, 104: 1.85, 105: 1.85, 106: 1.85, 107: 1.85, 108: 1.85,
    109: 1.85, 110: 1.85, 111: 1.85, 112: 1.85, 113: 1.85, 114: 1.85, 115: 1.85,
    116: 1.85, 117: 1.8, 118: 1.02
}


class AutoSlicer:
    """
    The AutoSlicer class is used to:
      1. Convert a folder of DICOM files into a single NIfTI image
      2. Perform medical image segmentation using TotalSegmentator
      3. Add a skin label to unlabeled regions within a specified intensity range
      4. Calculate mass, volume, inertia tensor, and center of mass from the final segmentation
    """

    def __init__(self, workspace: str):
        """
        Initialize the AutoSlicer class with default thresholds and workspace paths.

        Args:
            workspace (str): Name of the workspace directory
        """
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspace = os.path.join(self.current_dir, workspace)
        self._ensure_directory(self.workspace)

        # Threshold parameters (can be adjusted as needed)
        self.lower_ = -96.25
        self.upper_ = 153.46

        # File path configuration
        self.source_volume_path = os.path.join(self.workspace, "CT_Source_Volume.nii.gz")
        self.total_seg_result = os.path.join(self.workspace, "CT_TotalSegmentation.nii.gz")
        self.other_soft_tissue = os.path.join(self.workspace, "CT_SoftTissueLabel0.nii.gz")
        self.final_seg_result = os.path.join(self.workspace, "CT_SoftTissueLabel1.nii.gz")

    @staticmethod
    def _ensure_directory(path: str) -> None:
        """Create directory if it does not already exist."""
        os.makedirs(path, exist_ok=True)

    def set_density(self, label: int, value: float) -> None:
        """
        Set or update the density value for a specific label.

        Args:
            label (int): The label in the segmented result
            value (float): The corresponding density
        """
        if label in DENSITY_MAP:
            DENSITY_MAP[label] = value
        else:
            print(f"Label {label} not found in the density map. Skipping.")

    def set_threshold(self, lower_val: float, upper_val: float) -> None:
        """
        Set lower and upper intensity thresholds for future operations such as skin labeling.

        Args:
            lower_val (float): The lower threshold
            upper_val (float): The upper threshold
        """
        self.lower_ = lower_val
        self.upper_ = upper_val

    # ----------------- NIfTI Creation ----------------- #
    @staticmethod
    def _get_voxel_size(input_folder: str):
        """
        Retrieve the voxel spacing (e.g., pixel dimensions) from a DICOM folder.

        Args:
            input_folder (str): Path to the folder containing DICOM files

        Returns:
            tuple: (voxel_size, unit), where voxel_size is (x, y, z) in mm, and unit is "mm"
        """
        try:
            reader = sitk.ImageSeriesReader()
            dicom_series = reader.GetGDCMSeriesIDs(input_folder)
            if not dicom_series:
                raise ValueError("No DICOM series found in the input folder.")

            series_file_names = reader.GetGDCMSeriesFileNames(input_folder, dicom_series[0])
            reader.SetFileNames(series_file_names)
            image = reader.Execute()

            voxel_size = image.GetSpacing()
            print(f"Voxel size (x, y, z): {voxel_size}")
            unit = "mm"  # Default unit in medical imaging
            print(f"Assumed unit: {unit}")

            return voxel_size, unit
        except Exception as e:
            print(f"An error occurred while getting voxel size: {e}")
            return None, None

    def _dicom_to_nifti(self, input_folder: str, output_path: str) -> None:
        """
        Convert DICOM files from a given folder into a single NIfTI file and save it.

        Args:
            input_folder (str): Path to the folder containing DICOM files
            output_path (str): Path to the output NIfTI file
        """
        try:
            reader = sitk.ImageSeriesReader()
            # Retrieve and print voxel size (for informational purposes)
            self._get_voxel_size(input_folder)

            dicom_series = reader.GetGDCMSeriesIDs(input_folder)
            if not dicom_series:
                raise ValueError("No DICOM series found in the input folder.")

            print(f"Found {len(dicom_series)} DICOM series in the folder.")

            for series_id in dicom_series:
                series_file_names = reader.GetGDCMSeriesFileNames(input_folder, series_id)
                reader.SetFileNames(series_file_names)

                image = reader.Execute()
                sitk.WriteImage(image, output_path)
                print(f"Converted series {series_id} to {output_path}")

            print("All DICOM series have been converted successfully.")
        except Exception as e:
            print(f"An error occurred during DICOM to NIfTI conversion: {e}")

    def create_nifti(self, input_folder: str) -> None:
        """
        Public interface method: convert DICOM files from the input folder to a NIfTI file.

        Args:
            input_folder (str): Path to the folder containing DICOM files
        """
        self._dicom_to_nifti(input_folder, self.source_volume_path)

    # ----------------- Segmentation ----------------- #
    def _segment_image(self, input_image_path: str, output_path: str) -> None:
        """
        Perform segmentation using TotalSegmentator and save the result.

        Args:
            input_image_path (str): Path to the input NIfTI file
            output_path (str): Path to save the segmentation result
        """
        device = "gpu" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        try:
            input_img = nib.load(input_image_path)
            print("Starting segmentation with TotalSegmentator...")
            output_img = totalsegmentator(
                input=input_img,
                task="total",
                ml=True,
                device=device
            )
            nib.save(output_img, output_path)
            print(f"Segmentation completed. Results saved at: {output_path}")
        except Exception as e:
            print(f"An error occurred in segmentation: {e}")
            raise

    def _label_segmentation(self, seg_result_path: str, labeled_output_path: str) -> None:
        """
        Load the segmentation result and append label descriptions,
        making it compatible with 3D Slicer.

        Args:
            seg_result_path (str): Path to the segmented NIfTI file
            labeled_output_path (str): Path to save the labeled segmentation
        """
        try:
            print("Loading segmentation result with labels...")
            segmentation_nifti_img, label_map_dict = load_multilabel_nifti(seg_result_path)

            label_img = segmentation_nifti_img.get_fdata().astype(int)
            label_nifti = nib.Nifti1Image(label_img, segmentation_nifti_img.affine, segmentation_nifti_img.header)

            label_nifti.header["descrip"] = "Label Map for 3D Slicer"
            for label, description in label_map_dict.items():
                label_nifti.header.extensions.append(
                    nib.nifti1.Nifti1Extension(4, f"{label}: {description}".encode("utf-8"))
                )

            nib.save(label_nifti, labeled_output_path)
            print(f"Segmented labels saved at: {labeled_output_path}")
        except Exception as e:
            print(f"An error occurred while labeling segmentation: {e}")
            raise

    def create_segmentation(self) -> None:
        """
        Public interface method: segment the NIfTI image and save labeled results.
        """
        self._segment_image(self.source_volume_path, self.total_seg_result)
        self._label_segmentation(self.total_seg_result, self.other_soft_tissue)

    # ----------------- Soft Tissue and Skin Labeling ----------------- #
    @staticmethod
    def _load_nifti_file(file_path: str):
        """Load a NIfTI file and return (data, affine)."""
        nifti_img = nib.load(file_path)
        return nifti_img.get_fdata(), nifti_img.affine

    @staticmethod
    def _save_nifti_file(data: np.ndarray, affine: np.ndarray, file_path: str) -> None:
        """Save a NIfTI file to the specified path."""
        new_nifti_img = nib.Nifti1Image(data, affine)
        nib.save(new_nifti_img, file_path)

    def _add_skin_label(self, source_volume: np.ndarray, segmentation_result: np.ndarray) -> np.ndarray:
        """
        Mark unlabeled voxels whose intensity lies within [lower_, upper_] as label 100 (skin).

        Args:
            source_volume (np.ndarray): The original volume in which intensities will be checked
            segmentation_result (np.ndarray): The current segmentation array

        Returns:
            np.ndarray: An updated segmentation array with label 100 assigned to skin voxels
        """
        skin_candidate = (source_volume >= self.lower_) & (source_volume <= self.upper_)
        unlabeled_area = (segmentation_result == 0)
        skin_label_area = skin_candidate & unlabeled_area

        updated_seg = segmentation_result.copy()
        updated_seg[skin_label_area] = 118
        return updated_seg

    def create_soft_tissue_segmentation(self) -> None:
        """
        Public interface method: add a "skin" label to unlabeled soft tissue in the segmented result.
        """
        segmentation_result, seg_affine = self._load_nifti_file(self.other_soft_tissue)
        source_volume, _ = self._load_nifti_file(self.source_volume_path)

        updated_seg = self._add_skin_label(source_volume, segmentation_result)
        self._save_nifti_file(updated_seg, seg_affine, self.final_seg_result)
        print(f"Updated segmentation with skin label saved to: {self.final_seg_result}")

    # ----------------- Inertia Tensor + COM Calculation ----------------- #
    @staticmethod
    def _get_segmentation_labels(segmentation_file: str) -> list:
        """Retrieve unique label values from the segmentation result."""
        nifti_img = nib.load(segmentation_file)
        seg_data = nifti_img.get_fdata()
        unique_labels = np.unique(seg_data)
        return [int(x) for x in unique_labels.tolist()]

    def _calculate_inertia_parameters(self, segmentation_file: str) -> dict:
        """
        Calculate total mass, volume, inertia tensor, and global center of mass.

        Assumes voxel_size = (1,1,1) mm and uses DENSITY_MAP for densities.

        Args:
            segmentation_file (str): Path to the final segmented NIfTI file

        Returns:
            dict: Contains total volume (cm³), total mass (kg),
                  total inertia tensor (kg·mm²), and center of mass (mm).
        """
        voxel_size = (1, 1, 1)  # If you have actual spacing, set it here
        target_labels = self._get_segmentation_labels(segmentation_file)

        nifti_img = nib.load(segmentation_file)
        seg_data = nifti_img.get_fdata()

        # Convert 1 mm³ to 0.001 cm³ (1e-3)
        voxel_volume_cm3 = (voxel_size[0] * voxel_size[1] * voxel_size[2]) / 1000.0

        total_mass = 0.0
        total_volume = 0.0
        total_inertia_tensor = np.zeros((3, 3))

        # For computing global center of mass:
        acc_mass_times_centroid = np.zeros(3)  # sum of (mass * centroid)
        acc_mass = 0.0

        for label in target_labels:
            if label not in DENSITY_MAP:
                print(f"Warning: Label {label} not found in the density map. Skipping.")
                continue

            mask = (seg_data == label)
            num_voxels = mask.sum()
            if num_voxels == 0:
                continue

            density = DENSITY_MAP[label]
            volume = num_voxels * voxel_volume_cm3
            # Convert from g to kg by dividing by 1000 (assuming 1 cm³ of water ~ 1 g)
            mass = (volume * density) / 1000.0

            # Calculate centroid for this label
            coords = np.array(np.where(mask)).T
            coords_mm = coords * voxel_size  # converting voxel indices to mm
            centroid = coords_mm.mean(axis=0)

            # Accumulate for global center of mass
            acc_mass_times_centroid += mass * centroid
            acc_mass += mass

            # Calculate the inertia tensor for this region
            inertia_tensor = np.zeros((3, 3))
            for coord in coords_mm:
                relative_pos = coord - centroid
                x, y, z = relative_pos
                inertia_tensor += np.array([
                    [y**2 + z**2, -x*y,       -x*z],
                    [-x*y,        x**2 + z**2, -y*z],
                    [-x*z,        -y*z,       x**2 + y**2]
                ]) * mass / num_voxels

            total_volume += volume
            total_mass += mass
            total_inertia_tensor += inertia_tensor

        # Compute global center of mass
        if acc_mass > 0:
            global_center_of_mass = acc_mass_times_centroid / acc_mass  # in mm
        else:
            global_center_of_mass = np.zeros(3)

        # Prepare the result
        result = {
            "T1": {
                "name": "Volume",
                "value": total_volume,
                "unit": "cm³"
            },
            "T2": {
                "name": "Mass",
                "value": total_mass,
                "unit": "kg"
            },
            "T3": {
                "name": "Total Inertia Tensor",
                "value": total_inertia_tensor,
                "unit": "kg·mm²"
            },
            "T4": {
                "name": "Center of Mass",
                "value": global_center_of_mass.tolist(),  # Convert np.array to list for readability
                "unit": "mm"
            }
        }
        return result

    def calculate_inertia(self) -> dict:
        """
        Public interface method: calculate inertia, volume, mass, and center of mass
        using the final segmentation.
        """
        return self._calculate_inertia_parameters(self.final_seg_result)

    # ----------------- One-Click Automation ----------------- #
    def run_automation(self, input_folder: str) -> dict:
        """
        One-click process:
          1. DICOM -> NIfTI
          2. Segmentation
          3. Add skin label
          4. Inertia + COM calculation

        Args:
            input_folder (str): Path to the folder containing DICOM files

        Returns:
            dict: Contains the calculated volume, mass, inertia tensor, and center of mass
        """
        self.create_nifti(input_folder)
        self.create_segmentation()
        self.create_soft_tissue_segmentation()
        result = self.calculate_inertia()
        return result


if __name__ == "__main__":
    pass

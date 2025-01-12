# Automated carbide detection (carde)

Tool to detect carbides in scanning electron micrographs of steel.

During the production and heat treatment of steel, carbides with a size ranging between 10 nm up to a few µm precipitate in the steel matrix. While the carbides contribute to the steels yield strength, the largest carbides can be responsible for crack initiation leading to brittle fracture. Thus, a detailed quantitative description of carbides (e.g. number density, size distribution etc.) in a steel is of great interest.
On a polished sample, carbides can be observed using a scanning electron microscope (SEM). In the present case, SEM micrographs of a reactor pressure vessel steel have been recorded, in which carbides can be recognized.

## Installation

Create and activate a virtual environment with venv

```
python -m venv .carde-venv
source .carde-venv/bin/activate
```

Install carde and all required dependencies
```
pip install carde
```

## Usage

Please refer to the example notebooks

* [process a folder of images](https://chekhonin-automatic-carbide-detection-haicu-vouc-1d7a37eb51de28.pages.hzdr.de/notebooks/process_image_folder.html)
* [how the segmentation works](https://chekhonin-automatic-carbide-detection-haicu-vouc-1d7a37eb51de28.pages.hzdr.de/notebooks/classic_ml_segmentation.html)


## Documentation

https://chekhonin-automatic-carbide-detection-haicu-vouc-1d7a37eb51de28.pages.hzdr.de/

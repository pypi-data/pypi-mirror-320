
# Automated carbide detection

```
Progress |████████████████████------------------------------| 41.03% Complete

Total time available: 2.0 weeks

Total time spent: 0.82 weeks


```

## Project Info

* Project title: Automatic carbide detection
Name: Paul Chekhonin
* Submitter name: [Paul Chekhonin](mailto:p.chekhonin@hzdr.de)
* Submitting Helmholtz center: __HZDR__
* Submitting department/lab : _FWOM_
* Research field: __Matter__
* Start date: Aug 2024
* Expected duration: 2 weeks FTE
* Type of voucher: __Exploration__
* Data type: _images, labels_

## Documentation

https://chekhonin-automatic-carbide-detection-haicu-vouc-1d7a37eb51de28.pages.hzdr.de/

## Internal info

* Consultant(s) name and Helmholtz Center: Till Korten, HZDR
* Project acronym: `chekhonin-automatic-carbide-detection`
* Voucher system entry: _https://zammad-voucher.helmholtz.ai/#ticket/zoom/1027_

# Abstract / Summary

In order to study reactor pressure vessel steels (but in principle any other metallic structural components) with respect to mechanical properties, such as yield strength or fracture toughness, a detailed knowledge of the microstructure is essential.
During the steels production and heat treatment, carbides with a size ranging between 10 nm up to a few µm precipitate in the steel matrix. While the carbides contribute to the steels yield strength, the largest carbides can be responsible for crack initiation leading to brittle fracture. Thus, a detailed quantitative description of carbides (e.g. number density, size distribution etc.) in a steel is of great interest.
On a polished sample, carbides can be observed using a scanning electron microscope (SEM). In the present case, SEM micrographs of a reactor pressure vessel steel have been recorded, in which carbides can be recognized. However, the gray level in the background (grains of the steel), as well as the edge regions of many carbides overlap. Because of this, a simple approach via grey value threshold is insufficient in order to correctly mark the carbides and to distinguish them from the steel matrix. To facilitate a clean separation of carbides and steel matrix, in addition to a grey value threshold split, the SEM micrographs have been manually adjusted, which is a rather time consuming and presumably inefficient approach.
Therefore, in order to save time in the future for similar analyses, expertise of the Helmholtz AI team would be greatly appreciated.

# Goals

Automated segmentation pipeline that labels carbide inclusions in SEM images of reactor steel

# Data

SEM images and labels
 labels

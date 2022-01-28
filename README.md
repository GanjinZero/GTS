# Introduction
Code for [Unsupervised multi-granular Chinese word segmentation and term discovery via graph partition](https://www.researchgate.net/publication/343840671_Unsupervised_Multi-granular_Chinese_Word_Segmentation_and_Term_Discovery_via_Graph_Partition).

## Usage
N-gram and trained BERT classifier cannot be public since privacy policy. 

### Use in command lines
```python
python -m graces -s 饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。
python -m graces -f ./input.txt -o ./output.txt
```

### Import from python
```python
import graces
graces.cut("饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。") # Segment a single sentence
graces.cut_k("饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。", k=8) # Segment a single sentence with fixed word count k.
graces.cut_file("./input.txt", "./output.txt") # Segment a file
```

## Data
We ask 10 MD students to construct coarse and fine level word segmentation on EHRs for validation. We do not use data for training!
**dev.txt**: Unlabeled EHRs from part of CCKS2019.
**dev_label_coarse.txt**: Coarse-level word segmentation labels.
**dev_label_fine.txt**: Fine-level word segmentation labels.

## Citation
If you find our codes or data use
```bibtex
@article{YUAN2020103542,
title = "Unsupervised multi-granular Chinese word segmentation and term discovery via graph partition",
journal = "Journal of Biomedical Informatics",
volume = "110",
pages = "103542",
year = "2020",
issn = "1532-0464",
doi = "https://doi.org/10.1016/j.jbi.2020.103542",
url = "http://www.sciencedirect.com/science/article/pii/S1532046420301702",
author = "Zheng Yuan and Yuanhao Liu and Qiuyang Yin and Boyao Li and Xiaobin Feng and Guoming Zhang and Sheng Yu",
}
```

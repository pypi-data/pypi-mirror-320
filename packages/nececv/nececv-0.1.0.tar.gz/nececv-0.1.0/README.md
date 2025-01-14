# nececv

`nececv` is a Python package for advanced edge detection and object recognition using VGG16 and OpenCV.

## Features
- Sobel and Canny edge detection
- Enhanced edge detection using epsilon learning
- Object recognition with VGG16

## Installation
```bash
pip install nececv
```

## USAGE

import nececv

nececvo = nececv()
image_path = <path\\to\\your\\image>
predictions = nececvo.detect_object_probability(image_path)

# Display results
nececvo.display_results(
    image_path, 
    predictions=predictions, 
    edge_image="Sobel", 
    epsilon=0.2, 
    iterations=5
    )
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

    # Detailed Explanation of `nececv` Class

The `nececv` class is designed to integrate advanced image processing techniques with deep learning-based object detection, primarily using the VGG16 model and OpenCV’s edge detection tools. The class provides a powerful set of functionalities for processing images, detecting objects, and performing edge detection tasks such as Sobel and Canny edge detection. It also enhances the edge detection results using an epsilon learning technique.

## 1. **VGG16 Model for Object Detection**

The core functionality of the `nececv` class is object detection using a **pre-trained VGG16 model**. VGG16 is a deep convolutional neural network trained on ImageNet, which is widely used for image classification tasks. The model is capable of classifying images into 1,000 different categories based on the features it has learned from the dataset.

- **Process**: The image is resized to 224x224 pixels (the required input size for VGG16), converted into a format that the model can process, and then passed through the VGG16 model.
- **Output**: The model outputs the predicted object label and its associated probability. The top three predictions are returned, and the predicted class with the highest probability is typically selected as the most likely object in the image.

## 2. **Image Preprocessing**

For the model to make accurate predictions, the image must be preprocessed. This involves resizing the image, normalizing pixel values, and converting the image into a format suitable for the VGG16 model.

- **Resizing**: The image is resized to 224x224 pixels to match the input size required by the VGG16 model.
- **Normalization**: Pixel values are scaled to be between -1 and 1 using a standard preprocessing technique. This helps improve the model's performance by normalizing the input data.
- **Expansion**: The image is expanded to create an additional batch dimension, as the model expects a batch of images as input.

## 3. **Edge Detection Techniques**

Edge detection is a crucial step in image processing, as it helps identify the boundaries of objects within an image. In this class, two methods of edge detection are used: **Sobel** and **Canny**.

### Sobel Edge Detection:
The Sobel operator is a discrete differentiation operator that computes the gradient of the image intensity at each pixel, allowing for the detection of edges. The class applies a custom **Sobel filter** to detect edges by emphasizing regions of high intensity variation.

- **Edge Density**: After applying the Sobel filter, the number of non-zero pixels (edges) is counted. This count is normalized to calculate the **edge density**, which is a measure of how much of the image is considered to be an edge.

### Canny Edge Detection:
Canny edge detection is another popular edge detection technique that involves multiple steps:
1. **Smoothing**: The image is smoothed using a Gaussian filter to reduce noise.
2. **Gradient Calculation**: The gradient of the image is computed to identify areas of high intensity change.
3. **Thresholding**: Canny edge detection uses two threshold values to classify pixels as edges or non-edges.

The class enhances the Canny edge detection by using an **epsilon learning technique**, which iteratively adjusts the threshold values based on the calculated edge density. This method adapts the thresholds dynamically to refine the edge detection results.

## 4. **Epsilon Learning for Enhanced Edge Detection**

Epsilon learning is used to enhance edge detection by adjusting the edge detection thresholds in an iterative manner based on certain characteristics of the image. Specifically, the threshold values for the Canny edge detection are adjusted in each iteration by a small increment (epsilon), which depends on the average intensity of the edges and the edge density in the image.

- **Process**: The class starts by performing initial edge detection with default thresholds and then adjusts these thresholds after each iteration based on the mean intensity of the detected edges and the edge density. This dynamic adjustment helps to highlight more relevant edges and refine the edge detection process over multiple iterations.

## 5. **Object Detection and Edge Detection Integration**

The `nececv` class integrates the results of object detection with edge detection. Based on the top predicted label from the VGG16 model, the class generates edge images corresponding to the detected object. For example, if the predicted object is a "dog," the class could focus on generating edge images of that object with enhanced edge detection.

- **Edge Image Generation**: The class uses the top predicted object label to apply an edge detection technique (Sobel or Canny) and create a corresponding edge image. This process helps to visualize the object’s boundaries in a more defined manner.

## 6. **Visualization of Results**

The class includes a visualization function that allows the user to view the results of both object detection and edge detection. The user can choose to display:
1. The original image with the top prediction from the VGG16 model.
2. The edge detection result, either from the Sobel or Canny method.
3. Both the image and the edge detection result side by side.

The visualization makes it easier to understand how edge detection helps highlight the features of the detected object and provides an intuitive way to analyze the results.

### Customizable Output:
- **Edge Detection Type**: The user can select the edge detection technique (Sobel or Canny) and visualize the results.
- **Top Prediction**: The predicted object from the VGG16 model is shown with its associated probability.

## 7. **Workflow and Use Cases**

The `nececv` class is designed for tasks where both object recognition and edge detection are important. Common use cases include:
- **Image analysis**: Detecting and highlighting features of objects within images, which can be useful in applications like automated inspection or object tracking.
- **Enhanced visualizations**: Providing clearer visualizations of object boundaries through edge detection, helping in tasks like image segmentation.
- **Custom image processing workflows**: Allowing users to fine-tune edge detection methods based on the specific characteristics of the image, using epsilon learning for better results.

## Conclusion

The `nececv` class combines powerful deep learning and advanced image processing techniques to perform object detection and edge detection tasks. It leverages the VGG16 model for classification and uses Sobel and Canny edge detection to highlight important features in images. The inclusion of epsilon learning allows for adaptive thresholding in edge detection, making the process more dynamic and suitable for various types of images. The class’s integration of these techniques, along with its ability to visualize results, makes it a versatile tool for image processing tasks.
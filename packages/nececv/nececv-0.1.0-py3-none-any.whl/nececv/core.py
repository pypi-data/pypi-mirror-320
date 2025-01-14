import numpy as np
from PIL import Image
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
import cv2  # OpenCV for advanced edge detection
import matplotlib.pyplot as plt

class nececv:
    def __init__(self):
        # Load the VGG16 model pre-trained on ImageNet
        self.model = VGG16(weights="imagenet")

    # Function to load and preprocess the user image
    def load_and_preprocess_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((224, 224))  # Resize image for model
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array

    # Function to calculate Sobel edge density
    def calculate_sobel_density(self, image_path):
        # Read the image in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Define the custom kernel for edge detection
        custom_kernel = np.array([[-1, -1, -1],
                                  [-1,  8, -1],
                                  [-1, -1, -1]])
    
    # Apply the custom kernel to the image
        sobel_edges = cv2.filter2D(img, cv2.CV_64F, custom_kernel)
    
    # Normalize the Sobel edge image
        sobel_edges = cv2.normalize(sobel_edges, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Calculate edge density (fraction of non-zero pixels)
        edge_density = np.count_nonzero(sobel_edges) / sobel_edges.size
    
        return sobel_edges, edge_density

    # Function to apply epsilon learning for enhanced edge detection
    def apply_epsilon_learning(self, image_path, threshold1, threshold2, epsilon, iterations, object_name=None):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        blurred_img = cv2.GaussianBlur(img, (5, 5), 0)

        # Calculate Sobel edge density
        _, edge_density = self.calculate_sobel_density(image_path)

        # Apply epsilon learning
        for _ in range(iterations):
            edges = cv2.Canny(blurred_img, threshold1=10, threshold2=120)
            mean_intensity = np.mean(edges)
            threshold1 += epsilon * mean_intensity * edge_density
            threshold2 += epsilon * mean_intensity * edge_density

        return edges

    # Function to detect the probability and top labels in the image using VGG16
    def detect_object_probability(self, image_path):
        processed_image = self.load_and_preprocess_image(image_path)
        predictions = self.model.predict(processed_image)
        decoded_predictions = decode_predictions(predictions, top=3)[0]
        return decoded_predictions

    # Generate edge detection image based on top prediction and epsilon learning
    def generate_edge_image(self, image_path, predictions, epsilon, iterations):
        top_label = predictions[0][1]
        canny_edges = self.apply_epsilon_learning(image_path, 50, 150, epsilon, iterations, object_name=top_label)
        return canny_edges

    # Display results
    def display_results(self, image_path, predictions=None,edge_image=None, epsilon=0.1, iterations=10):
        original_img = Image.open(image_path)
        original_img = np.array(original_img)

        # Determine the number of subplots required
        n_plots = 0
        if edge_image is not None:
            n_plots += 1
        if predictions is not None:
            n_plots += 1

    # Create subplots dynamically
        fig, ax = plt.subplots(1, n_plots, figsize=(6 * n_plots, 6))
        if n_plots == 1:
            ax = [ax]  # Ensure `ax` is always a list for consistency

        plot_idx = 0  # To keep track of the subplot index

        if edge_image is not None:
        # Display edge image
            if edge_image == "Canny":
                edge_image_output = nececv.generate_edge_image(image_path, predictions, epsilon, iterations)
                ax[plot_idx].imshow(edge_image_output, cmap="gray")
                ax[plot_idx].set_title(f"Canny Edge Detection\nEpsilon: {epsilon}, Iterations: {iterations}")
                ax[plot_idx].axis("off")

            elif edge_image == "Sobel":
                sobel_edges, _ = self.calculate_sobel_density(image_path)  # Assuming this method exists
                ax[plot_idx].imshow(sobel_edges, cmap="gray")
                ax[plot_idx].set_title("Sobel Edge Detection")
                ax[plot_idx].axis("off")

            plot_idx += 1

        if predictions is not None:
        # Display original image with top prediction
            top_label = predictions[0][1]
            top_score = predictions[0][2]
            ax[plot_idx].imshow(original_img)
            ax[plot_idx].set_title(f"Predicted: {top_label} with Probability: {top_score:.2f}")
            ax[plot_idx].axis("off")

            plt.tight_layout()
            plt.show()

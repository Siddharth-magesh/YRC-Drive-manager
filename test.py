import cv2

def count_faces_advanced(image_path, cascade_path='haarcascade_frontalface_default.xml'):
    """
    Detects the number of faces in an image using Haar cascades with optimized parameters.

    Args:
        image_path (str): Path to the image file.
        cascade_path (str): Path to the Haar cascade XML file. Defaults to frontal face cascade.

    Returns:
        int: Number of faces detected.
    """
    # Load the Haar cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return 0

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces with optimized parameters
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.05,   # Smaller step for better accuracy
        minNeighbors=8,     # Higher value to reduce false positives
        minSize=(20, 20),   # Minimum face size (in pixels)
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw rectangles around detected faces (optional)
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display the image with detected faces (optional)
    cv2.imshow('Faces Detected', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return len(faces)

# Example usage
image_path = r'D:\YRC-Drive-manager\DSC_0655.JPG'  # Replace with the path to your image
num_faces = count_faces_advanced(image_path)
print(f"Number of faces detected: {num_faces}")

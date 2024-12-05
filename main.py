import streamlit as st
import cv2
import numpy as np
from PIL import Image

def rotate_image(image, angle):
    """Rotate image by specified angle."""
    (h, w) = image.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))

def main():
    st.title("Mobile Camera Frame Capture")
    
    st.markdown("""
    ### Instructions
    - This app works best on mobile Chrome browsers
    - Ensure you grant camera permissions
    - Click 'Start Camera' to begin
    """)
    
    # Camera capture section
    camera_on = st.checkbox("Start Camera")
    
    if camera_on:
        # Use Streamlit's camera_input for direct mobile camera access
        img_file_buffer = st.camera_input("Take a picture")
        
        if img_file_buffer is not None:
            # Convert the file to an opencv image
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Rotation controls
            rotation_angle = st.slider("Rotate Image", min_value=0, max_value=360, value=0, step=90)
            
            # Rotate image
            rotated_img = rotate_image(cv2_img, rotation_angle)
            
            # Display captured and rotated image
            st.subheader("Captured Image")
            st.image(rotated_img, channels="BGR")
            
            # Option to save the image
            if st.button("Save Image"):
                image_pil = Image.fromarray(cv2.cvtColor(rotated_img, cv2.COLOR_BGR2RGB))
                image_pil.save(f"captured_image_{rotation_angle}_degrees.jpg")
                st.success("Image saved successfully!")
    
if __name__ == "__main__":
    main()
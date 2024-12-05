import streamlit as st
import google.generativeai as genai
import PIL.Image

def process_image_with_gemini(image):
    """
    Process the captured image using Gemini API
    """
    # Replace 'YOUR_GEMINI_API_KEY' with your actual Gemini API key
    genai.configure(api_key=st.secrets["API_KEY"])

    # Initialize the generative model
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        # Convert Streamlit UploadedFile to PIL Image
        pil_image = PIL.Image.open(image)

        # Generate description of the image
        response = model.generate_content([
            "OCR the equation or the maths problem and solve it and give step-by-step solution", 
            pil_image
        ])

        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    st.set_page_config(page_title="Camera Capture", layout="wide")
    st.title("Camera Capture with Gemini Image Analysis")

    # Wider camera input with custom styling
    st.markdown("""
    <style>
    .stCameraInput > div > div > video, 
    .stCameraInput > div > div > img {
        width: 100%;
        max-width: 800px;
        height: auto;
        margin: 0 auto;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

    # Camera input
    picture = st.camera_input("Take a picture", key="camera")
    
    if picture:
        # Display captured image
        st.image(picture, caption="Captured Image")
        
        # Option to process image with Gemini
        if st.button("Analyze Image with Gemini"):
            with st.spinner('Analyzing image...'):
                description = process_image_with_gemini(picture)
                st.write("Gemini's Image Description:")
                st.info(description)
        
        # Download button
        st.download_button(
            label="Download Image", 
            data=picture, 
            file_name="captured_image.jpg",
            mime="image/jpeg"
        )

if __name__ == "__main__":
    main()
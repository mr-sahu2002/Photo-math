import streamlit as st
import google.generativeai as genai
import PIL.Image

def process_image_with_gemini(image, chat_history=None, doubt=None):
    """
    Process the image using Gemini API with optional chat context
    """
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        # Convert Streamlit UploadedFile to PIL Image
        pil_image = PIL.Image.open(image)

        # Prepare the prompt based on context
        if not chat_history and not doubt:
            prompt = [
                "OCR the equation or maths problem. Solve it step-by-step with numbered steps. Use clear notation with ^(superscript) for exponents and _(subscript) for indices.", 
                pil_image
            ]
        else:
            prompt = [
                f"Previous solution: {chat_history}\n",
                f"User's doubt: {doubt}\n" if doubt else "",
                "Provide a detailed clarification or additional explanation.",
                pil_image
            ]

        # Generate response
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    st.set_page_config(page_title="Math Problem Solver", layout="wide")
    st.title("📝 Camera-Based Math Problem Solver")

    # Custom styling for camera input
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

    # Initialize session state
    if 'solution' not in st.session_state:
        st.session_state.solution = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Camera input
    picture = st.camera_input("Capture a Math Problem")
    
    if picture:
        # Display captured image
        st.image(picture, caption="Captured Math Problem")
        
        # Solve problem
        if st.button("Solve with Gemini"):
            with st.spinner('Solving math problem...'):
                solution = process_image_with_gemini(picture)
                st.session_state.solution = solution
                st.markdown("### Solution:")
                st.info(solution)
        
        # Download button
        st.download_button(
            label="Download Image", 
            data=picture, 
            file_name="math_problem.jpg",
            mime="image/jpeg"
        )

        # Doubt clarification section
        if st.session_state.solution:
            st.markdown("### Ask About the Solution")
            user_doubt = st.text_input("Enter your doubt", key="user_doubt")
            
            if st.button("Get Clarification"):
                with st.spinner('Generating clarification...'):
                    clarification = process_image_with_gemini(
                        picture, 
                        chat_history=st.session_state.solution, 
                        doubt=user_doubt
                    )
                    
                    st.markdown("#### Clarification:")
                    st.info(clarification)
                    
                    # Update chat history
                    st.session_state.chat_history.append(f"Doubt: {user_doubt}")
                    st.session_state.chat_history.append(f"Clarification: {clarification}")

            # Show chat history
            if st.session_state.chat_history:
                st.markdown("### Chat History")
                for entry in st.session_state.chat_history:
                    st.markdown(entry)

if __name__ == "__main__":
    main()
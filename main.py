import streamlit as st
import google.generativeai as genai
import PIL.Image
import re

def format_math_solution(solution):
    """
    Enhance mathematical solution formatting with proper subscripts and superscripts
    """
    # Handle superscripts
    solution = re.sub(r'\^(\d+)', lambda m: f'<sup>{m.group(1)}</sup>', solution)
    
    # Handle subscripts
    solution = re.sub(r'_(\d+)', lambda m: f'<sub>{m.group(1)}</sub>', solution)
    
    # Improve equation clarity
    solution = solution.replace('\\', '<br>')
    
    return solution

def process_image_with_gemini(image, chat_history=None, doubt=None):
    """
    Process the image using Gemini API with optional chat context
    """
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        # Convert Streamlit UploadedFile to PIL Image
        pil_image = PIL.Image.open(image)

        # Prepare the initial prompt
        if not chat_history:
            prompt_parts = [
                "OCR the equation or the maths problem and solve it step-by-step with step numbering like step 1, step 2, .... . Use clear notation with ^(superscript) for exponents and _(subscript) for indices.", 
                pil_image
            ]
        else:
            # If there's a chat history or specific doubt, modify the prompt
            prompt_parts = [
                f"Previous solution: {chat_history}\n\n",
                "Additional context/doubt to address:" if doubt else "",
                doubt if doubt else "",
                pil_image
            ]

        # Generate response
        response = model.generate_content(prompt_parts)

        # Format the solution
        formatted_solution = format_math_solution(response.text)
        
        return formatted_solution
    except Exception as e:
        return f"Error processing image: {str(e)}"

def main():
    st.set_page_config(page_title="Math Problem Solver", layout="wide")
    st.title("Camera-Based Math Problem Solver")

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

    # Initialize session state for solution and chat history
    if 'solution' not in st.session_state:
        st.session_state.solution = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Camera input
    picture = st.camera_input("Capture a Math Problem", key="camera")
    
    if picture:
        # Display captured image
        st.image(picture, caption="Captured Math Problem")
        
        # Option to process image with Gemini
        if st.button("Solve with Gemini"):
            with st.spinner('Solving math problem...'):
                solution = process_image_with_gemini(picture)
                st.session_state.solution = solution
                st.markdown("### Solution:", unsafe_allow_html=True)
                st.markdown(solution, unsafe_allow_html=True)
        
        # Download button
        st.download_button(
            label="Download Image", 
            data=picture, 
            file_name="math_problem.jpg",
            mime="image/jpeg"
        )

        # Continuous Chat Section
        if st.session_state.solution:
            st.markdown("### Ask a Doubt about the Solution")
            user_doubt = st.text_input("Enter your doubt", key="user_doubt")
            
            if st.button("Get Clarification"):
                with st.spinner('Generating clarification...'):
                    # Append current doubt to chat history
                    st.session_state.chat_history.append(f"User Doubt: {user_doubt}")
                    
                    # Get clarification from Gemini
                    clarification = process_image_with_gemini(
                        picture, 
                        chat_history=st.session_state.solution, 
                        doubt=user_doubt
                    )
                    
                    # Display clarification
                    st.markdown("#### Clarification:", unsafe_allow_html=True)
                    st.markdown(clarification, unsafe_allow_html=True)
                    
                    # Update chat history
                    st.session_state.chat_history.append(f"Clarification: {clarification}")

            # Optional: Show chat history
            if st.session_state.chat_history:
                st.markdown("### Chat History")
                for entry in st.session_state.chat_history:
                    st.markdown(entry)

if __name__ == "__main__":
    main()
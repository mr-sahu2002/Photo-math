import streamlit as st
import google.generativeai as genai
import PIL.Image
import os



def process_image_with_gemini(image, chat_history=None, doubt=None):
    """
    Process the image using Gemini API with optional chat context
    Ensures mathematically formatted output
    """
    #if you are running the code locally then comment out the below two line of code and comment the third line
    #gemini_api = os.environ.get('GEMINI_API')
    # genai.configure(api_key=gemini_api)
    genai.configure(api_key=st.secrets["API_KEY"])
    
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        # Convert Streamlit UploadedFile to PIL Image
        pil_image = PIL.Image.open(image)

        # Detailed prompt for mathematical formatting
        if not chat_history and not doubt:
            prompt = [
                """
                OCR the equation or maths problem and make sure soulution should follow this guildlines:
                1. Use LaTeX-style notation for mathematical expressions
                2. Use ^ for superscripts (e.g., x^2)
                3. Use _ for subscripts (e.g., x_1)
                4. Write step-by-step solution with clear, numbered steps
                5. Include intermediate calculations
                6. Format equations and expressions cleanly
                7. If the problem involves complex notation, use standard mathematical typesetting
                8. Clearly show final answer with appropriate units or simplification
                
                Problem to solve:
                """,
                pil_image
            ]
        else:
            prompt = [
                f"Previous solution: {chat_history}\n",
                f"User's doubt: {doubt}\n" if doubt else "",
                """
                Provide a detailed clarification with:
                - Clear mathematical formatting
                - LaTeX-style notation
                - Use ^ for superscripts
                - Use _ for subscripts
                - Detailed explanation addressing the specific doubt
                """,
                pil_image
            ]

        # Generate response
        response = model.generate_content(prompt)
        
        # Post-process the response to ensure clean formatting
        formatted_solution = format_mathematical_solution(response.text)
        return formatted_solution
    
    except Exception as e:
        return f"Error processing image: {str(e)}"

def format_mathematical_solution(solution):
    """
    Post-process solution to ensure consistent mathematical formatting
    """
    # Replace common formatting issues
    formatting_replacements = [
        (r'\*\*', '^'),  # Convert ** to ^ for exponents
        (r'(\d+)_(\w+)', r'\1_{\2}'),  # Ensure proper subscript formatting
        (r'(\w+)_(\d+)', r'\1_{}\2'),  # Standardize subscript notation
    ]
    
    for pattern, replacement in formatting_replacements:
        solution = solution.replace(pattern, replacement)
    
    return solution

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
                st.markdown(solution)  # Use markdown for better rendering
        
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
                    st.markdown(clarification)  # Use markdown for better rendering
                    
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
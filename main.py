import streamlit as st

def main():
    st.title("Camera Access")

    # Custom JavaScript for camera permission
    camera_script = """
    <script>
    const getCameraPermission = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            window.cameraPermission = true;
            window.parent.postMessage('cameraGranted', '*');
        } catch (err) {
            window.cameraPermission = false;
            window.parent.postMessage('cameraDenied', '*');
        }
    };

    // Auto-trigger permission request
    getCameraPermission();
    </script>
    """
    
    # Inject JavaScript
    st.markdown(camera_script, unsafe_allow_html=True)

    # Add event listener for permission messages
    st.markdown("""
    <script>
    window.addEventListener('message', (event) => {
        if (event.data === 'cameraGranted') {
            // Camera access granted
            window.streamlit.setComponentValue(true);
        } else if (event.data === 'cameraDenied') {
            // Camera access denied
            window.streamlit.setComponentValue(false);
        }
    }, false);
    </script>
    """, unsafe_allow_html=True)

    # Check permission status
    permission = st.empty()
    
    # Camera input with conditional rendering
    picture = st.camera_input("Take a picture")
    
    if picture:
        st.image(picture)
        st.download_button(
            label="Download Image", 
            data=picture, 
            file_name="captured_image.jpg",
            mime="image/jpeg"
        )

if __name__ == "__main__":
    main()
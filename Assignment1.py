import streamlit as st

st.title("ECHO CHAMBER 9000")
st.write("Enter your name and a message then click Transmit to send it")

user_name = st.text_input("Name")
user_message = st.text_input("Message")

if st.button("Transmit"):

    if not user_name.strip():
        st.error("Please provide your name.")

    elif not user_message.strip():
        st.warning("Please type a message to transmit.")

    else:
        st.success(
            f"Transmission successful! Greetings, {user_name}. "
            f"We received your message: {user_message}"
        )

        total_characters = len(user_message)
        token_count = total_characters / 4

        st.info(
            f"System Check: Your message will consume approximately "
            f"{token_count:.2f} tokens from our context window."
        )
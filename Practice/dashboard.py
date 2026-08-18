import streamlit as st
st.title("analysis")
with st.sidebar:
    st.header("controls")
    player=st.selectbox("Select Player", ["Player 1", "Player 2", "Player 3"])  
    phase=st.slider("over",1,5,10)
st.subheader(f"Live stats : {player}")

col1,col2=st.columns(2)
with col1:
    st.write("TOTAL RUNS")
    st.write(15*phase)
with col2:
    st.write("Strike Rate")
    st.write(148.5)
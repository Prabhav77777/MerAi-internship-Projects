import streamlit as st
import pandas as pd
import time
st.header("forms")

if st.button("submit"):
    with st.spinner("working..."):
        time.sleep(3)
    st.toast("complete")
    st.write("done")

with st.form(key="details"):
    st.write("enter your details")
    name = st.text_input("Name")
    age = st.slider("Age",1,100,10)
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("form submitted successfully")
data=pd.DataFrame(
    {
        "task":["read","code","play"],
        "status":["done","working","not started"],
        "hours":[1,2,3]
    }
)
edited_df=st.data_editor(data,num_rows="dynamic")
if st.button("save"):
    st.success("saved")
    st.dataframe(edited_df)
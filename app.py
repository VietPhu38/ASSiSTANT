import streamlit as st

st.title("Xin chào từ Streamlit 👋")
st.write("Đây là một ứng dụng web đơn giản dùng Streamlit.")

ten = st.text_input("Nhập tên của bạn:")
if ten:
    st.success(f"Chào bạn, {ten}!")

so = st.slider("Chọn một số", 0, 100, 50)
st.write(f"Bạn đã chọn số: {so}")
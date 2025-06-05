import streamlit as st
from openai import OpenAI
from base64 import b64encode

# Ẩn thanh công cụ và nút "Manage app"
st.markdown("""
<style>
[data-testid="stToolbar"], [data-testid="manage-app-button"],
[data-testid="stAppViewBlockContainer"] > div > div > div > div > div {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Hàm tiện ích
def rfile(name): return open(name, "r", encoding="utf-8").read()
def img_to_base64(path): return b64encode(open(path, "rb").read()).decode()

# Ảnh avatar
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# Logo (nếu có)
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image("logo.png", use_container_width=True)
except: pass

# Tiêu đề
st.markdown(f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{rfile("00.xinchao.txt")}</h1>""", unsafe_allow_html=True)

# Nhập tên người dùng
user_id = st.text_input("🧑 Nhập tên của bạn để bắt đầu:", key="user_name")
if not user_id:
    st.warning("Vui lòng nhập tên để bắt đầu trò chuyện.")
    st.stop()

# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Tin nhắn khởi tạo
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# Tạo dict lưu lịch sử theo từng user
if "user_histories" not in st.session_state:
    st.session_state.user_histories = {}

if user_id not in st.session_state.user_histories:
    st.session_state.user_histories[user_id] = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

messages = st.session_state.user_histories[user_id]

# Nút bắt đầu lại cuộc trò chuyện
if st.button("🔁 New chat"):
    st.session_state.user_histories[user_id] = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    st.rerun()

# Giao diện CSS
st.markdown("""
<style>
.message {
    padding: 12px; border-radius: 12px; max-width: 75%; display: flex;
    align-items: flex-start; gap: 12px; margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.assistant { background-color: #f0f7ff; }
.user { background-color: #e6ffe6; text-align: right; margin-left: auto; flex-direction: row-reverse; }
.icon { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #ddd; }
.text { flex: 1; font-size: 16px; line-height: 1.4; }
.typing { font-style: italic; color: #888; padding: 5px 10px; display: flex; align-items: center; }
.typing::after { content: "..."; animation: blink 1s infinite; }
@keyframes blink { 0%{opacity:1;} 50%{opacity:0.5;} 100%{opacity:1;} }
[data-testid="stChatInput"] {
    border: 2px solid #ddd; border-radius: 8px; padding: 8px; background-color: #fafafa;
}
div.stButton > button {
    background-color: #4CAF50; color: white; border-radius: 2px solid #FFFFFF;
    padding: 6px 6px; font-size: 14px; border: none; margin: 10px 0;
}
div.stButton > button:hover { background-color: #45a049; }
</style>
""", unsafe_allow_html=True)

# Hiển thị lịch sử
for message in messages:
    if message["role"] == "assistant":
        st.markdown(f'''
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'''
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# Gửi tin nhắn mới
if prompt := st.chat_input("Nhập câu hỏi..."):
    messages.append({"role": "user", "content": prompt})
    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)

    # Trạng thái typing
    typing_placeholder = st.empty()
    typing_placeholder.markdown('<div class="typing">Đang trả lời...</div>', unsafe_allow_html=True)

    # Gọi GPT
    model = rfile("module_chatgpt.txt").strip()
    response = ""
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    # Xóa typing
    typing_placeholder.empty()

    # Hiển thị phản hồi
    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)

    messages.append({"role": "assistant", "content": response})
    st.session_state.user_histories[user_id] = messages

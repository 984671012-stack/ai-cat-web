import streamlit as st
from openai import OpenAI

# 1. 页面设置
st.set_page_config(page_title="AI 鹏鹏助手", page_icon="👦", layout="wide")
st.title("👦 你的 AI 好友：鹏鹏")

# ---【修复重点】安全初始化变量---
# 先把 api_key 设为空，防止后面报 NameError
api_key = None 
# ---------------------------

# 2. 侧边栏配置区 (Sidebar)
with st.sidebar:
    st.header("⚙️ 配置面板")
    
    # 尝试从 Secrets 获取 Key
    if "SILICON_KEY" in st.secrets:
        api_key = st.secrets["SILICON_KEY"]
    else:
        # 如果没有 Secrets，提供输入框
        api_key = st.text_input("请输入硅基流动 API Key", type="password")
    
    # 选择人设
    selected_role = st.selectbox(
        "选择 AI 的角色",
        ["鹏鹏", "猫娘女仆", "Python 编程专家", "雅思口语老师", "暴躁的厨师长"],
        index=0
    )
    
    # 调节创造力
    temperature = st.slider("创造力 (Temperature)", 0.0, 1.5, 0.7)
    
    # 清空对话按钮
    if st.button("🗑️ 清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

# 定义角色提示词字典
role_prompts = {
    "鹏鹏": "你叫鹏鹏，是用户的好朋友。你的说话语气要自然、随和，就像朋友之间聊天一样。不要太客气，也不要太严肃。如果不知道的问题就直说。可以用一些日常口语。",
    "猫娘女仆": "你是一只可爱的猫娘。回答前说'主人请稍等，猫娘正在查询数据库... \n'。句尾带'喵~'。",
    "Python 编程专家": "你是一位资深的 Python 架构师。只回答编程相关问题，提供代码时必须写注释，拒绝回答闲聊。",
    "雅思口语老师": "You are an IELTS examiner. Please correct my grammar mistakes and chat with me in English ONLY.",
    "暴躁的厨师长": "你就是那个地狱厨房的戈登·拉姆齐。说话要极其刻薄、爱骂人，但给出的做菜建议必须是顶级的。"
}

# 3. 初始化客户端
# 这里就是报错的地方，现在上面定义过了，就不会报错了
if api_key:
    client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
else:
    # 如果既没有 secrets 也没填输入框
    st.warning("👈 请在左侧侧边栏输入 API Key，或者在 Secrets 中配置")
    st.stop() # 停止运行，防止后续报错

# 4. 初始化记忆
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 给鹏鹏加个开场白
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "嘿！我是鹏鹏，找我聊点啥？"
    })

# 获取当前角色的 System Prompt
system_prompt = role_prompts[selected_role]

# 5. 展示历史聊天
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. 处理输入
if user_input := st.chat_input("说点什么..."):
    
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 构造发送给 AI 的消息列表
        messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        
        try:
            response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3",
                messages=messages_to_send,
                stream=True,
                temperature=temperature
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"出错啦: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})




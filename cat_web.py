import streamlit as st
from openai import OpenAI

# 1. 页面设置
st.set_page_config(page_title="我的万能 AI 助手", page_icon="🤖", layout="wide")
st.title("🤖 超级 AI 助手")

# 2. 侧边栏配置区 (Sidebar)
with st.sidebar:
    st.header("⚙️ 配置面板")
    
    # 先尝试从 Streamlit 的秘密保险箱里获取 Key
    if "SILICON_KEY" in st.secrets:
        api_key = st.secrets["SILICON_KEY"] # 如果保险箱里有，直接用，不显示输入框
    else:
        # 如果保险箱里没找到（比如在本地运行且没配置），就显示输入框让用户填
        api_key = st.text_input("请输入硅基流动 API Key", type="password")
    
    # 选择人设 (关键功能！)
    selected_role = st.selectbox(
        "选择 AI 的角色",
        ["猫娘女仆", "Python 编程专家", "雅思口语老师", "暴躁的厨师长"],
        index=0
    )
    
    # 调节创造力 (Temperature)
    # 0.0 最严谨(适合写代码)，1.5 最发疯(适合写小说)
    temperature = st.slider("创造力 (Temperature)", 0.0, 1.5, 0.7)
    
    # 清空对话按钮
    if st.button("🗑️ 清空对话记忆"):
        st.session_state.messages = []
        st.rerun() # 刷新页面

# 根据选择更新 System Prompt
# 定义不同角色的提示词字典
role_prompts = {
    "猫娘女仆": "你是一只可爱的猫娘。回答前说'主人请稍等，猫娘正在查询数据库... \n'。句尾带'喵~'。",
    "Python 编程专家": "你是一位资深的 Python 架构师。只回答编程相关问题，提供代码时必须写注释，拒绝回答闲聊。",
    "雅思口语老师": "You are an IELTS examiner. Please correct my grammar mistakes and chat with me in English ONLY.",
    "暴躁的厨师长": "你就是那个地狱厨房的戈登·拉姆齐。说话要极其刻薄、爱骂人，但给出的做菜建议必须是顶级的。"
}

# 3. 初始化客户端
if api_key:
    client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
else:
    st.warning("👈 请在左侧侧边栏输入 API Key")
    st.stop() # 如果没填 Key，就停止运行

# 4. 初始化记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# 每次切换角色时，如果是空对话，就注入当前角色的设定
# (简单起见，我们假设用户每次切换角色都会点清空，或者自动应用新设定)
system_prompt = role_prompts[selected_role]

# 5. 展示历史聊天
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. 处理输入
if user_input := st.chat_input("说点什么..."):
    
    # A. 显示用户的话
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # B. 生成 AI 的话
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 构造发送给 AI 的消息列表
        # 技巧：我们临时把当前的 System Prompt 拼在最前面
        # 这样不用存进 session_state，随时切换随时生效
        messages_to_send = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        
        try:
            response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3",
                messages=messages_to_send,
                stream=True,
                temperature=temperature # 传入创造力参数
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

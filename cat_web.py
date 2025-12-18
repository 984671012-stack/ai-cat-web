import streamlit as st
from openai import OpenAI

# 1. 页面设置
st.set_page_config(page_title="AI 鹏鹏助手", page_icon="👦", layout="wide")
st.title("👦 你的 AI 好友：鹏鹏")

# 选择人设
    selected_role = st.selectbox(
        "选择 AI 的角色",
        # 把 "鹏鹏" 放在第一个，他就是默认值
        ["鹏鹏", "猫娘女仆", "Python 编程专家", "雅思口语老师", "暴躁的厨师长"],
        index=0
    )

# ... (省略中间代码) ...

# 定义角色提示词
role_prompts = {
    "鹏鹏": "你叫鹏鹏，是用户的好朋友。你的说话语气要自然、随和，就像朋友之间聊天一样。不要太客气，也不要太严肃。如果不知道的问题就直说。可以用一些日常口语。",
    
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
    # 【新增】如果是第一次打开，给鹏鹏加一句开场白（仅在界面显示，不存入 System Prompt）
    # 注意：为了逻辑简单，我们通常直接让用户先说话。
    # 但如果你想让他先说话，可以手动 append 一句 assistant 的话：
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "嘿！我是鹏鹏，找我聊点啥？"
    })

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


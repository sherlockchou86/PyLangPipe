async function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (!message) return;

    //sendButton.disabled = true;
    appendMessage("我自己：", message, "user");
    input.value = "";
    const online_search = document.getElementById("searchCheckbox").checked;
    reply_title = "LangPipe：";
    if (online_search) {
        reply_title = "LangPipe（联网问答）：";
    } else {
        reply_title = "LangPipe（LLM问答）：";
    }
    const thinking_msg = appendMessage(reply_title, "正在思考中...", "bot");
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, online_search })
      });
  
      const data = await response.json();
      appendMessage(reply_title, data.reply, "bot");
    } catch (error) {
      appendMessage(reply_title, "发生错误，请稍后再试。", "bot");
    } finally {
        if (thinking_msg) {
            thinking_msg.remove();
        }
    }
  }
  
  function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  function appendMessage(nickname, text, type) {
    const chatMessages = document.getElementById("chatMessages");
  
    const msgWrapper = document.createElement("div");
    msgWrapper.classList.add("message", type);
  
    const nicknameElem = document.createElement("div");
    nicknameElem.classList.add("nickname");
    nicknameElem.textContent = nickname;
  
    const textElem = document.createElement("div");
    textElem.classList.add("text");
    textElem.textContent = text;
  
    const timeElem = document.createElement("div");
    timeElem.classList.add("time");
    timeElem.textContent = getCurrentTime();
  
    msgWrapper.appendChild(nicknameElem);
    msgWrapper.appendChild(textElem);
    msgWrapper.appendChild(timeElem);
  
    chatMessages.appendChild(msgWrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return msgWrapper;
  }
  
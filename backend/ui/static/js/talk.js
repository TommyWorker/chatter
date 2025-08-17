// talk.js
// トーク画面で利用するjavascript関数群

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

// IME入力中フラグ
let isComposing = false;
chatInput.addEventListener("compositionstart", () => isComposing = true);
chatInput.addEventListener("compositionend", () => isComposing = false);

// 自分のメッセージ追加
function addMyMessage(text) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");

    const sender = document.createElement("div");
    sender.classList.add("sender-name", "text-end");
    sender.textContent = "あなた";

    const messageEl = document.createElement("div");
    messageEl.classList.add("message", "sent");
    messageEl.textContent = text;

    wrapper.appendChild(sender);
    wrapper.appendChild(messageEl);
    chatMessages.appendChild(wrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 相手のメッセージ追加
function addOtherMessage(text, senderName = "XXX") {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");

    const sender = document.createElement("div");
    sender.classList.add("sender-name");
    sender.textContent = senderName + "さん";

    const messageEl = document.createElement("div");
    messageEl.classList.add("message", "received");
    messageEl.textContent = text;

    wrapper.appendChild(sender);
    wrapper.appendChild(messageEl);
    chatMessages.appendChild(wrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// フォーム送信
chatForm.addEventListener("submit", function(e) {
    e.preventDefault();
    const messageText = chatInput.value.trim();
    if (messageText !== "") {
        addMyMessage(messageText);
        chatInput.value = "";

        // デモ：相手から返信
        setTimeout(() => {
            addOtherMessage("これはサーバーからの返信です！", "山田");
        }, 2000);
    }
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        if (e.shiftKey) return; // Shift+Enterは改行
        if (isComposing) return; // IME確定前は送信しない
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});



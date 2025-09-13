// chat.js
// チャット画面で利用するjavascript関数群

const room_id = document.getElementById("hdn_room_id").value;
const user_id = document.getElementById("hdn_user_id").value;
const user_name = document.getElementById("hdn_user_name").value;

    const ws = new WebSocket(
    `ws://${location.host}/ws/${encodeURIComponent(room_id)}/${encodeURIComponent(user_id)}/${encodeURIComponent(user_name)}`
);

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

// IME変換中を示すフラグ管理（日本語入力中にSubmitされないようにするための措置）
let isComposing = false;
chatInput.addEventListener("compositionstart", () => isComposing = true);
chatInput.addEventListener("compositionend", () => isComposing = false);

function addMessage(text, sender) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");

    const senderEl = document.createElement("div");
    senderEl.classList.add("sender-name");
    if (sender === user_name) {
        senderEl.classList.add("text-end");
        senderEl.textContent = 'あなた';
    } else {
        senderEl.textContent = sender + "さん";
    }

    const msgEl = document.createElement("div");
    msgEl.classList.add("message", sender === user_name ? "sent" : "received");
    msgEl.textContent = text;

    wrapper.appendChild(senderEl);
    wrapper.appendChild(msgEl);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (text) {
        ws.send(text);
        chatInput.value = "";
    }
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    addMessage(data.message, data.sender);
};

// ページロード
function page_init(){

    fetch("/chat/" + room_id + "/api")
    .then(res => res.json())
    .then(data => {
        loadMessage(data.messages);
    });
    

}

// 既存登録メンバーをロード
function loadMessage(messageData) {
    console.log(messageData)
    messageData.forEach(msg => {
        addMessage(msg.message, msg.user.user_name);
    });
}
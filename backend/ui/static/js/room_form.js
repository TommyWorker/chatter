// room_form.js
// ルーム入力画面で利用するjavascript関数群

const member_input = document.getElementById("sel_member");
const selected_area = document.getElementById("selected_area");
const hidden_container = document.getElementById("membershidden_container");


// Enter またはカンマでメンバー追加
member_input.addEventListener("keydown", function(e) {
    
    if (e.key === "Enter" || e.key === ",") {
        e.preventDefault(); // フォーム送信防止
        const val = member_input.value.trim();
        if (val !== "") {
            // datalist からユーザ名を取得
            const option = Array.from(document.getElementById("lst_member").options)
                                .find(opt => opt.value === val);
            const username = option ? option.dataset.username : "";
            addMemberTag(val, username);
            member_input.value = "";
        }
    }
});

function addMemberTag(mail, username = "") {

    // バッジ生成
    const badge = document.createElement("span");
    badge.className = "badge bg-primary mb-2 me-1 fs-6";

    const displayText = username ? `${mail} (${username})` : mail;
    badge.textContent = displayText;

    // 削除ボタン
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn-close btn-close-white ms-2";
    removeBtn.style.fontSize = "0.8em";
    removeBtn.onclick = () => {
    const hidden = badge.querySelector('input[type="hidden"]');
    if(hidden) hidden.remove();
        badge.remove();
    };
    badge.appendChild(removeBtn);

    // hidden input（サーバ送信用、メールアドレスのみ）
    const hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = "members[]";
    hidden.value = mail;

    hidden_container.appendChild(hidden);
    badge.appendChild(removeBtn);;
    selected_area.appendChild(badge);
}

// ページロード
function page_init(){

    

}



// 登録ボタン押下時
function send_data() {

    // 入力チェック
    if (!entry_check()) {
        return false;
    } 

    // 入力値取得
    const room_id = document.getElementById("hdn_room_id").value
    const room_name = document.getElementById("txt_room_name").value
    const remarks = document.getElementById("txt_remarks").value
    /// hidden に入っている値を全部集める
    const members = Array.from(document.querySelectorAll('input[name="members[]"]'))
                     .map(input => input.value);


    fetch("/room_entry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room_id, members, room_name, remarks })
    })
    .then(response => response.json())
    .then(data => {
        if(data.result === "complete"){
            disp_info(data.sys_msg, "div_message_area")
        }else{
            disp_alert(data.sys_msg, "div_message_area")
        }
    })
    .catch(error => {
        disp_alert(error, "div_message_area")
    });

}

// 登録時入力チェック処理
function entry_check() {

    // メールアドレスの形式チェック
    // const txt_mail_address = document.getElementById("txt_mail_address").value
    // if (!is_string_empty(txt_mail_address)) {
    //     if (!is_email_string(txt_mail_address)) {
    //         disp_alert("メールアドレスの形式が不正です。", "div_message_area");
    //         return false;
    //     }
    // }

    // エラーなし・正常終了
    return true;
}
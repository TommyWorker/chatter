// user_form.js
// ユーザ入力画面で利用するjavascript関数群

const member_input = document.getElementById("sel_member");
const selectedArea = document.getElementById("selectedArea");
const hiddenContainer = document.getElementById("membersHiddenContainer");

// Enter またはカンマでメンバー追加
member_input.addEventListener("keydown", function(e) {
    
    if (e.key === "Enter" || e.key === ",") {
        e.preventDefault(); // フォーム送信防止
        const val = member_input.value.trim();
        if (val !== "") {
            // datalist からユーザ名を取得できるか確認
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

    badge.appendChild(hidden);
    selectedArea.appendChild(badge);
    hiddenContainer.appendChild(hidden);
}


// 登録ボタン押下時
function disp_onsubmit() {

    // 入力チェック
    if (!entry_check()) {
        return false;
    } 

    // Submit
    document.getElementById("form_main").submit();

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
// user_form.js
// ユーザ入力画面で利用するjavascript関数群

// 登録ボタン押下時
function disp_onsubmit() {

    // 入力チェック
    if (!entry_check()) {
        return false;
    }    
}

// 登録時入力チェック処理
function entry_check() {

    // メールアドレスの形式チェック
    const txt_mail_address = document.getElementById("txt_mail_address").value
    if (!is_string_empty(txt_mail_address)) {
        if (!is_email_string(txt_mail_address)) {
            disp_alert("メールアドレスの形式が不正です。", "div_message_area");
            return false;
        }
    }

    // 同じパスワードが入力されているか
    const txt_password = document.getElementById("txt_password").value
    const txt_password_confirm = document.getElementById("txt_password_confirm").value
    if (!is_string_empty(txt_password)) {
        if (txt_password != txt_password_confirm) {
            disp_alert("入力されたパスワードが異なります。確認してください。", "div_message_area");
            return false;
        }
    }

    // エラーなし・正常終了
    return true;
}
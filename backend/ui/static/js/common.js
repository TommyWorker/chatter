// common.js
// 全画面共通で利用するjavascript群

// フォーム検証のためのスターター
// 無効なフィールドがある場合にフォーム送信を無効にするスターター
(() => {
    "use strict"

    // Bootstrapカスタム検証スタイルを適用してすべてのフォームを取得
    const forms = document.querySelectorAll(".needs-validation")

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener("submit", event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()

                // エラーメッセージ表示
                document.getElementById("div_message_area").innerHTML = '<div class="alert alert-danger alert-dismissible fade show" role="alert">'
                    + ' 入力エラーがあります。赤枠部分を確認してください。'
                    + ' <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
                    + '</div > '

                form.classList.add("was-validated");

            } else {
                // 確認メッセージ表示
                if (!event.defaultPrevented && !confirm("入力した内容で登録します。よろしいですか？")){
                    event.preventDefault();
                    return false;
                }
            }
        }, false)
    })
})()


// スクロールボタンの表示/非表示を制御する
window.onscroll = function() {
    var scrollToTopBtn = document.getElementById("scrollToTopBtn");
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        scrollToTopBtn.style.display = "block";
    } else {
        scrollToTopBtn.style.display = "none";
    }
};
// スクロールボタンをクリックしたときに上へスクロールする
document.getElementById("scrollToTopBtn").onclick = function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

// ハイパーリンククリック時のメッセージ表示（confirm-linkクラスが指定されているアンカータグが対象）
document.addEventListener("DOMContentLoaded", function() {
    let specificLinks = document.querySelectorAll("a.confirm-link");
    specificLinks.forEach(function(link) {
        link.addEventListener("click", function(event) {
        if (!confirm("入力内容が保存されていません。ページを離れてよろしいですか？")) {
            event.preventDefault();
        }
        });
    });
});

// メッセージを表示
// msg: 表示するメッセージ
// position: 表示する位置（idを指定）
function disp_info(msg, position_id) {

    document.getElementById(position_id).innerHTML =
        '<div class="alert alert-info alert-dismissible fade show" role="alert">'
        + msg
        + ' <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
        + '</div > '

}

// エラーメッセージを表示
// msg: 表示するメッセージ
// position: 表示する位置（idを指定）
function disp_alert(msg, position_id) {

    document.getElementById(position_id).innerHTML =
        '<div class="alert alert-danger alert-dismissible fade show" role="alert">'
        + msg
        + ' <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'
        + '</div > '

}

// 空白か判定
// check_target: チェック対象文字列
function is_string_empty(check_target) {

    return !check_target?.trim()

}

// 半角数字か判定
// check_target: チェック対象文字列
function is_num(check_target) {
    // 半角英数字のパターン 正規表現
    const pattern = /[^0-9]+/;
    return !(pattern.test(check_target))
}

// 半角英数字か判定
// check_target: チェック対象文字列
function is_alphabet_num(check_target) {
    // 半角英数字のパターン 正規表現
    const pattern = /[^A-Za-z0-9]+/;
    return !(pattern.test(check_target))
}

// メールアドレス形式か判定
// check_target: チェック対象文字列
function is_email_string(check_target) {

    // メールアドレスのパターン 正規表現
    const pattern = /^[A-Za-z0-9]{1}[A-Za-z0-9_.-]*@{1}[A-Za-z0-9_.-]+.[A-Za-z0-9]+$/;
    return pattern.test(check_target);
}

// 日付形式か判定
// check_target: チェック対象文字列
function is_date_string(check_target) {
    const date = new Date(check_target);

    if (isNaN(date.getDate())) {
        return false;
    }
    else {
        // SQL ServerのSmallDatetimeのサイズに合わせてチェック
        const max_date = new Date(2078, 12, 1, 0, 0, 0);
        const min_date = new Date(1899, 12, 1, 0, 0, 0);

        if (date < max_date && date >= min_date) {
            return true;
        }
        else {
            return false;
        }
    }
}

// 現在日付をyyyy-mm-dd hh:mm:ss形式で取得
function get_now_format_string() {

    const date = new Date();
    const local_date = new Date(date - date.getTimezoneOffset() * 60000); //offset in milliseconds. Credit https://stackoverflow.com/questions/10830357/javascript-toisostring-ignores-timezone-offset

    date.setTime(local_date);
    return date.toISOString().replace('T', ' ').substring(0, 19);
}

// 現在日付をカレンダーコントロールが認識できる形式で取得
function get_now_calender_value() {

    const date = new Date();
    let local_date = new Date(date - date.getTimezoneOffset() * 60000); //offset in milliseconds. Credit https://stackoverflow.com/questions/10830357/javascript-toisostring-ignores-timezone-offset

    // 秒/ミリ秒は削除
    local_date.setSeconds(null);
    local_date.setMilliseconds(null);
    return local_date.toISOString().slice(0, -1);

}

// 改行を<br>タグへ変換
// target: 変換対象文字列
function convert_brtag(target) {

    return target.replace(/\r?\n|\r/g, "<br>")
}

// URLを<a>タグへ変換
// target: 変換対象文字列
function convert_anker_tag(target) {

    // URLマッチ文字列
    const regexp_url = /(https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+)/g;
    return target.replace(regexp_url, '<a href="$1" target="_blank">$1</a>');
}

// ドメイン内のすべてのCookieを削除
//   ※Cookieの有効期限を0にすることで削除
function delete_all_cookies() {
    const cookies = document.cookie.split(';')
    for (i = 0; i < cookies.length; i++) {
        let cookie = cookies[i]
        let eqPos = cookie.indexOf('=')
        let name = eqPos > -1 ? cookie.substring(1, eqPos.length) : cookie
        document.cookie = name + '=;max-age=0'
    }
}

// Enterキー押下にSubmit実行対応
function enableEnterKey(func, ...fields) {

    fields.forEach(id => {
        document.getElementById(id).addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                func();
            }
        });
    });
}
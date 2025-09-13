// general_list.js
// 汎用マスタ一覧で利用するjavascript関数群

// クリアボタン押下時
function clear_onclick() {

    // 検索条件初期化
    set_search_clear();

    // 検索条件をCookieへ設定
    set_search_cookie();

    //初回ロード時と同様のフラグに変更
    document.getElementById('hdn_page_no').value = 0;
    document.cookie = "hdn_page_no=" + document.getElementById("hdn_page_no").value;

    // Submit
    document.getElementById("form_list").action = "/general/list";
    document.getElementById("form_list").submit(this.form);

}

// ダウンロードリンク押下時
function download_onclick() {

    // 検索条件をCookieへ設定
    set_search_cookie();

    // Submit
    document.getElementById("form_list").action = "/general/list/download";
    document.getElementById("form_list").submit(this.form);

}

// 検索ボタン押下時
// 検索処理実施
function get_search_list(page_no) {


    // Hiddenへページ番号を設定
    document.getElementById("hdn_page_no").value = page_no;

    // 検索条件をCookieへ設定
    set_search_cookie();

    // Submit
    document.getElementById("form_list").action = "/general/list";
    document.getElementById("form_list").submit(this.form);

}

// 検索条件をCookieへセット
function set_search_cookie() {

    document.cookie = "sel_category=" + encodeURIComponent(document.getElementById("sel_category").value);
    document.cookie = "txt_code_value=" + encodeURIComponent(document.getElementById("txt_code_value").value);
    document.cookie = "hdn_page_no=" + document.getElementById("hdn_page_no").value;
    document.cookie = "sel_row_max=" + document.getElementById("sel_row_max").value;

}

// 検索条件を初期化
function set_search_clear() {

    document.getElementById("sel_category").value = "";
    document.getElementById("txt_code_value").value = "";
    document.getElementById("hdn_page_no").value = 1;

}

// 検索条件のテキストボックス上でEnterをクリックすると検索実行
enableEnterKey(() => get_search_list(1), "txt_code_value");

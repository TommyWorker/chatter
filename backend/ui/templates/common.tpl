<!-- 全画面共通のヘッダー部 -->

{% macro common_header(login_user, mode) -%}
<header>
    {% if mode == "new" or mode == "edit" %}
    <nav class="navbar navbar-expand-lg bg-danger bg-gradient">
    {% else %}
    <nav class="navbar navbar-expand-lg bg-secondary bg-gradient">
    {% endif %}
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <h2 class="text-white">Chatter</h2>
            </a>
            <div class="navbar-collapse col-auto" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto">
                    {% if login_user.authority_code >= 0 %}
                    <li class="nav-item mx-2">
                        <a class="nav-link active text-white text-decoration-underline" href="/">Home</a>
                    </li>
                    {% endif %}
                    <li class="nav-item dropdown">
                        <a class="nav-link active text-white text-decoration-underline dropdown-toggle" id="link_check" data-bs-toggle="dropdown"
                            href="#" role="button">マスタメンテナンス</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/general/list">汎用マスタ</a></li>
                            <li><a class="dropdown-item" href="/user/list" >ユーザマスタ</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div class="col-auto text-end">
                <div class="text-light">
                    {{login_user.account_display_name}} 【{{login_user.authority[0].code_value or ''}}】
                </div>
                <a class="link-light me-3" href="/user/{{login_user.id}}/edit">プロファイル変更</a>
                <a class="link-light" href="/logout">ログアウト</a>
            </div>
        </div>
    </nav>
</header>
{%- endmacro %}
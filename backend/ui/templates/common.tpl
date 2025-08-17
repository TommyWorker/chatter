{% macro common_sidebar(login_user, mode) -%}
<div class="d-flex flex-column flex-shrink-0 p-3 text-bg-dark" style="width: 220px; height: 100vh; ">
  <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
    <h2 class="fs-4">Chatter</h2>
  </a>
  <hr>
  <ul class="nav nav-pills flex-column mb-auto">
    {% if login_user.authority_code >= 0 %}
    <li class="nav-item">
      <a href="/room/list" class="nav-link text-white">Chat Room</a>
    </li>
    {% endif %}
    {% if login_user.authority_code >= 99 %}
    <li>
      <a href="#" class="nav-link dropdown-toggle text-white" data-bs-toggle="collapse" data-bs-target="#submenu" aria-expanded="false">
        Maintenance
      </a>
      <div class="collapse" id="submenu">
        <ul class="btn-toggle-nav list-unstyled fw-normal pb-1 small">
          <li><a href="/general/list" class="nav-link text-white ps-4">汎用マスタ</a></li>
          <li><a href="/user/list" class="nav-link text-white ps-4">ユーザマスタ</a></li>
        </ul>
      </div>
    </li>
    {% endif %}
  </ul>
  <hr>
  <div class="p-3">
    <div class="text-white small">
      {{ login_user.user_name }} <br>
      【{{ login_user.authority[0].code_value or '' }}】
    </div>
    <a class="small link-light mb-3 d-block" href="/user/{{login_user.id}}/edit">Profile</a>
    <a class="link-light d-block" href="/logout">Logout</a>
  </div>
</div>
{%- endmacro %}

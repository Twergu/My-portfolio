/* Metadata, session and access controls. Authorization is enforced by the server. */
function showLogin() {
  const ja = state.locale === 'ja';
  state.docs = []; state.messages = []; state.selected = ''; state.source = null;
  $('#app').innerHTML = `<main class="boot"><h1>Knowbase</h1><p>${ja ? '管理者が発行したアクセストークンでログインしてください。' : '请使用管理员签发的访问令牌登录。'}</p><form id="login-form"><label for="login-token">${ja ? 'アクセストークン' : '访问令牌'}</label><input id="login-token" type="password" required autocomplete="off" minlength="20" maxlength="200"><button class="button primary">${ja ? 'ログイン' : '登录'}</button><p id="login-error" role="alert"></p></form></main>`;
  $('#login-form').onsubmit = async event => {
    event.preventDefault();
    const token = $('#login-token').value;
    try { await api('/auth/login', {method:'POST', body:{token}}); await init(); }
    catch (error) { $('#login-error').textContent = error.message; }
  };
}

function applyAccess() {
  const user = state.auth?.user;
  if (!user) return;
  const admin = user.roles.includes('admin');
  const editor = admin || user.roles.includes('editor');
  const ja = state.locale === 'ja';
  const displayName = state.auth.mode === 'local' ? (ja ? 'ローカルユーザー' : '本地用户') : user.username;
  if ($('.local-user div')) $('.local-user div').innerHTML = `${esc(displayName)}<small>${esc(user.roles.join(' · '))}</small>`;
  if ($('.local-user b')) $('.local-user b').textContent = 'v0.4';
  if ($('.workspace small')) $('.workspace small').textContent = state.auth.mode === 'required' ? (ja ? 'アクセス制御が有効' : '已启用访问控制') : (ja ? 'ローカル・単一ユーザー' : '本地单用户模式');
  document.querySelectorAll('[data-action="upload"],[data-action="sample"]').forEach(button => button.disabled = !editor);
  document.querySelectorAll('[data-action="reindex"]').forEach(button => button.disabled = !admin);
  if (!admin) document.querySelectorAll('#settings-form input,#settings-form select,#settings-form button').forEach(el => el.disabled = true);
  if (!$('#session-control') && $('.topbar-actions')) {
    const button = document.createElement('button');
    button.id = 'session-control'; button.className = 'text-button';
    button.textContent = state.auth.mode === 'local' ? (state.locale === 'ja' ? 'ローカル利用' : '本地单用户') : `${user.username} · ${state.locale === 'ja' ? 'ログアウト' : '退出'}`;
    button.disabled = state.auth.mode === 'local';
    button.onclick = async () => { await api('/auth/logout', {method:'POST'}); state.auth = null; showLogin(); };
    $('.topbar-actions').append(button);
  }
}

function renderFilters() {
  const ja = state.locale === 'ja';
  const filters = state.filters || {};
  const selected = filters.policy_status?.[0] || '';
  $('#question-form').insertAdjacentHTML('beforebegin', `<details class="retrieval-filters"><summary>${ja ? 'ポリシー・部門・有効日の絞り込み' : '按政策状态、部门与生效日期筛选'}</summary><div class="field-grid"><div class="field"><label for="policy-filter">${ja ? 'ポリシー状態' : '政策状态'}</label><select id="policy-filter">${[['','すべて','全部'],['current','現行','现行'],['archived','旧版','旧版'],['draft','草案','草案'],['unclassified','未分類','未分类']].map(([v,j,z]) => `<option value="${v}" ${v===selected?'selected':''}>${ja?j:z}</option>`).join('')}</select></div><div class="field"><label for="date-filter">${ja ? '基準日' : '适用日期'}</label><input id="date-filter" type="date" value="${esc(filters.as_of || '')}"></div><div class="field"><label for="department-filter">${ja ? '部門（完全一致）' : '部门（精确匹配）'}</label><input id="department-filter" maxlength="120" value="${esc(filters.department || '')}"></div></div><small>${ja ? '日付指定時は有効開始日が不明の資料を除外します。空欄は絞り込みなし。' : '指定日期时排除未标明生效日期的文档；留空表示不按此字段筛选。'}</small></details>`);
  const sync = () => {state.filters = {
    policy_status: $('#policy-filter').value ? [$('#policy-filter').value] : [],
    as_of: $('#date-filter').value || null,
    department: $('#department-filter').value || null,
  };};
  for (const id of ['policy-filter','date-filter','department-filter']) $(`#${id}`).onchange = sync;
}

function appendVerificationSettings(config) {
  const ja = state.locale === 'ja';
  $('#verification-mode').closest('.settings-section').insertAdjacentHTML('beforeend', `<div class="field-grid"><div class="field"><label for="verification-strategy">${ja ? '検証対象' : '验证范围'}</label><select id="verification-strategy" name="verification_strategy">${['all','selective'].map(v => `<option ${config.verification_strategy===v?'selected':''}>${v}</option>`).join('')}</select></div><div class="field"><label for="verifier-prompt">${ja ? '検証プロンプト' : 'Verifier 提示词'}</label><select id="verifier-prompt" name="verifier_prompt">${['baseline','calibrated'].map(v => `<option ${config.verifier_prompt===v?'selected':''}>${v}</option>`).join('')}</select></div></div><small>${ja ? 'selective は単純な原文の全文引用のみ意味検証を省略し、未検証と表示します。標準は all です。' : 'selective 仅对简单的完整原文摘录跳过语义验证，并标记未验证；默认使用 all。'}</small>`);
}

async function editMetadata(id) {
  const doc = state.docs.find(d => d.id === id);
  if (!doc) return;
  const ja = state.locale === 'ja';
  const dialog = $('#preview-dialog');
  dialog.innerHTML = `<div class="dialog-header"><h2 id="preview-title">${esc(doc.name)}</h2><button class="icon-btn" data-action="close-dialog" aria-label="${ja?'閉じる':'关闭'}">${icon('close')}</button></div><form id="metadata-form"><div class="field-grid"><div class="field"><label>${ja?'ポリシー状態':'政策状态'}<select name="policy_status">${['unclassified','current','archived','draft'].map(v => `<option ${doc.policy_status===v?'selected':''} value="${v}">${({unclassified:ja?'未分類':'未分类',current:ja?'現行':'现行',archived:ja?'旧版':'旧版',draft:ja?'草案':'草案'})[v]}</option>`).join('')}</select></label></div>${[['effective_from',ja?'有効開始日':'生效日期','date'],['effective_to',ja?'有効終了日（含む）':'失效日期（含当天）','date'],['department',ja?'部門':'部门','text'],['document_version',ja?'バージョン':'版本号','text']].map(([name,label,type]) => `<div class="field"><label>${label}<input name="${name}" type="${type}" maxlength="120" value="${esc(doc[name] || '')}"></label></div>`).join('')}</div><p>${ja?'未分類の資料は現行ポリシーとは見なしません。':'未分类的文档不会自动视为现行政策。'}</p><button class="button primary" ${doc.can_write===false?'disabled':''}>${ja?'保存':'保存'}</button></form><div id="permission-editor"></div>`;
  if (doc.can_write === false) dialog.querySelectorAll('input,select').forEach(el => el.disabled = true);
  $('#metadata-form').onsubmit = async event => {
    event.preventDefault();
    const body = Object.fromEntries(new FormData(event.target));
    body.effective_from ||= null; body.effective_to ||= null;
    try { await api(`/documents/${id}/metadata`, {method:'PUT',body}); dialog.close(); await refreshDocs(); }
    catch(error) {toast(error.message,true);}
  };
  dialog.showModal();
  if (state.auth?.user?.roles.includes('admin')) {
    try {
      const data = await api(`/documents/${id}/permissions`);
      $('#permission-editor').innerHTML = `<hr><h3>${ja?'ロール別権限':'角色权限'}</h3><p>${data.permissions.map(p => `${esc(p.role_name)}: ${p.permission}`).join(' · ') || (ja?'付与なし（所有者と管理者のみ）':'未授权（仅所有者和管理员）')}</p><form id="permission-form"><div class="field"><label>${ja?'ロール名':'角色名称'}<input name="role" required maxlength="80"></label></div><div class="field"><select name="permission"><option value="read">${ja?'閲覧':'读取'}</option><option value="write">${ja?'編集':'编辑'}</option><option value="">${ja?'取り消し':'撤销'}</option></select></div><button class="button secondary">${ja?'権限を更新':'更新权限'}</button></form>`;
      $('#permission-form').onsubmit = async event => {event.preventDefault(); const body=Object.fromEntries(new FormData(event.target)); body.permission ||= null; try {await api(`/documents/${id}/permissions`,{method:'PUT',body}); dialog.close(); await editMetadata(id);} catch(error) {toast(error.message,true);}};
    } catch(error) {toast(error.message,true);}
  }
}

'use strict';

const paths = {
  chat: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/>',
  files: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
  settings: '<path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="M12 19V5M5 12l7-7 7 7"/>',
  upload: '<path d="M12 16V3M7 8l5-5 5 5M4 15v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  link: '<path d="M15 3h6v6M10 14 21 3"/><path d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/>',
  search: '<circle cx="10.5" cy="10.5" r="7.5"/><path d="m16 16 5 5"/>',
  trash: '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/>',
  refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-2l2 3M4 16l2 3a7 7 0 0 0 12-2"/>',
  spark: '<path d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4M12 14v3"/>',
  book: '<path d="M12 5c-3-2-6-2-10-1v16c4-1 7-1 10 1 3-2 6-2 10-1V4c-4-1-7-1-10 1zM12 5v16"/>',
  copy: '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
};
const icon = (name, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.files}</svg>`;
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const state = {view:'chat', docs:[], settings:null, messages:[], selected:'', draft:'', busy:false, uploading:false, source:null, locale:localStorage.getItem('knowbase-locale') || (navigator.language?.toLowerCase().startsWith('ja') ? 'ja' : 'zh')};
const $ = selector => document.querySelector(selector);
const readyDocs = () => state.docs.filter(doc => doc.status === 'ready' && !doc.needs_reindex);
let toastTimer, pollTimer;

const jaPairs = [
  ['HNSW 需要 PostgreSQL + pgvector 和 AI 问答模式；当前请使用 exact。','HNSWにはPostgreSQL + pgvectorとAI質問応答モードが必要です。現在はexactを使用してください。'], ['企业知识助手','企業ナレッジアシスタント'], ['企业工作空间','企業ワークスペース'], ['本地版本 · Phase 01','ローカル版 · Phase 01'],
  ['发起新问答','新しい質問'], ['工作空间','ワークスペース'], ['知识问答','ナレッジQ&A'], ['文档知识库','ドキュメント'], ['模型设置','モデル設定'],
  ['本次问答','今回の質問'], ['你的问题会显示在这里','質問履歴がここに表示されます'], ['文件保存在本机','ファイルはこのPCに保存されます'],
  ['API 模式下，相关文本将发送到','APIモードでは、関連テキストが'], ['你配置的模型服务。','設定したモデルサービスへ送信されます。'], ['本地用户','ローカルユーザー'], ['个人工作环境','個人ワークスペース'],
  ['添加文档','ドキュメントを追加'], ['让知识，成为答案','知識を答えに変える'], ['今天，想了解什么？','今日は何を知りたいですか？'],
  ['从你的企业文档中，找到有据可查的答案。','社内ドキュメントから、根拠のある答えを見つけます。'], ['上传团队文档，提问业务问题。','チームの資料をアップロードして、業務について質問できます。'], ['每个答案，都有原文可循。','すべての回答に原文の根拠があります。'],
  ['上传你的第一份文档','最初のドキュメントをアップロード'], ['制度、手册、项目资料 · PDF','規程、マニュアル、プロジェクト資料 · PDF'], ['用演示文档体验','サンプル資料で試す'], ['员工手册 · 3 页示例内容','社員ハンドブック · 3ページのサンプル'],
  ['试着问问','質問例'], ['员工年假如何申请？','年次有給休暇はどのように申請しますか？'], ['差旅报销需要哪些材料？','出張精算に必要な書類は何ですか？'],
  ['向知识库提问','ナレッジベースに質問'], ['检索范围','検索範囲'], ['基于所选文档回答 · 点击引用核对原文','選択した資料に基づく回答 · 引用をクリックして原文を確認'],
  ['我的知识库','マイナレッジベース'], ['管理文档','ドキュメントを管理'], ['就绪文档','準備完了の資料'], ['知识片段','ナレッジチャンク'], ['文档来源','資料の出典'], ['一份文档，如何成为答案','ドキュメントが答えになるまで'],
  ['解析文档','ドキュメントを解析'], ['提取文字，保留页码','文字を抽出し、ページ番号を保持'], ['检索相关内容','関連情報を検索'], ['配置模型后启用语义检索','モデル設定後に意味検索を有効化'], ['带着依据回答','根拠を示して回答'], ['点击引用，回到原文','引用をクリックして原文を確認'],
  ['连接你的 AI 模型','AIモデルを接続'], ['启用语义检索和 AI 生成回答。','意味検索とAI回答を有効にします。'], ['配置模型','モデルを設定'], ['添加','追加'],
  ['文档知识库','ドキュメント'], ['全部文档','すべてのドキュメント'], ['导入演示文档','サンプル資料を追加'], ['重建索引','インデックスを再構築'], ['拖入 PDF 文件，或点击选择','PDFをドラッグするかクリックして選択'], ['点击选择','クリックして選択'], ['支持批量上传 · 单份不超过 20 MB / 200 页 · 扫描件需先做 OCR','複数アップロード対応 · 1件20MB / 200ページまで · スキャン資料はOCRが必要'], ['从第一份文档开始','最初のドキュメントから始める'], ['上传企业资料，或导入演示文档体验完整流程。','社内資料をアップロードするか、サンプル資料で流れを試せます。'], ['文档与索引保存在本机。更换 Embedding 服务或模型后，请重建索引。','資料とインデックスはこのPCに保存されます。Embeddingサービスまたはモデル変更後は再構築してください。'],
  ['选择工作模式','動作モード'], ['暂时没有 API？也可以先用原文检索。','APIがなくても、まず原文検索を使えます。'], ['AI 问答','AI質問応答'], ['语义向量检索 + 基于原文生成回答','意味ベクトル検索 + 原文に基づく回答生成'], ['原文检索','原文検索'], ['本地关键词匹配，直接返回原文片段','ローカルキーワード検索で原文を返す'],
  ['模型服务','モデルサービス'], ['回答和 Embedding 使用同一个服务地址与密钥。','回答とEmbeddingには同じサービスURLとキーを使用します。'], ['API 服务地址','APIサービスURL'], ['填写 API 根路径，通常以 /v1 结尾。','APIのルートURLを入力します。通常は /v1 で終わります。'], ['API 密钥','APIキー'], ['界面输入的密钥仅保留在服务端内存中，重启后需重新输入。','画面で入力したキーはサーバーのメモリにのみ保持され、再起動後は再入力が必要です。'], ['清除已配置的密钥','保存済みのキーを消去'], ['回答模型','回答モデル'], ['Embedding 模型','Embeddingモデル'], ['检索设置','検索設定'], ['更换 Embedding 配置后，已有文档需要重建索引。','Embedding設定を変更した場合、既存資料の再構築が必要です。'], ['最多检索片段','最大検索チャンク数'], ['最低语义相似度','最低意味類似度'], ['仅用于 AI 模式，需根据实际模型调整；不代表回答可信度。','AIモードのみ使用。モデルに合わせて調整してください。回答の信頼度ではありません。'], ['AI 模式会将文档文本用于 Embedding，并将检索到的片段和问题发送到上方配置的模型服务。','AIモードでは文書テキストをEmbeddingに使用し、検索チャンクと質問を上記のモデルサービスへ送信します。'], ['测试连接','接続テスト'], ['保存配置','設定を保存'], ['测试连接会调用一次 Embedding 和一次回答接口，可能产生 API 费用。','接続テストではEmbeddingと回答APIを1回ずつ呼び出すため、料金が発生する場合があります。'],
  ['原文检索模式','原文検索モード'], ['AI 问答模式','AI質問応答モード'], ['已就绪','準備完了'], ['处理失败','処理失敗'], ['待重建','再構築が必要'], ['等待处理','処理待ち'], ['解析中','解析中'], ['建立索引','インデックス作成中'], ['向量化中','ベクトル化中'], ['未找到可引用的答案','引用できる回答が見つかりません'], ['正在查找相关内容…','関連情報を検索しています…'], ['正在检索文档','ドキュメントを検索しています'], ['AI 回答','AI回答'], ['查看引用','引用を表示'], ['复制回答','回答をコピー'], ['返回文档列表','資料一覧に戻る'], ['引用来源','引用元'], ['原文片段','原文の抜粋'], ['在 PDF 中查看','PDFで確認'], ['页码对应 PDF 的实际页序。请结合原文上下文核对回答。','ページ番号はPDFの実際の順序です。原文の文脈と照合してください。'], ['PDF 第','PDF '], ['页','ページ'], ['个引用','件の引用'], ['秒','秒'], ['文件格式','ファイル形式'], ['演示内容，不代表实际公司政策。','サンプル内容であり、実際の会社規程ではありません。'], ['份','件'], [' 个',' 個'], ['页数 / 片段','ページ / チャンク'], ['添加时间','追加日'], ['把分散的 PDF，变成团队可检索的知识。','散らばったPDFを、チームで検索できる知識に変えます。'], ['拖入 PDF 文件，或 クリックして選択','PDFをドラッグするかクリックして選択'], ['文档名称','資料名'], ['状态','ステータス'], ['片段','チャンク'], ['文档与索引保存在本机。更换 Embedding 服务或模型后，请インデックスを再構築。','資料とインデックスはこのPCに保存されます。Embeddingサービスまたはモデル変更後は再構築してください。'],
  ['请输入问题。','質問を入力してください。'], ['请先上传或导入文档，等待索引就绪后再提问。','先に資料をアップロードまたは追加し、準備完了になるまでお待ちください。'], ['无法连接本地服务，请检查应用是否正在运行。','ローカルサービスに接続できません。アプリが起動しているか確認してください。'], ['仅支持有效的 PDF 文件。','有効なPDFファイルのみ対応しています。'], ['单个 PDF 不能超过 20 MB。','1件のPDFは20MB以内にしてください。'], ['PDF 已加密，请先解密后再上传。','PDFが暗号化されています。復号してから再アップロードしてください。'], ['未提取到文字。这可能是扫描版 PDF，请先进行 OCR 文字识别。','文字を抽出できませんでした。スキャンPDFの場合は、先にOCRを実行してください。'], ['处理失败，请重试；若持续失败，请检查服务日志。','処理に失敗しました。再試行してください。繰り返し失敗する場合はログを確認してください。'], ['请等待文档处理完成后再修改模型配置。','資料の処理が完了してからモデル設定を変更してください。'], ['请等待处理完成后再删除。','処理が完了してから削除してください。'], ['文档不存在或已删除。','資料が存在しないか、削除されています。'], ['所选文档已删除、尚未就绪或需要重建索引，请重新选择。','選択した資料が削除されたか、準備未完了または再構築が必要です。選び直してください。']
];
function localized(text) {
  if (state.locale !== 'ja') return text;
  let result = text;
  for (const [from, to] of jaPairs) result = result.split(from).join(to);
  const cleanup = [
    ['界面语言', '表示言語'], ['选择应用界面和提示信息的语言。', 'アプリの表示と案内メッセージの言語を選択します。'], ['简体中文', '中国語（簡体字）'],
    ['连接兼容 OpenAI 的服务，自由选择回答与 Embedding 模型。', 'OpenAI互換サービスに接続し、回答モデルとEmbeddingモデルを選択します。'],
    ['连接兼容 OpenAI 的服务，自由选择回答与 Embedding模型。', 'OpenAI互換サービスに接続し、回答モデルとEmbeddingモデルを選択します。'],
    ['更换 Embedding 配置后，已有文档需要インデックスを再構築。', 'Embedding設定を変更した場合、既存資料の再構築が必要です。'],
    ['AI 模式会将文档文本用于 Embedding，并将检索到的片段和问题发送到上方配置的模型服务。', 'AIモードでは文書テキストをEmbeddingに使用し、検索チャンクと質問を上記のモデルサービスへ送信します。'],
    ['AI 模式会将文档文本用于 Embedding，并将检索到的片段和问题发送到上方的モデルサービス。', 'AIモードでは文書テキストをEmbeddingに使用し、検索チャンクと質問を上記のモデルサービスへ送信します。'],
    ['AI 模式会将文档文本用于 Embedding，并将检索到的片段和问题发送到上方配置的モデル服务。', 'AIモードでは文書テキストをEmbeddingに使用し、検索チャンクと質問を上記のモデルサービスへ送信します。'],
    ['追加时间', '追加日'], ['MODEL CONNECTION', 'モデル接続'],
    ['接続テスト会调用一次 Embedding 和一次回答接口，可能产生 API 费用。', '接続テストではEmbeddingと回答APIを1回ずつ呼び出すため、料金が発生する場合があります。']
  ];
  for (const [from, to] of cleanup) result = result.split(from).join(to);
  result = result.replace(/(\d+) 个引用/g, '$1件の引用').replace(/(\d+) 页/g, '$1ページ').replace(/全部就绪文档/g, '準備完了の資料');
  return result;
}
function applyLocale() {
  document.documentElement.lang = state.locale === 'ja' ? 'ja' : 'zh-CN';
  document.title = state.locale === 'ja' ? 'Knowbase · 企業ナレッジアシスタント' : 'Knowbase · 企业知识助手';
  const navigation = $('nav');
  if (navigation) navigation.setAttribute('aria-label', state.locale === 'ja' ? 'メインナビゲーション' : '主导航');
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const skip = '.recent-item,.answer-text,.source-quote,.preview-chunks,.user-question,.citation-card,.rail-doc,.table-file,.source-file';
  const nodes = [];
  while (walker.nextNode()) if (!walker.currentNode.parentElement.closest(skip)) nodes.push(walker.currentNode);
  nodes.forEach(node => { const value = localized(node.nodeValue); if (value !== node.nodeValue) node.nodeValue = value; });
  const question = $('#question');
  if (question) question.placeholder = state.locale === 'ja' ? 'ナレッジベースに質問：例）年次有給休暇はどのように申請しますか？' : '向知识库提问，例如：员工年假如何申请？';
  const scope = $('#scope');
  if (scope?.options[0]) scope.options[0].textContent = state.locale === 'ja' ? `準備完了の資料 (${readyDocs().length})` : `全部就绪文档 (${readyDocs().length})`;
  const localeButton = $('.locale-toggle');
  if (localeButton) {
    localeButton.textContent = state.locale === 'ja' ? '中文' : '日本語';
    localeButton.setAttribute('aria-label', state.locale === 'ja' ? '中国語（簡体字）に切り替え' : '日本語に切り替え');
  }
  const menuButton = $('.mobile-menu');
  if (menuButton) menuButton.setAttribute('aria-label', state.locale === 'ja' ? 'ナビゲーションを開く' : '展开导航');
  const dropzone = $('#dropzone');
  if (dropzone) dropzone.setAttribute('aria-label', state.locale === 'ja' ? 'PDFをアップロードまたはドラッグ' : '上传或拖入 PDF');
  document.querySelectorAll('[data-retry]').forEach(button => { button.setAttribute('aria-label', state.locale === 'ja' ? '資料を再構築' : '重新索引'); button.title = state.locale === 'ja' ? '再構築' : '重新索引'; });
  document.querySelectorAll('[data-delete]').forEach(button => { button.setAttribute('aria-label', state.locale === 'ja' ? '資料を削除' : '删除'); button.title = state.locale === 'ja' ? '削除' : '删除'; });
}

function toast(message, error = false) {
  if (state.locale === 'ja') message = localized(message);
  const node = $('#toast');
  node.textContent = message;
  node.className = `show ${error ? 'error' : ''}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.className = '', 6500);
}

async function api(path, options = {}) {
  const opts = {...options};
  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers = {'Content-Type':'application/json', ...opts.headers};
    opts.body = JSON.stringify(opts.body);
  }
  let response;
  try { response = await fetch(`/api${path}`, opts); }
  catch { throw new Error('无法连接本地服务，请检查应用是否正在运行。'); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : `请求失败（${response.status}）`);
  return data;
}

function statusBadge(doc) {
  const status = doc.needs_reindex ? 'stale' : doc.status;
  const labels = state.locale === 'ja'
    ? {queued:'処理待ち', parsing:'解析中', embedding:state.settings.mode === 'api' ? 'ベクトル化中' : 'インデックス作成中', ready:'準備完了', error:'処理失敗', stale:'再構築が必要'}
    : {queued:'等待处理', parsing:'解析中', embedding:state.settings.mode === 'api' ? '向量化中' : '建立索引', ready:'已就绪', error:'处理失败', stale:'待重建'};
  return `<span class="badge ${status}">${status === 'ready' ? icon('check') : ['queued','parsing','embedding'].includes(status) ? '<i class="spinner"></i>' : ''}${labels[status] || esc(status)}</span>`;
}

function fileIcon() { return `<span class="pdf-icon">${icon('files')}<b>PDF</b></span>`; }
function sizeLabel(bytes) { return bytes < 1048576 ? `${Math.max(1, Math.round(bytes/1024))} KB` : `${(bytes/1048576).toFixed(1)} MB`; }

function shell() {
  $('#app').innerHTML = `<aside class="sidebar" id="sidebar">
    <a class="brand" href="#" data-view="chat"><span class="brand-mark">K</span><span>Knowbase<span class="brand-sub">企业知识助手</span></span></a>
    <div class="workspace"><span class="workspace-avatar">企</span><span>企业工作空间<small>本地版本 · Phase 01</small></span>${icon('lock')}</div>
    <button class="new-chat" data-action="new-chat">${icon('plus')}发起新问答<span>↵</span></button>
    <p class="nav-label">工作空间</p>
    <nav aria-label="主导航">
      <button data-view="chat" class="nav-item active">${icon('chat')}知识问答</button>
      <button data-view="documents" class="nav-item">${icon('book')}文档知识库<span id="nav-doc-count" class="nav-count">0</span></button>
      <button data-view="settings" class="nav-item">${icon('settings')}模型设置</button>
    </nav>
    <div class="recent"><p class="nav-label">本次问答</p><div id="recent-list"><p class="muted recent-empty">你的问题会显示在这里</p></div></div>
    <div class="sidebar-bottom"><div class="storage-line">${icon('lock')}<span>文件保存在本机</span></div><p>API 模式下，相关文本将发送到<br>你配置的模型服务。</p><div class="local-user"><span>本</span><div>本地用户<small>个人工作环境</small></div><b>v0.2</b></div></div>
  </aside>
  <div class="workspace-main"><header class="topbar"><div class="breadcrumb"><button class="icon-btn mobile-menu" data-action="menu" aria-label="展开导航">${icon('menu')}</button><span>工作空间</span>${icon('chevron')}<strong id="view-title">知识问答</strong></div><div class="topbar-actions"><button class="locale-toggle" data-action="toggle-locale" aria-label="切换界面语言"></button><button class="mode-pill" data-view="settings" id="mode-label"></button></div></header>
    <main id="main"></main>
  </div>
  <input type="file" accept=".pdf,application/pdf" multiple id="file-input" hidden>
  <dialog id="preview-dialog" aria-labelledby="preview-title"></dialog>
  <dialog id="delete-dialog" aria-labelledby="delete-title"></dialog>`;
  $('#file-input').addEventListener('change', event => {uploadFiles(event.target.files); event.target.value='';});
  renderView();
}

function updateChrome() {
  $('#nav-doc-count').textContent = state.docs.length;
  $('#mode-label').innerHTML = `${icon(state.settings.mode === 'api' ? 'spark' : 'search')}<span>${state.locale === 'ja' ? (state.settings.mode === 'api' ? 'AI質問応答モード' : '原文検索モード') : (state.settings.mode === 'api' ? 'AI 问答模式' : '原文检索模式')}</span>${icon('down')}`;
  $('#view-title').textContent = {chat:'知识问答', documents:'文档知识库', settings:'模型设置'}[state.view];
  document.querySelectorAll('.nav-item').forEach(node => node.classList.toggle('active', node.dataset.view === state.view));
  $('#recent-list').innerHTML = state.messages.length ? state.messages.slice(-5).reverse().map(message => `<button class="recent-item" data-message="${message.id}">${icon('chat')}<span>${esc(message.question)}</span></button>`).join('') : `<p class="muted recent-empty">${state.locale === 'ja' ? '質問履歴がここに表示されます' : '你的问题会显示在这里'}</p>`;
}

function renderView() {
  updateChrome();
  $('#main').className = `view-${state.view}`;
  if (state.view === 'chat') renderChat();
  else if (state.view === 'documents') renderDocuments();
  else renderSettings();
  applyLocale();
}

function renderChat() {
  $('#main').innerHTML = `<div class="chat-layout"><section class="chat-workspace">
    <div class="chat-heading"><div><h1>知识问答 <span class="tiny-tag">KNOWLEDGE AI</span></h1><p>从你的企业文档中，找到有据可查的答案。</p></div><button class="button secondary compact" data-action="upload">${icon('plus')}添加文档</button></div>
    <div id="chat-content" class="chat-content" aria-live="polite"></div>
    <div class="composer-area"><form id="question-form" class="composer"><label for="question" class="sr-only">向知识库提问</label><textarea id="question" placeholder="向知识库提问，例如：员工年假如何申请？" rows="2" maxlength="2000">${esc(state.draft)}</textarea><div class="composer-bottom"><div class="scope-control">${icon('book')}<label class="sr-only" for="scope">检索范围</label><select id="scope" ${state.busy ? 'disabled' : ''}></select></div><div class="send-controls"><span>${state.locale === 'ja' ? 'Enter 送信' : 'Enter 发送'}</span><button type="submit" class="send-button" aria-label="${state.locale === 'ja' ? '質問を送信' : '发送问题'}" ${state.busy ? 'disabled' : ''}>${state.busy ? '<i class="spinner"></i>' : icon('arrow')}</button></div></div></form><p class="composer-note">${icon('lock')}${state.locale === 'ja' ? '選択した資料に基づく回答 · 引用をクリックして原文を確認' : '基于所选文档回答 · 点击引用核对原文'}</p></div>
    </section><aside class="knowledge-rail" id="knowledge-rail"></aside></div>`;
  renderChatContent(); renderRail(); updateScope();
  $('#question-form').addEventListener('submit', event => {event.preventDefault(); askQuestion();});
  $('#question').addEventListener('input', event => state.draft = event.target.value);
  $('#question').addEventListener('keydown', event => {if(event.key === 'Enter' && !event.shiftKey && !event.isComposing) {event.preventDefault(); askQuestion();}});
  $('#scope').addEventListener('change', event => state.selected = event.target.value);
  applyLocale();
}

function updateScope() {
  if (!$('#scope')) return;
  if (state.selected && !readyDocs().some(doc => doc.id === state.selected)) state.selected='';
  $('#scope').innerHTML = `<option value="">全部就绪文档 (${readyDocs().length})</option>` + readyDocs().map(doc => `<option value="${doc.id}" ${state.selected === doc.id ? 'selected' : ''}>${esc(doc.name)}</option>`).join('');
  applyLocale();
}

function renderChatContent() {
  const container = $('#chat-content');
  if (!container) return;
  if (!state.messages.length) {
    container.innerHTML = `<div class="welcome"><div class="welcome-symbol">${icon('spark')}</div><p class="eyebrow">让知识，成为答案</p><h2>今天，想了解什么？</h2><p class="welcome-copy">上传团队文档，提问业务问题。<br>每个答案，都有原文可循。</p>
      <div class="start-cards"><button class="start-card" data-action="upload"><span class="card-symbol blue">${icon('upload')}</span><strong>上传你的第一份文档</strong><span>制度、手册、项目资料 · PDF</span><i>${icon('chevron')}</i></button><button class="start-card" data-action="sample"><span class="card-symbol amber">${icon('book')}</span><strong>用演示文档体验</strong><span>员工手册 · 3 页示例内容</span><i>${icon('chevron')}</i></button></div>
      <div class="try-questions"><span>试着问问</span><button data-prompt="员工年假如何申请？">员工年假如何申请？${icon('chevron')}</button><button data-prompt="差旅报销需要哪些材料？">差旅报销需要哪些材料？${icon('chevron')}</button></div>
    </div>`;
    return;
  }
  container.innerHTML = `<div class="messages">${state.messages.map(message => `<article class="exchange" id="message-${message.id}"><div class="user-question"><span class="user-avatar">${state.locale === 'ja' ? '私' : '我'}</span><h2>${esc(message.question)}</h2></div><div class="assistant-answer"><span class="ai-avatar">${icon('spark')}</span><div class="answer-body"><div class="answer-byline">Knowbase <span>${message.loading ? (state.locale === 'ja' ? 'ドキュメントを検索しています' : '正在检索文档') : message.mode === 'api' ? (state.locale === 'ja' ? 'AI回答' : 'AI 回答') : (state.locale === 'ja' ? '原文検索' : '原文检索')}</span></div>${message.loading ? `<div class="thinking"><i></i><i></i><i></i><span>${state.locale === 'ja' ? '関連情報を検索しています…' : '正在查找相关内容…'}</span></div>` : message.error ? `<div class="inline-error">${esc(message.error)}<button class="text-button" data-retry-question="${message.id}">${state.locale === 'ja' ? 'もう一度質問' : '重新提问'}</button></div>` : `<div class="answer-text">${answerHTML(message)}</div>${message.sources.length ? `<div class="answer-sources">${message.sources.map(source => `<button class="citation-card" data-source="${message.id}:${source.number}"><b>${source.number}</b><span>${esc(source.name)}<small>${state.locale === 'ja' ? `PDF ${source.page}ページ` : `PDF 第 ${source.page} 页`}</small></span>${icon('link')}</button>`).join('')}</div>` : ''}${metricsHTML(message)}<div class="answer-footer"><span>${message.refused ? (state.locale === 'ja' ? '引用できる回答が見つかりません' : '未找到可引用的答案') : (state.locale === 'ja' ? `${message.sources.length}件の引用 · ${(message.elapsed_ms/1000).toFixed(1)}秒` : `${message.sources.length} 个引用 · ${(message.elapsed_ms/1000).toFixed(1)} 秒`)}</span><button class="icon-btn" data-copy="${message.id}" aria-label="${state.locale === 'ja' ? '回答をコピー' : '复制回答'}">${icon('copy')}</button></div>`}</div></div></article>`).join('')}</div>`;
  container.scrollTop = container.scrollHeight;
}

function answerHTML(message) {
  return esc(message.answer).replace(/\[(\d+)\]/g, (match, number) => message.sources.some(source => source.number === Number(number)) ? `<button class="inline-citation" data-source="${message.id}:${number}" aria-label="${state.locale === 'ja' ? '引用を表示 ' : '查看引用 '}${number}">${number}</button>` : match);
}

function renderRail() {
  const rail = $('#knowledge-rail');
  if (!rail) return;
  const last = [...state.messages].reverse().find(message => message.sources?.length);
  if (state.source) {
    const source = state.source;
    rail.innerHTML = `<div class="rail-title"><h2>引用来源</h2><button class="icon-btn" data-action="close-source" aria-label="返回文档列表">${icon('close')}</button></div><div class="source-file">${fileIcon()}<strong>${esc(source.name)}</strong></div><div class="source-meta"><span>${state.locale === 'ja' ? `PDF ${source.page}ページ` : `PDF 第 ${source.page} 页`}</span><span>引用 ${source.number}</span></div><p class="nav-label">原文片段</p><blockquote class="source-quote">${esc(source.text)}</blockquote><a class="button primary full" href="${esc(source.url)}" target="_blank" rel="noopener">在 PDF 中查看${icon('link')}</a><p class="rail-note">页码对应 PDF 的实际页序。请结合原文上下文核对回答。</p>`;
    applyLocale();
    return;
  }
  rail.innerHTML = `<div class="rail-title"><h2>我的知识库</h2><button class="icon-btn" data-view="documents" aria-label="管理文档">${icon('settings')}</button></div><div class="rail-stats"><div><strong>${readyDocs().length}<span>份</span></strong><small>就绪文档</small></div><div><strong>${readyDocs().reduce((n,doc) => n + doc.chunk_count, 0)}<span>个</span></strong><small>知识片段</small></div></div><div class="rail-section-title"><span>文档来源</span><button class="text-button" data-action="upload">${icon('plus')}添加</button></div>
    <div class="rail-docs">${state.docs.length ? state.docs.slice(0,6).map(doc => `<button class="rail-doc" data-preview="${doc.id}">${fileIcon()}<span><strong>${esc(doc.name)}</strong><small>${doc.pages ? (state.locale === 'ja' ? `${doc.pages}ページ · ` : `${doc.pages} 页 · `) : ''}${sizeLabel(doc.size)}</small>${statusBadge(doc)}</span></button>`).join('') : `<div class="rail-empty">${icon('files')}<strong>知识库还没有文档</strong><p>添加 PDF 后，即可开始<br>检索与问答。</p><button class="button secondary" data-action="upload">${icon('upload')}上传 PDF</button></div>`}</div>
    ${last ? `<button class="rail-last-source text-button" data-source="${last.id}:${last.sources[0].number}">查看最近回答的引用${icon('chevron')}</button>` : ''}
    <div class="how-it-works"><p class="nav-label">一份文档，如何成为答案</p><ol><li><span>1</span><div>解析文档<small>提取文字，保留页码</small></div></li><li><span>2</span><div>${state.settings.mode === 'api' ? '语义检索' : '检索相关内容'}<small>${state.settings.mode === 'api' ? '找到问题相关的知识片段' : '配置模型后启用语义检索'}</small></div></li><li><span>3</span><div>带着依据回答<small>点击引用，回到原文</small></div></li></ol></div>
    ${state.settings.mode === 'local' ? `<div class="connect-card">${icon('spark')}<strong>连接你的 AI 模型</strong><p>启用语义检索和 AI 生成回答。</p><button class="text-button" data-view="settings">配置模型${icon('chevron')}</button></div>` : ''}`;
  applyLocale();
}

function renderDocuments() {
  $('#main').innerHTML = `<div class="page-wrap"><div class="page-heading"><div><p class="eyebrow">YOUR KNOWLEDGE, CONNECTED</p><h1>文档知识库</h1><p>${state.locale === 'ja' ? '散らばったPDFを、チームで検索できる知識に変えます。' : '把分散的 PDF，变成团队可检索的知识。'}</p></div><button class="button primary" data-action="upload">${icon('plus')}${state.locale === 'ja' ? '資料をアップロード' : '上传文档'}</button></div>
    <div class="dropzone" id="dropzone" tabindex="0" role="button" aria-label="${state.locale === 'ja' ? 'PDFをアップロードまたはドラッグ' : '上传或拖入 PDF'}"><span class="drop-icon">${icon('upload')}</span><div><strong>${state.locale === 'ja' ? 'PDFをドラッグ、または' : '拖入 PDF 文件，或'}<span>${state.locale === 'ja' ? 'クリックして選択' : '点击选择'}</span></strong><p>${state.locale === 'ja' ? '複数アップロード対応 · 1件20MB / 200ページまで · スキャン資料はOCRが必要' : '支持批量上传 · 单份不超过 20 MB / 200 页 · 扫描件需先做 OCR'}</p></div><span class="file-format">PDF</span></div>
    <div class="document-toolbar"><h2>全部文档 <span id="table-count">${state.docs.length}</span></h2><div><button class="text-button" data-action="sample">导入演示文档</button><button class="button secondary compact" data-action="reindex">${icon('refresh')}重建索引</button></div></div>
    <div id="upload-status" aria-live="polite"></div><div id="document-table"></div>
    <div class="document-info">${icon('lock')}文档与索引保存在本机。更换 Embedding 服务或模型后，请重建索引。</div></div>`;
  renderTable();
  const dropzone = $('#dropzone');
  dropzone.addEventListener('click', () => $('#file-input').click());
  dropzone.addEventListener('keydown', event => {if(['Enter',' '].includes(event.key)) {event.preventDefault(); $('#file-input').click();}});
  for (const name of ['dragenter','dragover']) dropzone.addEventListener(name, event => {event.preventDefault(); dropzone.classList.add('dragging');});
  for (const name of ['dragleave','drop']) dropzone.addEventListener(name, event => {event.preventDefault(); dropzone.classList.remove('dragging'); if(name === 'drop') uploadFiles(event.dataTransfer.files);});
  applyLocale();
}

function renderTable() {
  if (!$('#document-table')) return;
  $('#table-count').textContent = state.docs.length;
  $('#document-table').innerHTML = state.docs.length ? `<div class="table-scroll"><table><thead><tr><th>文档名称</th><th>状态</th><th>页数 / 片段</th><th>添加时间</th><th><span class="sr-only">操作</span></th></tr></thead><tbody>${state.docs.map(doc => `<tr><td><button class="table-file" data-preview="${doc.id}">${fileIcon()}<span><strong>${esc(doc.name)}</strong><small>${sizeLabel(doc.size)}</small></span></button>${doc.error || doc.warning ? `<p class="doc-error ${doc.error ? '' : 'warning'}">${esc(doc.error || doc.warning)}</p>` : ''}</td><td>${statusBadge(doc)}</td><td class="cell-muted">${doc.pages || '—'} / ${doc.chunk_count || '—'}</td><td class="cell-muted">${new Date(doc.created_at).toLocaleDateString(state.locale === 'ja' ? 'ja-JP' : 'zh-CN')}</td><td><div class="row-actions">${['error','ready','stale'].includes(doc.status) ? `<button class="icon-btn" data-retry="${doc.id}" aria-label="重新索引 ${esc(doc.name)}" title="重新索引">${icon('refresh')}</button><button class="icon-btn danger" data-delete="${doc.id}" aria-label="删除 ${esc(doc.name)}" title="删除">${icon('trash')}</button>` : `<span class="muted">${state.locale === 'ja' ? '処理中' : '处理中'}</span>`}</div></td></tr>`).join('')}</tbody></table></div>` : `<div class="table-empty">${icon('book')}<h3>从第一份文档开始</h3><p>上传企业资料，或导入演示文档体验完整流程。</p><button class="button secondary" data-action="sample">导入演示文档${icon('chevron')}</button></div>`;
  applyLocale();
}

function renderSettings() {
  const config = state.settings;
  $('#main').innerHTML = `<div class="page-wrap settings-wrap"><div class="page-heading"><div><p class="eyebrow">MODEL CONNECTION</p><h1>模型设置</h1><p>${state.locale === 'ja' ? 'OpenAI互換サービスに接続し、回答モデルとEmbeddingモデルを選択します。' : '连接兼容 OpenAI 的服务，自由选择回答与 Embedding 模型。'}</p></div></div>
    <section class="settings-section language-section"><div class="section-heading"><span>00</span><div><h2>界面语言</h2><p>选择应用界面和提示信息的语言。</p></div></div><div class="language-options"><button type="button" class="language-option ${state.locale === 'zh' ? 'selected' : ''}" data-locale="zh">简体中文</button><button type="button" class="language-option ${state.locale === 'ja' ? 'selected' : ''}" data-locale="ja">日本語</button></div></section>
    <form id="settings-form"><section class="settings-section"><div class="section-heading"><span>01</span><div><h2>选择工作模式</h2><p>暂时没有 API？也可以先用原文检索。</p></div></div><div class="mode-options"><label class="mode-option"><input type="radio" name="mode" value="api" ${config.mode === 'api' ? 'checked' : ''}><span class="card-symbol blue">${icon('spark')}</span><strong>AI 问答</strong><small>语义向量检索 + 基于原文生成回答</small></label><label class="mode-option"><input type="radio" name="mode" value="local" ${config.mode === 'local' ? 'checked' : ''}><span class="card-symbol gray">${icon('search')}</span><strong>原文检索</strong><small>本地关键词匹配，直接返回原文片段</small></label></div></section>
    <section class="settings-section"><div class="section-heading"><span>02</span><div><h2>模型服务</h2><p>回答和 Embedding 使用同一个服务地址与密钥。</p></div></div><div class="field"><label for="base-url">API 服务地址 <span>Base URL</span></label><input id="base-url" name="base_url" type="url" required value="${esc(config.base_url)}" placeholder="https://api.openai.com/v1"><small>填写 API 根路径，通常以 /v1 结尾。</small></div><div class="field"><label for="api-key">API 密钥 <span>API Key</span></label><input id="api-key" name="api_key" type="password" autocomplete="new-password" placeholder="${config.has_key ? '密钥已配置，留空保留' : '输入密钥；无鉴权的本机服务可留空'}"><small>界面输入的密钥仅保留在服务端内存中，重启后需重新输入。</small>${config.has_key ? '<label class="checkbox-label"><input type="checkbox" name="clear_key">清除已配置的密钥</label>' : ''}</div><div class="field-grid"><div class="field"><label for="chat-model">回答模型</label><input id="chat-model" name="chat_model" required value="${esc(config.chat_model)}" placeholder="gpt-4o-mini"></div><div class="field"><label for="embedding-model">Embedding 模型</label><input id="embedding-model" name="embedding_model" required value="${esc(config.embedding_model)}" placeholder="text-embedding-3-small"></div></div></section>
    <section class="settings-section"><div class="section-heading"><span>03</span><div><h2>检索设置</h2><p>更换 Embedding 配置后，已有文档需要重建索引。</p></div></div><div class="field-grid"><div class="field"><label for="top-k">最多检索片段 <span>Top K</span></label><input id="top-k" name="top_k" type="number" min="1" max="50" required value="${config.top_k}"></div><div class="field"><label for="min-score">最低语义相似度</label><input id="min-score" name="min_score" type="number" min="0" max="1" step="0.01" required value="${config.min_score}"><small>仅用于 AI 模式，需根据实际模型调整；不代表回答可信度。</small></div></div><div class="field-grid"><div class="field"><label for="chunk-size">${state.locale === 'ja' ? 'チャンクサイズ（文字数）' : '分块大小（字符数）'}</label><input id="chunk-size" name="chunk_size" type="number" min="64" max="8000" required value="${config.chunk_size}"></div><div class="field"><label for="chunk-overlap">${state.locale === 'ja' ? '重複する文字数' : '重叠字符数'}</label><input id="chunk-overlap" name="chunk_overlap" type="number" min="0" max="2000" required value="${config.chunk_overlap}"></div></div><div class="field"><label for="search-mode">${state.locale === 'ja' ? '検索方式' : '检索方式'}</label><select id="search-mode" name="search_mode"><option value="exact" ${config.search_mode === 'exact' ? 'selected' : ''}>${state.locale === 'ja' ? '完全検索（Exact）' : '精确检索（Exact）'}</option><option value="hnsw" ${config.search_mode === 'hnsw' ? 'selected' : ''}>HNSW · pgvector</option></select><small>${state.locale === 'ja' ? 'チャンク設定を変えた後は再インデックスが必要です。HNSWはpgvectorと2,000次元以下のAPIベクトルを使用します。' : '调整分块后需要重建索引。HNSW 需使用 pgvector 和不超过 2,000 维的 API 向量。'}</small></div></section>
    <div class="settings-notice">${icon('lock')}${state.locale === 'ja' ? 'AIモードでは文書テキストをEmbeddingに使用し、検索チャンクと質問を上記のモデルサービスへ送信します。' : 'AI 模式会将文档文本用于 Embedding，并将检索到的片段和问题发送到上方配置的模型服务。'}</div><div id="settings-feedback" role="status"></div><div class="settings-actions"><button type="button" class="button secondary" id="test-settings">${icon('link')}${state.locale === 'ja' ? '接続テスト' : '测试连接'}</button><button type="submit" class="button primary" id="save-settings">${state.locale === 'ja' ? '設定を保存' : '保存配置'}${icon('check')}</button></div><p class="settings-footnote">${state.locale === 'ja' ? '接続テストではEmbeddingと回答APIを1回ずつ呼び出すため、料金が発生する場合があります。' : '测试连接会调用一次 Embedding 和一次回答接口，可能产生 API 费用。'}</p></form></div>`;
  const ja = state.locale === 'ja';
  $('#search-mode').closest('.settings-section').insertAdjacentHTML('beforebegin', `<section class="settings-section"><div class="section-heading"><span>02b</span><div><h2>${ja ? '回答の根拠検証' : '回答依据验证'}</h2><p>${ja ? '回答モデルとは別の検証モデルを指定できます。' : '可以使用与回答模型不同的验证模型。'}</p></div></div><div class="field-grid"><div class="field"><label for="verifier-model">${ja ? '検証モデル' : 'Verifier 模型'}</label><input id="verifier-model" name="verifier_model" maxlength="160" value="${esc(config.verifier_model || '')}" placeholder="${ja ? '空欄なら回答モデルを使用' : '留空则使用回答模型'}"></div><div class="field"><label for="verification-mode">${ja ? '検証モード' : 'Verification 模式'}</label><select id="verification-mode" name="verification_mode">${['off','fast','strict'].map(mode => `<option value="${mode}" ${(config.verification_mode || 'strict') === mode ? 'selected' : ''}>${mode}</option>`).join('')}</select></div></div><p>${ja ? 'off：構造と引用番号を確認。fast：原文との一致も確認。strict：追加のモデル呼び出しで各主張の根拠を確認します。off / fast では意味的な裏付けは未検証です。' : 'off：检查结构和来源编号。fast：再检查摘录是否来自原文。strict：追加模型调用，检查每项断言是否有依据。off / fast 的语义依据未经验证。'}</p></section>`);
  $('#settings-form').addEventListener('submit', event => {event.preventDefault(); submitSettings(false);});
  $('#test-settings').addEventListener('click', () => submitSettings(true));
  applyLocale();
}

async function submitSettings(test) {
  const form = $('#settings-form');
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form));
  data.chunk_size = Number(data.chunk_size); data.chunk_overlap = Number(data.chunk_overlap); data.top_k = Number(data.top_k); data.min_score = Number(data.min_score); data.clear_key = data.clear_key === 'on';
  if (data.chunk_overlap >= data.chunk_size) return toast(state.locale === 'ja' ? '重複文字数はチャンクサイズより小さくしてください。' : '重叠字符数必须小于分块大小。', true);
  const feedback = $('#settings-feedback');
  const buttons = [...form.querySelectorAll('button')];
  buttons.forEach(button => button.disabled = true);
  feedback.innerHTML = `<p class="feedback">${test ? '<i class="spinner"></i>正在测试模型服务…' : '正在保存…'}</p>`;
  try {
    const result = await api(test ? '/settings/test' : '/settings', {method:test ? 'POST' : 'PUT', body:data});
    if (!test) {state.settings = result; $('#api-key').value=''; $('#api-key').placeholder = result.has_key ? '密钥已配置，留空保留' : '输入 API 密钥'; await refreshDocs(); updateChrome();}
    feedback.innerHTML = `<p class="feedback success">${icon('check')}${esc(test ? result.message : '配置已保存。' + (state.docs.some(doc => doc.needs_reindex) ? '请前往文档知识库重建索引。' : ''))}</p>`;
  } catch(error) {feedback.innerHTML = `<p class="feedback failure">${esc(error.message)}</p>`;}
  finally {buttons.forEach(button => button.disabled = false);}
}

async function refreshDocs() {
  state.docs = (await api('/documents')).documents;
  updateChrome(); updateScope(); renderTable(); renderRail();
  clearTimeout(pollTimer);
  if (state.docs.some(doc => ['queued','parsing','embedding'].includes(doc.status))) pollTimer = setTimeout(() => refreshDocs().catch(error => toast(error.message, true)), 2000);
}

async function uploadFiles(fileList) {
  if (state.uploading) return toast('上一批文件仍在上传，请稍候。');
  const files = [...fileList];
  if (!files.length) return;
  state.uploading = true;
  let succeeded=0;
  for (const file of files) {
    if (!file.name.toLowerCase().endsWith('.pdf') || file.size > 20*1024*1024) {toast(`${file.name}：仅支持不超过 20 MB 的 PDF。`, true); continue;}
    const body = new FormData(); body.append('file',file);
    try {
      toast(`正在上传 ${file.name}…`);
      const result = await api('/documents', {method:'POST', body});
      succeeded++;
      toast(result.duplicate ? `${file.name} 已在知识库中。` : `${file.name} 上传成功，正在处理。`);
      await refreshDocs();
    } catch(error) {toast(`${file.name}：${error.message}`, true);}
  }
  state.uploading=false;
  if ($('#upload-status')) $('#upload-status').innerHTML = `<p class="upload-result">本批 ${files.length} 份文件：已接收 ${succeeded} 份，未接收 ${files.length-succeeded} 份。处理结果见下表。</p>`;
}

async function loadSample() {
  try {const result=await api('/documents/sample', {method:'POST'}); toast(result.duplicate ? '演示文档已在知识库中。' : '已添加演示员工手册，正在建立索引。'); await refreshDocs();}
  catch(error) {toast(error.message,true);}
}

async function askQuestion() {
  const question = state.draft.trim();
  if (!question || state.busy) return;
  if (!readyDocs().length) {toast('请先上传或导入文档，等待索引就绪后再提问。'); return;}
  state.busy=true; state.draft=''; state.source=null;
  const message={id:Date.now().toString(36), question, loading:true, sources:[]};
  state.messages.push(message); renderChat(); updateChrome();
  try {Object.assign(message, await api('/chat', {method:'POST', body:{question, language:state.locale, document_ids:state.selected ? [state.selected] : []}}));}
  catch(error) {message.error=error.message;}
  finally {message.loading=false; state.busy=false; if(state.view === 'chat') renderChat(); updateChrome(); await refreshDocs().catch(error => toast(error.message,true));}
}

async function previewDocument(id) {
  try {
    const data = await api(`/documents/${id}/chunks`);
    const dialog = $('#preview-dialog');
    dialog.innerHTML = `<div class="dialog-header"><div><p class="eyebrow">DOCUMENT PREVIEW</p><h2 id="preview-title">${esc(data.document.name)}</h2></div><button class="icon-btn" data-action="close-dialog" aria-label="关闭预览">${icon('close')}</button></div><div class="dialog-meta">${data.document.pages} 页 · ${data.chunks.length} 个知识片段 <a class="text-button" href="/api/documents/${id}/file" target="_blank" rel="noopener">打开 PDF${icon('link')}</a></div><div class="preview-chunks">${data.chunks.length ? data.chunks.map(chunk => `<section><a class="page-label" href="/api/documents/${id}/file#page=${chunk.page}" target="_blank" rel="noopener">PDF 第 ${chunk.page} 页${icon('link')}</a><p>${esc(chunk.text)}</p></section>`).join('') : `<p class="muted">${esc(data.document.error || '文档尚未处理完成。')}</p>`}</div>`;
    dialog.showModal();
  } catch(error) {toast(error.message,true);}
}

function showSource(value) {
  const [id, number] = value.split(':');
  state.source=state.messages.find(message => message.id === id)?.sources.find(source => source.number === Number(number));
  renderRail();
  if (window.innerWidth < 1080) $('#knowledge-rail').classList.add('source-open');
}

document.addEventListener('click', async event => {
  const button = event.target.closest('button,a[data-view]');
  if (!button) return;
  if (button.dataset.view) {event.preventDefault(); state.view=button.dataset.view; $('#sidebar').classList.remove('open'); renderView(); return;}
  const action=button.dataset.action;
  if (action === 'upload') $('#file-input').click();
  if (action === 'sample') loadSample();
  if (action === 'menu') $('#sidebar').classList.toggle('open');
  if (action === 'toggle-locale') {state.locale = state.locale === 'ja' ? 'zh' : 'ja'; localStorage.setItem('knowbase-locale', state.locale); shell();}
  if (button.dataset.locale) {state.locale = button.dataset.locale; localStorage.setItem('knowbase-locale', state.locale); shell();}
  if (action === 'new-chat') {if(state.busy) return toast('请等待当前回答完成。'); state.messages=[]; state.source=null; state.draft=''; state.view='chat'; renderView(); $('#sidebar').classList.remove('open'); $('#question').focus();}
  if (action === 'close-source') {state.source=null; $('#knowledge-rail').classList.remove('source-open'); renderRail();}
  if (action === 'close-dialog') button.closest('dialog').close();
  if (action === 'reindex') {
    button.disabled=true;
    try {const result=await api('/documents/reindex',{method:'POST'}); toast(`已安排 ${result.queued} 份文档重新建立索引。`); await refreshDocs();} catch(error) {toast(error.message,true);} finally {button.disabled=false;}
  }
  if (button.dataset.prompt) {state.draft=button.dataset.prompt; $('#question').value=state.draft; $('#question').focus();}
  if (button.dataset.source) showSource(button.dataset.source);
  if (button.dataset.preview) previewDocument(button.dataset.preview);
  if (button.dataset.message) {state.view='chat'; renderView(); $(`#message-${button.dataset.message}`)?.scrollIntoView({behavior:'smooth'});}
  if (button.dataset.copy) {try {await navigator.clipboard.writeText(state.messages.find(message => message.id === button.dataset.copy).answer); toast('回答已复制。');} catch {toast('无法访问剪贴板，请选中文字复制。',true);}}
  if (button.dataset.retryQuestion) {state.draft=state.messages.find(message => message.id === button.dataset.retryQuestion).question; askQuestion();}
  if (button.dataset.retry) {try {await api(`/documents/${button.dataset.retry}/retry`,{method:'POST'}); await refreshDocs(); toast('已安排重新处理。');} catch(error) {toast(error.message,true);}}
  if (button.dataset.delete) {
    const id=button.dataset.delete; const doc=state.docs.find(item => item.id === id);
    const dialog=$('#delete-dialog');
    dialog.innerHTML=`<div class="dialog-header"><h2 id="delete-title">删除这份文档？</h2><button class="icon-btn" data-action="close-dialog" aria-label="取消">${icon('close')}</button></div><p class="delete-copy">${esc(doc.name)} 的原文件与知识索引将从本应用中删除。</p><div class="settings-actions"><button class="button secondary" data-action="close-dialog">取消</button><button class="button destructive" id="confirm-delete">删除文档</button></div>`;
    dialog.showModal();
    $('#confirm-delete').onclick=async () => {try {await api(`/documents/${id}`,{method:'DELETE'}); dialog.close(); await refreshDocs(); toast('文档已删除。');} catch(error) {toast(error.message,true);}};
  }
});

async function init() {
  try {const [config, docs]=await Promise.all([api('/settings'),api('/documents')]); state.settings=config; state.docs=docs.documents; shell(); await refreshDocs();}
  catch(error) {$('#app').innerHTML=`<div class="boot boot-error"><h1>暂时无法连接知识库</h1><p>${esc(error.message)}</p><button class="button primary" id="retry-connect">重新连接</button></div>`; $('#retry-connect').onclick=init;}
}
init();



function metricsHTML(message) {
  const m = message.metrics;
  if (!m) return '';
  const ja = state.locale === 'ja';
  const labels = {query_embedding:ja?'質問のEmbedding':'问题向量化', retrieval:ja?'検索':'检索', generation:ja?'回答生成':'回答生成', verification:ja?'根拠検証':'依据校验'};
  const phases = Object.entries(labels).filter(([key]) => m.timings_ms?.[key] !== undefined).map(([key,label]) => `${label}: ${(m.timings_ms[key]/1000).toFixed(3)}s`).join(' · ');
  const usage = m.token_usage || {};
  const cost = m.cost_usd == null ? (ja?'費用不明':'费用未知') : `USD ${Number(m.cost_usd).toFixed(6)}`;
  const support = message.support?.method === 'quote_match_and_model_entailment' ? `${ja?'根拠検証':'依据校验'} ${message.support.verified_claims}/${message.support.total_claims}` : ['disabled','quote_match_only'].includes(message.support?.method) ? (ja?'意味的な根拠は未検証':'语义依据未经验证') : '';
  const tokens = usage.complete ? `${usage.total_tokens || 0} tokens` : `${usage.total_tokens || 0}+ tokens (${ja?'使用量の一部が不明':'部分用量未知'})`;
  return `<details class="answer-metrics"><summary>${ja?'性能・使用量':'性能与用量'} · ${esc(cost)}${support ? ' · '+esc(support):''}</summary><p>${esc(phases)}</p><p>${esc(tokens)} · ${esc(String(m.attempt_count || 0))} ${ja?'HTTP試行':'次 HTTP 尝试'}</p><small>${ja?'費用は設定した単価による推計です。根拠の自動検証は人による確認を代替しません。':'费用按配置单价估算；自动依据校验不能替代人工核对。'}</small></details>`;
}

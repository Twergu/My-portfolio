/* Agent presentation and chat lifecycle. No task handles or evidence in localStorage. */
'use strict';

const aText = (zh, ja) => state.locale === 'ja' ? ja : zh;
const isAgent = () => state.chatMode === 'agent';
const taskLocked = () => state.busy || Boolean(state.agentTask);

function chatPlaceholder() {
  if (state.agentTask) return aText('补充当前任务所需的信息…', '現在のタスクに必要な情報を入力…');
  return isAgent() ? aText('描述想办理的事，以及已知的日期、金额或条件…', '進めたい業務と、分かっている日付・金額・条件を入力…') : aText('向知识库提问，例如：员工年假如何申请？', 'ナレッジベースに質問：例）年次有給休暇はどのように申請しますか？');
}

function chatModeHTML() {
  return `<div class="chat-mode-row"><div class="chat-mode-switch" role="group" aria-label="${aText('对话模式','会話モード')}">${[['rag',aText('知识问答','ナレッジQ&A'),'chat'],['agent',aText('业务 Agent','業務 Agent'),'spark']].map(([mode,label,symbol]) => `<button type="button" data-chat-mode="${mode}" aria-pressed="${state.chatMode === mode}" ${taskLocked()?'disabled':''}>${icon(symbol)}${label}</button>`).join('')}</div><span class="chat-mode-description">${isAgent()?aText('查规定 · 核对条件 · 整理步骤','規程を検索 · 条件を確認 · 手順を整理'):aText('从文档中获取带引用的回答','資料から引用付きの回答を取得')}</span></div>`;
}

function agentTaskHTML() {
  const task = state.agentTask;
  if (!task) return '';
  return `<div class="agent-task-banner" role="status"><div><strong>${aText('继续当前任务','現在のタスクを続ける')}</strong><p>${aText('请在下方补充信息。文档范围已锁定；任务创建后保留 15 分钟。','下の欄に追加情報を入力してください。検索範囲は固定され、タスクは開始から15分間保持されます。')}</p></div><button type="button" class="text-button" data-action="end-agent-task" ${state.busy?'disabled':''}>${aText('结束任务','タスクを終了')}</button></div>`;
}

function agentWelcomeHTML() {
  const examples = state.locale === 'ja' ? [
    ['備品の購入','備品を3点、各1200円で購入したいです。規程を調べ、合計金額と必要書類を確認してください。'],
    ['研修の手続き','研修の開始日は2026年10月12日です。規程に基づく申請期限と必要書類を確認してください。'],
    ['申請条件の確認','通勤補助の申請条件を確認したいです。判断に必要な情報があれば質問してください。'],
  ] : [
    ['采购申请','我想采购3本办公笔记本，每本1200日元。请查询规定、计算总额，并列出所需材料。'],
    ['培训办理','培训开始日期是2026年10月12日。请按规定计算申请期限，并告诉我需要提交什么。'],
    ['申请条件','帮我确认是否符合通勤补助申请条件；如果缺少个人信息，请先问我。'],
  ];
  return `<div class="welcome agent-welcome"><div class="welcome-symbol">${icon('spark')}</div><p class="eyebrow">${aText('从问题，到办理方案','質問から、業務の進め方へ')}</p><h2>${aText('这次，想办什么事？','どの業務を進めますか？')}</h2><p class="welcome-copy">${aText('结合企业规定与日期、金额计算，核对条件并整理步骤。<br>缺少关键信息时，会先向你确认。','社内規程と日付・金額の計算を組み合わせ、条件と手順を確認します。<br>必要な情報が足りない場合は、先に質問します。')}</p><div class="agent-example-grid">${examples.map(([title,prompt]) => `<button class="agent-example" data-prompt="${esc(prompt)}"><strong>${esc(title)}${icon('chevron')}</strong><span>${esc(prompt)}</span></button>`).join('')}</div><p class="agent-example-note">${aText('示例展示提问方式；实际判断以你有权访问的文档为依据。','質問の例です。実際の判断には、アクセス権のある資料を使用します。')}</p><div class="agent-capabilities"><span>${icon('book')}${aText('知识检索','ナレッジ検索')}</span><span>${icon('clock')}${aText('日期核对','日付の確認')}</span><span>${icon('calculator')}${aText('金额计算','金額の計算')}</span></div></div>`;
}

function applyChatControls() {
  document.querySelectorAll('#scope,#policy-filter,#date-filter,#department-filter,[data-chat-mode]').forEach(node => node.disabled = taskLocked());
  document.querySelectorAll('[data-action="end-agent-task"],[data-retry-question]').forEach(node => node.disabled = state.busy || (Boolean(state.agentTask) && Boolean(node.dataset.retryQuestion)));
  const needsApi = isAgent() && state.settings?.mode !== 'api';
  if ($('#question')) $('#question').disabled = state.busy || needsApi;
  if ($('.send-button')) $('.send-button').disabled = state.busy || needsApi;
  if ($('#agent-api-notice')) $('#agent-api-notice').hidden = !needsApi;
}

function sourceKind(source) { return ['tool','user'].includes(source.kind) ? source.kind : 'document'; }
function sourceLabel(source) {
  if (sourceKind(source) === 'user') return aText('用户提供的信息','ユーザーの申告情報');
  if (sourceKind(source) === 'tool') return source.name === 'calendar' ? aText('日期工具','日付ツール') : source.name === 'calculator' ? aText('计算工具','計算ツール') : aText('工具结果','ツール結果');
  return source.name;
}
function sourceCaption(source) {
  if (sourceKind(source) === 'document') return aText(`PDF 第 ${source.page} 页`, `PDF ${source.page}ページ`);
  if (source.provenance === 'mock') return aText('模拟数据 · 查看假设','模擬データ · 前提を確認');
  return sourceKind(source) === 'user' ? aText('自述 · 尚未经业务系统核实','申告内容 · 業務システムで未確認') : aText('计算结果 · 查看输入与结果','計算結果 · 入力と結果を確認');
}
function sourcePdfUrl(source) {
  if (sourceKind(source) !== 'document' || !source.document_id || !Number.isInteger(source.page) || source.page < 1) return null;
  return `/api/documents/${encodeURIComponent(source.document_id)}/file#page=${source.page}`;
}
function sourceCardsHTML(message) {
  return ['document','tool','user'].map(kind => {
    const sources = (message.sources || []).filter(source => sourceKind(source) === kind);
    if (!sources.length) return '';
    const title = {document:aText('文档依据','資料の根拠'),tool:aText('工具依据','ツールの根拠'),user:aText('用户信息','ユーザー情報')}[kind];
    return `<div class="source-group">${message.kind === 'agent'?`<p class="source-group-title">${title}</p>`:''}<div class="answer-sources">${sources.map(source => `<button class="citation-card source-${kind}" data-source="${message.id}:${source.number}"><b>${source.number}</b><span>${esc(sourceLabel(source))}<small>${esc(sourceCaption(source))}</small></span>${icon(kind === 'document'?'files':kind === 'tool'?'calculator':'user')}</button>`).join('')}</div></div>`;
  }).join('');
}

function sourceRailHTML(source) {
  const kind = sourceKind(source), url = sourcePdfUrl(source);
  const titles = {document:aText('原文片段','原文の抜粋'),tool:aText('工具原始结果','ツールの元の結果'),user:aText('用户原始输入','ユーザーの元の入力')};
  const notes = {document:aText('页码对应 PDF 实际页序，请结合原文上下文核对。','ページ番号はPDFの実際の順序です。原文の文脈と照合してください。'),tool:source.provenance === 'mock'?aText('此结果采用模拟日历，并未确认公司实际节假日、余额或审批情况。','模擬カレンダーによる結果です。実際の会社休日・残日数・承認状況は確認していません。'):aText('计算准确性与业务适用性是两项检查。请核对输入、单位及所引用规定。','計算の正確さと業務への適用は別々に確認します。入力・単位・引用規程を照合してください。'),user:aText('这是用户自述，尚未由业务系统核实。相关判断应保留这一条件。','ユーザーの申告内容であり、業務システムでは未確認です。判断にはこの前提が付きます。')};
  const labels = {operation:aText('操作','操作'),operands:aText('输入数值','入力値'),result:aText('结果','結果'),date:aText('日期','日付'),calendar_days:aText('自然日（含首尾）','暦日（両端を含む）'),working_days:aText('工作日','営業日'),working_dates:aText('工作日期','営業日の日付'),start_date:aText('起始日期','開始日'),end_date:aText('结束日期','終了日'),offset_days:aText('偏移天数','加減日数'),weekday:aText('星期（周一为0）','曜日（月曜=0）'),week_offset:aText('周偏移','週のオフセット'),reference_date:aText('参考日期','基準日'),timezone:aText('时区','タイムゾーン'),rounded:aText('已四舍五入','丸め処理済み')};
  const values = {sum:aText('求和','合計'),subtract:aText('相减','減算'),multiply:aText('相乘','乗算'),divide:aText('相除','除算'),percent_of:aText('百分比计算','割合計算'),date_range:aText('日期区间','期間計算'),date_offset:aText('日期偏移','日付の加減'),next_weekday:aText('指定周的星期','指定した週の曜日')};
  const fields = {...source.metadata?.arguments, ...source.metadata?.result};
  if (source.name === 'calendar') {
    const used = {date_offset:['offset_days'],next_weekday:['week_offset','weekday'],date_range:['end_date']}[fields.operation] || [];
    for (const key of ['offset_days','week_offset','weekday','end_date']) if (!used.includes(key)) delete fields[key];
  }
  const rows = kind === 'tool' ? Object.entries(fields).filter(([key,value]) => labels[key] && value != null).map(([key,value]) => `<div><dt>${labels[key]}</dt><dd class="tool-value">${esc(Array.isArray(value)?value.join(', '):typeof value === 'boolean'?(value?aText('是','はい'):aText('否','いいえ')):values[value] || value)}</dd></div>`).join('') : '';
  return `<div class="rail-title"><h2>${aText('引用依据','引用の根拠')}</h2><button class="icon-btn" data-action="close-source" aria-label="${aText('关闭来源','出典を閉じる')}">${icon('close')}</button></div><div class="source-file">${kind === 'document'?fileIcon():`<span class="source-symbol">${icon(kind === 'user'?'user':'calculator')}</span>`}<strong>${esc(sourceLabel(source))}</strong></div><div class="source-meta"><span>${esc(sourceCaption(source))}</span><span>${aText('引用','引用')} ${source.number}</span></div>${rows?`<dl class="tool-fields">${rows}</dl>`:''}<p class="nav-label">${titles[kind]}</p><blockquote class="source-quote">${esc(source.text)}</blockquote>${url?`<a class="button primary full" href="${esc(url)}" target="_blank" rel="noopener">${aText('在 PDF 中查看','PDFで確認')}${icon('link')}</a>`:''}<p class="rail-note">${notes[kind]}</p>`;
}

function agentStatusLabel(message) {
  if (message.status === 'needs_input' && state.agentTask?.messageId !== message.id) return message.closed?aText('任务已结束','タスク終了'):aText('信息已补充','追加情報を受信済み');
  return ({answered:aText('依据验证通过','根拠検証を通過'),needs_input:aText('等待补充信息','追加情報を待機中'),insufficient_evidence:aText('证据不足','根拠が不足'),unsupported_answer:aText('回答未通过依据验证','回答の根拠を確認できません'),invalid_model_response:aText('模型返回格式异常','モデルの応答形式が不正'),unavailable:aText('当前无法完成','現在は実行できません'),limit_reached:aText('已达到执行上限','実行上限に到達'),error:aText('任务未完成','タスク未完了')})[message.status] || aText('任务结果','タスク結果');
}
function agentFailureText(message) {
  const codes = {
    no_accessible_evidence:aText('所选范围没有可用证据。请检查文档是否就绪，以及当前筛选和访问权限。','選択範囲に利用できる根拠がありません。資料の準備状況・絞り込み・アクセス権を確認してください。'),
    api_required:aText('请在模型设置中启用 API 模式后使用 Agent。','モデル設定でAPIモードを有効にしてからAgentを利用してください。'),
    missing_tool:aText('当前工具无法完成这项任务，请调整任务范围。','現在のツールでは実行できません。タスクの範囲を調整してください。'),
    no_evidence:aText('没有找到足够的政策依据，请补充相关文档或调整问题。','十分な規程の根拠が見つかりません。資料を追加するか質問を変更してください。'),
  };
  return codes[message.failure_code] || (message.status === 'limit_reached'?aText('任务已达到调用或上下文上限，请缩小范围后重新开始。','呼び出し回数またはコンテキストの上限に達しました。範囲を絞って再開してください。'):aText('未能生成通过验证的结果，请检查模型设置或调整问题后重新开始。','検証を通過した結果を生成できませんでした。モデル設定や質問を確認して再開してください。'));
}
function agentTraceHTML(message) {
  const names = {knowledge_search:aText('检索企业规定','社内規程を検索'),calendar:aText('核对日期','日付を確認'),calculator:aText('计算数值','数値を計算')};
  const trace = (message.trace || []).filter(step => ['tool_completed','tool_error','needs_input','answer_clarification','unavailable','limit_reached','error'].includes(step.event));
  const steps = trace.map(step => {
    const ok = step.event === 'tool_completed', tool = step.event.startsWith('tool_');
    const label = tool ? names[step.tool] || aText('调用工具','ツール呼び出し') : ['needs_input','answer_clarification'].includes(step.event)?aText('确认缺失信息','不足情報を確認'):aText('停止当前执行','現在の実行を停止');
    return `<li><span class="trace-marker ${ok?'done':''}">${icon(ok?'check':tool?'close':'chat')}</span><div><strong>${label}</strong><small>${tool?(ok?aText('已完成','完了'):aText('未完成，结果未用作依据','未完了・根拠には使用せず')):aText('等待补充或调整任务','情報の追加またはタスクの調整が必要')}</small></div><span class="trace-step">${aText('步骤','ステップ')} ${step.step}</span></li>`;
  });
  if (message.support?.method === 'quote_match_and_model_entailment') steps.push(`<li><span class="trace-marker ${message.support.all_supported?'done':''}">${icon(message.support.all_supported?'check':'close')}</span><div><strong>${aText('原文与断言依据验证','原文と各主張の根拠を検証')}</strong><small>${message.support.all_supported?aText('全部断言通过检查','すべての主張が検証を通過'):aText('未通过，回答已隐藏','検証未通過・回答は非表示')}</small></div></li>`);
  else if (message.status === 'unsupported_answer') steps.push(`<li><span class="trace-marker">${icon('close')}</span><div><strong>${aText('引用检查未通过','引用の検証に失敗')}</strong><small>${aText('回答已隐藏','回答は非表示')}</small></div></li>`);
  return steps.length?`<details class="agent-trace"><summary>${icon('steps')}${aText('执行记录','実行履歴')}<span>${trace.filter(s => s.event.startsWith('tool_')).length} ${aText('次工具调用','回のツール呼び出し')}</span></summary><ol>${steps.join('')}</ol></details>`:'';
}

function renderMessageHTML(message) {
  const agent = message.kind === 'agent';
  let content;
  if (message.loading) content = `<div class="thinking"><i></i><i></i><i></i><span>${agent?aText('正在处理任务，完成后显示实际执行记录…','タスクを処理しています。完了後に実行履歴を表示します…'):aText('正在查找相关内容…','関連情報を検索しています…')}</span></div>`;
  else if (message.error) content = `<div class="inline-error" role="alert">${esc(message.error)}<button class="text-button" data-retry-question="${message.id}">${agent?aText('重新开始任务','タスクを最初から開始'):aText('重新提问','もう一度質問')}</button></div>`;
  else {
    const isWaiting = agent && message.status === 'needs_input';
    const current = state.agentTask?.messageId === message.id;
    const body = isWaiting ? `<div class="agent-questions"><strong>${aText('还需要确认这些信息','次の情報を教えてください')}</strong><ul class="agent-question-list">${(message.questions || []).map(question => `<li>${esc(question)}</li>`).join('')}</ul><p>${current?aText('请在下方输入框回复，可一次回答所有问题。','下の入力欄から回答してください。まとめて回答できます。'):message.closed?aText('此任务已结束。','このタスクは終了しました。'):aText('已在后续消息中补充。','後続のメッセージで追加済みです。')}</p></div>` : `<div class="answer-text">${message.answer?answerHTML(message):esc(agentFailureText(message))}</div>`;
    const notices = [];
    if (message.evidence_notices?.uses_mock_data) notices.push(aText('包含模拟数据，请结合来源卡片中的假设理解结果。','模擬データを含みます。出典カードに記載の前提を確認してください。'));
    if (message.evidence_notices?.uses_self_report) notices.push(aText('部分依据来自你的输入，尚未经业务系统核实。','一部の根拠はあなたの申告内容であり、業務システムでは未確認です。'));
    content = `${agent?`<span class="agent-status status-${esc(message.status)}">${agentStatusLabel(message)}</span>`:''}${body}${notices.length?`<div class="agent-notices">${notices.map(note => `<p>${icon('info')}${note}</p>`).join('')}</div>`:''}${sourceCardsHTML(message)}${agent?agentTraceHTML(message):''}${metricsHTML(message)}<div class="answer-footer"><span>${agent?agentStatusLabel(message):message.refused?aText('未找到可引用的答案','引用できる回答が見つかりません'):aText(`${(message.sources || []).length} 个引用`,`${(message.sources || []).length}件の引用`)}${Number.isFinite(message.elapsed_ms)?` · ${(message.elapsed_ms/1000).toFixed(1)} ${aText('秒','秒')}`:''}</span>${message.answer?`<button class="icon-btn" data-copy="${message.id}" aria-label="${aText('复制回答','回答をコピー')}">${icon('copy')}</button>`:''}</div>`;
  }
  return `<article class="exchange" id="message-${message.id}"><div class="user-question"><span class="user-avatar">${aText('我','私')}</span><h2>${message.continuation?`<small class="reply-label">${aText('补充信息','追加情報')}</small>`:''}${esc(message.question)}</h2></div><div class="assistant-answer"><span class="ai-avatar">${icon(agent?'steps':'spark')}</span><div class="answer-body"><div class="answer-byline">Knowbase <span>${agent?'Agent':message.mode === 'api'?aText('AI 回答','AI回答'):aText('原文检索','原文検索')}</span></div>${content}</div></div></article>`;
}

function chatRequest(question, task, agent) {
  if (agent && task) return {path:`/agent/${encodeURIComponent(task.id)}/reply`, body:{question}};
  return {path:agent?'/agent':'/chat', body:{question, filters:structuredClone(state.filters || {}), language:state.locale, document_ids:state.selected?[state.selected]:[]}};
}

async function sendChatMessage() {
  const question = state.draft.trim();
  if (!question || state.busy) return;
  if (question.length > 2000) return toast(aText('每条消息最多 2000 个字符，请缩短后再发送。','1回の入力は2000文字以内です。短くして送信してください。'));
  if (!readyDocs().length && !state.agentTask) return toast('请先上传或导入文档，等待索引就绪后再提问。');
  const agent = isAgent(), task = agent ? state.agentTask : null, epoch = state.chatEpoch;
  if (agent && state.settings?.mode !== 'api') return toast(aText('请先配置 API 模型，再使用 Agent。','Agentを利用するには、先にAPIモデルを設定してください。'));
  const request = chatRequest(question, task, agent);
  const message = {id:crypto.randomUUID(),kind:agent?'agent':'rag',mode:state.settings?.mode,question,loading:true,sources:[],continuation:Boolean(task),transcript:[...(task?.transcript || []),question]};
  state.busy=true; state.draft=''; state.source=null;
  state.messages.push(message); renderChat(); updateChrome();
  try {
    const result = await api(request.path,{method:'POST',body:request.body});
    if (epoch !== state.chatEpoch) return;
    Object.assign(message,result);
    message.sources ||= [];
    if (agent) state.agentTask = result.status === 'needs_input' && result.task_id ? {id:result.task_id,messageId:message.id,transcript:message.transcript,documentIds:task?.documentIds || request.body.document_ids,documentNames:task?.documentNames || state.docs.filter(d => request.body.document_ids.includes(d.id)).map(d => d.name)} : null;
  } catch (error) {
    if (epoch !== state.chatEpoch) return;
    message.error = agent && error.status === 404 ? aText('任务已过期、已结束，或所选资料不可访问。请重新开始。','タスクが期限切れ・終了済み、または資料にアクセスできません。最初から開始してください。') : agent && error.status === 409 ? aText('任务仍在执行，或权限、文档、模型配置已变化。请稍后重新开始任务。','実行中、または権限・資料・モデル設定が変更されています。しばらくしてから最初から開始してください。') : localized(error.message);
    if (agent) {state.agentTask=null; state.messages.filter(m => m.status === 'needs_input').forEach(m => m.closed=true);}
  } finally {
    if (epoch === state.chatEpoch) {
      message.loading=false; state.busy=false;
      if (state.auth?.user) {if(state.view === 'chat') renderChat(); updateChrome(); await refreshDocs().catch(error => toast(error.message,true));}
    }
  }
}

async function endAgentTask() {
  if (state.busy) return false;
  const task = state.agentTask, epoch = state.chatEpoch;
  if (!task) return true;
  state.busy=true; applyChatControls();
  try {await api(`/agent/${encodeURIComponent(task.id)}`,{method:'DELETE'});}
  catch (error) {if (![404,401].includes(error.status)) {toast(aText('未能结束任务，请稍后重试。','タスクを終了できませんでした。後でもう一度お試しください。'),true); return false;}}
  finally {if(epoch === state.chatEpoch) {state.busy=false; applyChatControls();}}
  if (epoch !== state.chatEpoch) return false;
  const message = state.messages.find(m => m.id === task.messageId);
  if (message) message.closed=true;
  state.agentTask=null;
  return true;
}

function resetChatIdentity() {
  state.chatEpoch=(state.chatEpoch || 0)+1;
  state.agentTask=null; state.draft=''; state.busy=false; state.filters={}; state.chatMode='rag';
  state.docs=[]; state.messages=[]; state.selected=''; state.source=null;
}

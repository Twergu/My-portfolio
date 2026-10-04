'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const {randomUUID} = require('node:crypto');

const source = readFileSync(join(__dirname, '../../dist/agent.js'), 'utf8');
function fixture(overrides = {}) {
  const elements = new Map();
  const controls = ['#scope','#policy-filter','#date-filter','#department-filter','[data-chat-mode]','#question','.send-button','#agent-api-notice','[data-action="end-agent-task"]'].map(id => {
    const element = {disabled:false, hidden:false, dataset:{}};
    elements.set(id, element);
    return element;
  });
  const requests = [], notices = [];
  const state = {locale:'zh',chatMode:'agent',chatEpoch:0,agentTask:null,docs:[{id:'policy',name:'Policy',status:'ready'}],selected:'policy',filters:{policy_status:['current']},settings:{mode:'api'},draft:'购买3件，每件1200日元',busy:false,messages:[],auth:{user:{id:1}},view:'chat'};
  const context = vm.createContext({
    state, structuredClone, crypto:{randomUUID},
    esc:value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])),
    icon:() => '<svg></svg>', fileIcon:() => '<svg></svg>',
    $:selector => elements.get(selector), document:{querySelectorAll:selector => selector.split(',').map(s => elements.get(s)).filter(Boolean)},
    readyDocs:() => state.docs, toast:message => notices.push(message), localized:value => value,
    api:async (path, options) => {requests.push({path,...options}); return {status:'answered',sources:[],answer:'ok'};},
    renderChat:() => {}, updateChrome:() => {}, refreshDocs:async () => {}, metricsHTML:() => '', answerHTML:message => message.answer,
    ...overrides,
  });
  vm.runInContext(source, context);
  return {context, state, controls, elements, requests, notices};
}

test('new Agent and RAG requests preserve locale, filters and document scope', () => {
  const {context,state} = fixture();
  state.locale='ja';
  for (const [agent,path] of [[true,'/agent'],[false,'/chat']]) {
    const request=context.chatRequest('質問',null,agent);
    assert.equal(request.path,path);
    assert.equal(request.body.language,'ja');
    assert.equal(request.body.document_ids[0],'policy');
    assert.equal(request.body.filters.policy_status[0],'current');
    request.body.filters.policy_status.push('draft');
    assert.equal(state.filters.policy_status.length,1);
  }
});

test('reply sends only supplemental input; client cannot replace server evidence/scope', () => {
  const {context}=fixture();
  const request=context.chatRequest('週3日です',{id:'a/b'},true);
  assert.equal(request.path,'/agent/a%2Fb/reply');
  assert.deepEqual(Object.keys(request.body),['question']);
});

test('clarification is resumed, then terminal response releases task', async () => {
  const {context,state,requests}=fixture();
  let round=0;
  context.api=async (path,options) => {requests.push({path,...options}); return ++round===1?{status:'needs_input',task_id:'opaque',questions:['雇用形態は？']}:{status:'answered',answer:'条件付き',sources:[]};};
  await context.sendChatMessage();
  assert.equal(state.agentTask.id,'opaque');
  assert.equal(state.agentTask.documentIds[0],'policy');
  assert.equal(vm.runInContext('taskLocked()',context),true);
  context.applyChatControls();
  assert.equal(context.$('#scope').disabled,true);
  assert.equal(context.$('#question').disabled,false);
  state.draft='正社員です';
  await context.sendChatMessage();
  assert.equal(requests[1].path,'/agent/opaque/reply');
  assert.deepEqual(Object.keys(requests[1].body),['question']);
  assert.equal(state.messages[1].continuation,true);
  assert.equal(state.messages[1].transcript.length,2);
  assert.equal(state.agentTask,null);
  assert.equal(state.busy,false);
  assert.match(context.renderMessageHTML(state.messages[0]),/信息已补充/);
});

test('double send and local-only Agent do not trigger extra model requests', async () => {
  let release;
  const {context,state}=fixture({api:() => new Promise(resolve => {release=resolve;})});
  const pending=context.sendChatMessage();
  state.draft='second';
  await context.sendChatMessage();
  assert.equal(state.messages.length,1);
  release({status:'answered',sources:[],answer:'ok'});
  await pending;
  state.settings.mode='local'; state.draft='task';
  await context.sendChatMessage();
  assert.equal(state.messages.length,1);
  context.applyChatControls();
  assert.equal(context.$('#question').disabled,true);
  assert.equal(context.$('#agent-api-notice').hidden,false);
});

test('RAG still uses its own endpoint and never creates a task', async () => {
  const {context,state,requests}=fixture();
  state.chatMode='rag';
  await context.sendChatMessage();
  assert.equal(requests[0].path,'/chat');
  assert.equal(state.messages[0].kind,'rag');
  assert.equal(state.agentTask,null);
});

test('cancel is explicit, owner-bound, and clears only a successfully ended task', async () => {
  const {context,state,requests}=fixture();
  state.agentTask={id:'task',messageId:'m'};
  state.messages=[{id:'m',status:'needs_input'}];
  assert.equal(await context.endAgentTask(),true);
  assert.equal(requests[0].method,'DELETE');
  assert.equal(requests[0].path,'/agent/task');
  assert.equal(state.agentTask,null);
  assert.equal(state.messages[0].closed,true);
  state.agentTask={id:'other'};
  context.api=async () => {throw Object.assign(new Error('busy'),{status:409});};
  assert.equal(await context.endAgentTask(),false);
  assert.equal(state.agentTask.id,'other');
  assert.equal(state.busy,false);
  context.api=async () => {throw Object.assign(new Error('expired'),{status:404});};
  assert.equal(await context.endAgentTask(),true);
  assert.equal(state.agentTask,null);
});

for (const status of [404,409]) test(`HTTP ${status} releases stale reply handle and offers a fresh task`, async () => {
  const {context,state}=fixture({api:async () => {throw Object.assign(new Error('server detail'),{status});}});
  state.agentTask={id:'old',messageId:'oldmessage',transcript:['original'],documentIds:['policy'],documentNames:['Policy']};
  state.messages=[{id:'oldmessage',status:'needs_input'}];
  await context.sendChatMessage();
  assert.equal(state.agentTask,null);
  assert.equal(state.messages[0].closed,true);
  assert.match(state.messages[1].error,/重新开始/);
  assert.equal(state.messages[1].transcript[0],'original');
});

test('logout discards an in-flight response and clears sensitive task/draft/filters', async () => {
  let release, renders=0;
  const {context,state}=fixture({api:() => new Promise(resolve => {release=resolve;}),renderChat:() => {renders++;}});
  const pending=context.sendChatMessage();
  context.resetChatIdentity(); state.auth=null;
  release({status:'needs_input',task_id:'secret',questions:['secret']});
  await pending;
  assert.equal(state.messages.length,0);
  assert.equal(state.agentTask,null);
  assert.equal(state.draft,'');
  assert.equal(Object.keys(state.filters).length,0);
  assert.equal(state.chatMode,'rag');
  assert.equal(renders,1); // Only the pre-request render; none after logout.
});

test('document links use trusted local route; tools/users never masquerade as PDFs', () => {
  const {context}=fixture();
  const doc={kind:'document',document_id:'doc/1',page:2,name:'Policy',number:1,url:'javascript:alert(1)',text:'<script>secret</script>'};
  assert.equal(context.sourcePdfUrl(doc),'/api/documents/doc%2F1/file#page=2');
  assert.match(context.sourceRailHTML(doc),/&lt;script&gt;/);
  assert.doesNotMatch(context.sourceRailHTML(doc),/javascript:|<script>/);
  assert.equal(context.sourcePdfUrl({...doc,page:null}),null);
  for (const kind of ['user','tool']) {
    const source={...doc,kind,name:'calendar',provenance:kind==='tool'?'mock':'self_report'};
    assert.equal(context.sourcePdfUrl(source),null);
    const html=context.sourceRailHTML(source);
    assert.doesNotMatch(html,/href=|PDF 第|PDFで確認/);
    assert.match(html,kind==='tool'?/模拟日历/:/用户自述/);
  }
});

test('typed evidence groups and mock disclaimer remain visible in Japanese', () => {
  const {context,state}=fixture(); state.locale='ja';
  const message={id:'m',kind:'agent',status:'answered',answer:'ok',evidence_notices:{uses_mock_data:true,uses_self_report:true},sources:[{number:1,name:'Policy',page:1},{number:2,kind:'tool',name:'calendar',provenance:'mock'},{number:3,kind:'user',text:'申告'}]};
  const html=context.renderMessageHTML(message);
  for (const text of ['資料の根拠','ツールの根拠','ユーザー情報','模擬データ','あなたの申告']) assert.ok(html.includes(text),text);
  assert.doesNotMatch(html,/undefined|nullページ/);
});

test('date offset panel omits unused weekday defaults from the validated tool arguments', () => {
  const {context}=fixture();
  const html=context.sourceRailHTML({kind:'tool',name:'calendar',number:1,text:'2026-10-09',metadata:{arguments:{operation:'date_offset',start_date:'2026-10-12',offset_days:-3,weekday:0,week_offset:1},result:{date:'2026-10-09',timezone:'Asia/Tokyo'}}});
  assert.match(html,/2026-10-12/);
  assert.match(html,/2026-10-09/);
  assert.doesNotMatch(html,/周偏移|周一为0/);
});

test('trace shows observed tool results and verification, without model rationale or arguments', () => {
  const {context}=fixture();
  const html=context.agentTraceHTML({trace:[{step:1,event:'call_tool',tool:'calculator',arguments:'PRIVATE'},{step:1,event:'tool_completed',tool:'calculator'},{step:2,event:'tool_error',tool:'calendar',reason:'PRIVATE'},{step:3,event:'prepare_answer',reason:'PRIVATE'}],support:{method:'quote_match_and_model_entailment',all_supported:true}});
  assert.match(html,/2 次工具调用/);
  assert.match(html,/结果未用作依据/);
  assert.match(html,/全部断言通过检查/);
  assert.doesNotMatch(html,/PRIVATE|prepare_answer|call_tool/);
});

test('clarification and source text cannot inject markup', () => {
  const {context,state}=fixture(); state.agentTask={messageId:'m'};
  const html=context.renderMessageHTML({id:'m',kind:'agent',question:'<img src=x onerror=alert(1)>',status:'needs_input',questions:['<script>oops</script>']});
  assert.doesNotMatch(html,/<img|<script/);
  assert.match(html,/&lt;script&gt;/);
});

test('a late HTTP 401 from a previous identity cannot log out the next identity', async () => {
  let release, logins=0;
  const context=vm.createContext({
    localStorage:{getItem:() => null}, navigator:{language:'ja'},
    document:{addEventListener:() => {}}, FormData,
    showLogin:() => {logins++;}, fetch:() => new Promise(resolve => {release=resolve;}),
  });
  const app=readFileSync(join(__dirname,'../../dist/app.js'),'utf8').replace('\ninit();\n','\n');
  vm.runInContext(app,context);
  const pending=context.api('/agent',{method:'POST',body:{question:'test'}});
  vm.runInContext('state.chatEpoch++; state.auth={user:{id:2}};',context);
  release({status:401,ok:false,json:async () => ({detail:'old request'})});
  await assert.rejects(pending,error => error.status===401);
  assert.equal(logins,0);
  assert.equal(vm.runInContext('state.auth.user.id',context),2);
});

'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

for (const locale of ['zh','ja']) test(`demo disables mutation controls even for admin, with ${locale} notice`, () => {
  const controls = [{disabled:false,hidden:false}];
  const nodes = new Map([['#session-control',{}],['.workspace small',{}],['.storage-line span',{}]]);
  let markup='';
  nodes.set('#main',{insertAdjacentHTML:(_,html) => {markup=html;}});
  const context = vm.createContext({
    state:{locale,auth:{mode:'required',demo:true,user:{roles:['admin'],username:'Reviewer'}}},
    $:key => nodes.get(key), document:{querySelectorAll:() => controls}, esc:s => s,
  });
  vm.runInContext(readFileSync(join(__dirname,'../../dist/governance.js'),'utf8'),context);
  context.applyAccess();
  assert.equal(controls[0].disabled,true);
  assert.equal(controls[0].hidden,true);
  assert.match(markup,locale==='ja'?/個人情報・機密情報/:/个人隐私或企业机密/);
  assert.match(nodes.get('.storage-line span').textContent,locale==='ja'?/サーバー/:/服务器/);
});

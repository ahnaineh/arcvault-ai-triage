const {readFileSync} = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const elements = {};
for (const id of ['tester','progress','submit','resume','new','detail','source','message']) elements[id] = {value:'fixture', hidden:false, handlers:{}, addEventListener(k,f){this.handlers[k]=f},querySelector(){return {value:'csrf'}}};
const events = {}, calls = [];
let fail = true;
vm.runInNewContext(readFileSync('static/intake/tester.js','utf8'), {
 document:{hidden:false,querySelector:s=>elements[s.slice(1)]},
 window:{addEventListener:(k,f)=>events[k]=f}, AbortController, setTimeout,clearTimeout,
 crypto:{randomUUID:()=> 'retained-key'},location:{reload(){}},
 fetch:async (url, options)=> {calls.push({url,options}); if(fail) throw Error('uncertain'); return {ok:true,json:async()=>url.includes('/api/v1/requests/') ? {id:'fixture',status_url:'/status/fixture'} : {status:'completed',attempt_count:1}};}
});
const settle = () => new Promise(r=>setImmediate(r));
(async()=>{
 elements.tester.handlers.submit({preventDefault(){}});
 await settle();
 assert.equal(calls.length,1);
 events.pagehide(); events.pageshow();
 fail=false;
 elements.resume.handlers.click(); elements.resume.handlers.click();
 await settle();
 assert.equal(calls.length,3);
 assert.equal(calls[0].options.body,calls[1].options.body);
 events.pagehide(); events.pageshow();
 elements.resume.handlers.click();
 await settle();
 assert.equal(calls.at(-1).url,'/status/fixture');
 console.log('PASS navigation recovery, uncertain-key retention, single flight, known-request resume');
})();

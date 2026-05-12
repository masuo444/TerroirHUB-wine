// Terroir HUB WINE — track.js

// ── モバイル閉じるボタン注入 ──
(function(){
  var CSS='.mob-close-bar{display:none;padding:8px 16px 4px;flex-shrink:0;}.mob-close-bar button{width:100%;padding:10px;background:none;border:1px solid var(--border);border-radius:8px;color:var(--text-muted);font-size:.8rem;letter-spacing:.1em;cursor:pointer;font-family:inherit;transition:all .2s;}.mob-close-bar button:hover{color:var(--text);}@media(max-width:699px){.mob-close-bar{display:block;}}';
  function inject(){
    if(document.getElementById('_mcb_style'))return;
    var panel=document.querySelector('.panel');
    if(!panel)return;
    var row=panel.querySelector('.inp-row');
    if(!row)return;
    var s=document.createElement('style');s.id='_mcb_style';s.textContent=CSS;document.head.appendChild(s);
    var bar=document.createElement('div');bar.className='mob-close-bar';
    bar.innerHTML='<button onclick="typeof closePanel===\'function\'&&closePanel()">✕ チャットを閉じる</button>';
    row.insertAdjacentElement('afterend',bar);
  }
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',inject):inject();
})();

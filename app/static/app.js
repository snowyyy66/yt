const videos = [
  {id:'v1',title:'Как я нажал «пропустить рекламу» 47 раз',channel:'Кот Борисыч',views:'2,4 млн просмотров',age:'2 дня назад',color:'coral',duration:'12:48',category:'Для вас',scene:'🐈',word:'НЕ РЕКЛАМА'},
  {id:'v2',title:'Собрал компьютер из того, что нашёл под диваном',channel:'Паяльник и печеньки',views:'840 тыс. просмотров',age:'5 часов назад',color:'blue',duration:'28:03',category:'Технологии',scene:'🖥️',word:'RTX 9090'},
  {id:'v3',title:'Рецепт идеального бутерброда. Спонсор: хлеб',channel:'Шеф на районе',views:'1,1 млн просмотров',age:'1 неделю назад',color:'yellow',duration:'08:17',category:'Кулинария',scene:'🥪',word:'СЕКРЕТНЫЙ РЕЦЕПТ'},
  {id:'v4',title:'Поставил будильник на 6:00. Проснулся в 11:32',channel:'Планировщик жизни',views:'320 тыс. просмотров',age:'Вчера',color:'green',duration:'16:41',category:'Для вас',scene:'⏰',word:'НОВАЯ ЖИЗНЬ'},
  {id:'v5',title:'Топ-10 причин посмотреть это видео до конца',channel:'Алгоритм рекомендует',views:'9,8 млн просмотров',age:'3 недели назад',color:'purple',duration:'10:00',category:'Популярное',scene:'📈',word:'ПРИЧИНА №1'},
  {id:'v6',title:'Распаковываю коробку, в которой была другая коробка',channel:'Почта России unboxing',views:'75 тыс. просмотров',age:'4 дня назад',color:'orange',duration:'21:09',category:'Развлечения',scene:'📦',word:'ЧТО ВНУТРИ?'},
  {id:'v7',title:'Белый шум: сосед сверлит стену (8 часов)',channel:'Звуки панельки',views:'4,2 млн просмотров',age:'1 месяц назад',color:'slate',duration:'8:00:00',category:'Музыка',scene:'🛠️',word:'ASMR'},
  {id:'v8',title:'Обзор обзора на обзор нового телефона',channel:'Обзорщик обзоров',views:'612 тыс. просмотров',age:'6 дней назад',color:'pink',duration:'19:52',category:'Технологии',scene:'📱',word:'ОБЗОР ОБЗОРА'}
];
const categories=['Все','Для вас','Популярное','Технологии','Музыка','Кулинария','Развлечения'];
let activeCategory='Все';
let query='';
const feed=document.querySelector('#feed');
const chips=document.querySelector('#chips');
let activeVideoId=null;
const escapeHtml=(value)=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const formatCount=value=>new Intl.NumberFormat('ru-RU').format(value||0);
function render(){
  chips.innerHTML=categories.map(category=>`<button class="chip ${activeCategory===category?'active':''}" data-category="${category}">${category}</button>`).join('');
  const shown=videos.filter(video=>(activeCategory==='Все'||video.category===activeCategory)&&(`${video.title} ${video.channel}`.toLowerCase().includes(query.toLowerCase())));
  feed.innerHTML=shown.length?shown.map(video=>`<article class="video-card" data-video="${video.id}" tabindex="0"><div class="thumbnail ${video.color}">${video.thumbnail?`<img class="thumb-img" src="${escapeHtml(video.thumbnail)}" alt="Превью: ${escapeHtml(video.title)}">`:`<span class="thumb-word">${video.word}</span><span class="scene">${video.scene}</span>`}<span class="duration">${video.duration}</span></div><div class="video-info"><div class="channel-avatar">${video.scene}</div><div class="video-copy"><h3>${escapeHtml(video.title)}</h3><p>${escapeHtml(video.channel)} ✓</p><p>${video.views} · ${video.age}</p></div><button class="video-menu" data-report="${video.id}" aria-label="Пожаловаться">⋮</button></div></article>`).join(''):'<p>Ничего не нашлось. Алгоритм уже переживает.</p>';
}
function openVideo(id){
  const video=videos.find(item=>item.id===id); if(!video)return;
  activeVideoId=id;
  const history=JSON.parse(localStorage.getItem('history')||'[]').filter(item=>item!==id);history.unshift(id);localStorage.setItem('history',JSON.stringify(history.slice(0,50)));
  const demoComments=[];
  document.querySelector('#player-content').innerHTML=`<div class="watch-layout"><section class="watch-primary"><div class="player-frame ${video.color}"><span>${video.scene}</span></div><div class="player-details"><h2>${escapeHtml(video.title)}</h2><div class="watch-meta"><div class="watch-channel"><div class="channel-avatar">${video.scene}</div><div><strong>${escapeHtml(video.channel)}</strong><small>${escapeHtml(video.views)}</small></div></div><div class="player-actions"><button id="subscribe-button" class="subscribe-button">Подписаться</button><div class="engagement-group"><button id="like-button" aria-pressed="false"><span aria-hidden="true">♡</span><span>Нравится</span><span data-like-count>0</span></button></div><button id="share-button">Поделиться</button><button id="save-video-button">Сохранить</button><button id="report-watch-button" aria-label="Пожаловаться">⋮</button></div></div><div id="save-video-panel" class="save-video-panel hidden"></div><section class="description-panel"><strong>${escapeHtml(video.channel)}</strong><p>${video.uploaded?escapeHtml(video.description||'Описание не добавлено.'): 'Демо-ролик Видосферы. Название и статистика вымышлены.'}</p></section><section class="comment-box"><div class="comment-heading"><h3 id="comment-count">Комментарии (${demoComments.length})</h3><span>${video.uploaded?'':'Пример демо-обсуждения'}</span></div><form id="comment-form" class="comment-composer"><textarea id="comment-input" rows="1" maxlength="2000" placeholder="Оставь комментарий" aria-label="Оставь комментарий" required></textarea><div class="comment-form-footer"><p id="comment-status" role="status"></p><button id="comment-submit" class="comment-submit" type="submit">Отправить</button></div></form><div id="comments" aria-live="polite"></div></section></div></section><aside class="watch-recommendations"><h3>Следом в ленте</h3>${videos.filter(item=>item.id!==id).slice(0,4).map(item=>`<button class="watch-recommendation" data-watch-next="${item.id}"><span class="recommendation-thumb ${item.color}">${item.thumbnail?`<img src="${escapeHtml(item.thumbnail)}" alt="">`:`<b>${escapeHtml(item.word||'ДЕМО')}</b>`}<small>${escapeHtml(item.duration)}</small></span><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.channel)} · ${escapeHtml(item.views)}</small></span></button>`).join('')}</aside></div>`;
  const commentList=document.querySelector('#comments');
  const showComments=items=>{
    document.querySelector('#comment-count').textContent=`Комментарии (${items.length})`;
    commentList.innerHTML=items.length?items.map(item=>`<article class="comment"><div class="comment-avatar">${escapeHtml(item.author.slice(0,1).toUpperCase())}</div><div><strong>${escapeHtml(item.author)}</strong><p>${escapeHtml(item.text)}</p></div></article>`).join(''):'<p class="empty-comments">Пока тихо. Начни разговор первым.</p>';
  };
  showComments(demoComments);
  const playerDialog=document.querySelector('#player-dialog');
  playerDialog.showModal();
  playerDialog.scrollTop=0;
  fetch(`/api/videos/${id}/comments`,{headers:tokenHeaders()}).then(async response=>{if(!response.ok)throw new Error('Не удалось загрузить комментарии');showComments(await response.json());document.querySelector('.comment-heading > span').textContent=''}).catch(()=>{document.querySelector('#comment-status').textContent='Не удалось загрузить комментарии.'});
  fetch(`/api/videos/${id}/like`,{headers:tokenHeaders()}).then(async response=>{if(!response.ok)throw new Error('Лайки недоступны');const state=await response.json();const button=document.querySelector('#like-button');button.setAttribute('aria-pressed',String(state.liked));button.classList.toggle('is-liked',state.liked);button.querySelector('[aria-hidden="true"]').textContent=state.liked?'♥':'♡';button.querySelector('[data-like-count]').textContent=formatCount(state.count)}).catch(()=>{});
  if(video.uploaded){fetch(`/api/videos/${id}/play`,{headers:tokenHeaders()}).then(async response=>{const result=await response.json();if(!response.ok)throw new Error(result.detail||'Видео недоступно');const frame=document.querySelector('.player-frame');frame.innerHTML=`<video controls autoplay playsinline src="${escapeHtml(result.url)}"></video>`}).catch(error=>{const frame=document.querySelector('.player-frame');frame.innerHTML=`<p class="demo-player-note">${escapeHtml(error.message)}</p>`})}else{document.querySelector('.player-frame').innerHTML='<div class="demo-player-note"><span aria-hidden="true">▶</span><strong>Демо-заставка</strong><p>Исходного ролика пока нет. Загрузи своё видео, чтобы проверить настоящий плеер.</p></div>'}
  document.querySelector('#subscribe-button').onclick=async(event)=>{const item=videos.find(entry=>entry.id===id);const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}if(!item?.ownerId){event.currentTarget.textContent='Демо-канал не принимает подписки';return}const response=await fetch(`/api/channels/${item.ownerId}/subscribe`,{method:'PUT',headers:tokenHeaders()});if(response.ok){const result=await response.json();event.currentTarget.textContent=result.subscribed?'Вы подписаны':'Подписаться, пока не передумал'}};
  document.querySelector('#share-button').onclick=async()=>{try{await navigator.clipboard.writeText(new URL(`/?v=${encodeURIComponent(id)}`,location.origin).href);document.querySelector('#share-button').textContent='Ссылка скопирована'}catch{document.querySelector('#comment-status').textContent='Не удалось скопировать ссылку. Скопируй адрес страницы вручную.'}};
  document.querySelector('#save-video-button').onclick=async()=>{
    if(!localStorage.getItem('token')){document.querySelector('#account-dialog').showModal();return}
    const response=await fetch('/api/playlists',{headers:tokenHeaders()});const playlists=await response.json();const panel=document.querySelector('#save-video-panel');
    if(!response.ok||playlists.length===0){panel.classList.remove('hidden');panel.textContent='Сначала создай плейлист в разделе «Плейлисты».';return}
    panel.classList.remove('hidden');panel.innerHTML=`<label>Добавить в <select id="save-playlist">${playlists.map(item=>`<option value="${item.id}">${escapeHtml(item.title)}</option>`).join('')}</select></label><button id="confirm-save-video">Сохранить</button>`;
    document.querySelector('#confirm-save-video').onclick=async()=>{const playlistId=document.querySelector('#save-playlist').value;const result=await fetch(`/api/playlists/${playlistId}/videos/${id}`,{method:'POST',headers:tokenHeaders()});panel.textContent=result.ok?'Добавлено. Теперь оно точно не потеряется.':'Не удалось добавить видео'};
  };
}
render();
chips.addEventListener('click',event=>{if(event.target.dataset.category){activeCategory=event.target.dataset.category;render()}});
feed.addEventListener('click',event=>{const report=event.target.closest('[data-report]');if(report){event.stopPropagation();if(confirm('Пожаловаться на видео? Модератор посмотрит, когда закончит смотреть своё.'))report.closest('.video-card').remove();return}const card=event.target.closest('[data-video]');if(card)openVideo(card.dataset.video)});
feed.addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-video]'))openVideo(event.target.dataset.video)});
document.querySelector('#search-form').addEventListener('submit',event=>{event.preventDefault();query=document.querySelector('#search-input').value;activeCategory='Все';render()});
document.querySelector('#menu-button').onclick=()=>document.querySelector('#sidebar').classList.toggle('hidden');
document.querySelector('#upload-open').onclick=()=>document.querySelector('#upload-dialog').showModal();
document.querySelector('#account-open').onclick=()=>{if(localStorage.getItem('token')){location.href='/?page=you';return}document.querySelector('#account-dialog').showModal()};
document.querySelector('#signin-side').onclick=()=>document.querySelector('#account-dialog').showModal();
document.querySelectorAll('[data-close]').forEach(button=>button.onclick=()=>button.closest('dialog').close());
document.querySelector('#register-toggle').onclick=()=>{const name=document.querySelector('#name-field');const isHidden=name.hidden;name.hidden=!isHidden;document.querySelector('#account-title').textContent=isHidden?'Создание аккаунта':'Вход в Видосферу';document.querySelector('#account-form [name=password]').autocomplete=isHidden?'new-password':'current-password';document.querySelector('#register-toggle').textContent=isHidden?'Уже есть аккаунт? Войти':'Впервые здесь? Создать аккаунт'};
const accountForm=document.querySelector('#account-form');
accountForm.onsubmit=async event=>{
  event.preventDefault();
  const values=Object.fromEntries(new FormData(accountForm));
  const registering=!document.querySelector('#name-field').hidden;
  const status=document.querySelector('#account-status');
  try{
    const response=await fetch(registering?'/api/auth/register':'/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)});
    const result=await response.json();
    if(!response.ok)throw new Error(result.detail||'Не удалось войти');
    localStorage.setItem('token',result.access_token);
    document.querySelector('#account-dialog').close();
    const accountButton=document.querySelector('#account-open');
    const displayName=values.name?.trim()||values.email;
    accountButton.textContent=displayName[0].toUpperCase();
    accountButton.setAttribute('aria-label',`Аккаунт ${displayName}`);
  }catch(error){status.textContent=error.message}
};
const tokenHeaders=()=>{const token=localStorage.getItem('token');return token?{Authorization:`Bearer ${token}`}:{}};
async function syncAccountButton(){
  if(!localStorage.getItem('token'))return;
  try{
    const response=await fetch('/api/auth/me',{headers:tokenHeaders()});
    if(!response.ok){localStorage.removeItem('token');return}
    const user=await response.json();const button=document.querySelector('#account-open');
    button.textContent=user.name[0].toUpperCase();button.setAttribute('aria-label',`Аккаунт ${user.name}`);
  }catch{}
}
syncAccountButton();
document.querySelector('#player-content').addEventListener('submit',async event=>{
  if(!event.target.matches('#comment-form'))return;
  event.preventDefault();
  const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
  const input=document.querySelector('#comment-input');const button=document.querySelector('#comment-submit');const status=document.querySelector('#comment-status');
  if(!input.value.trim())return;
  button.disabled=true;status.textContent='Отправляем…';
  try{
    const response=await fetch(`/api/videos/${activeVideoId}/comments`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({text:input.value.trim()})});
    const result=await response.json();
    if(!response.ok)throw new Error(result.detail||'Не удалось отправить комментарий');
    const list=document.querySelector('#comments');list.querySelector('.empty-comments')?.remove();
    const item=document.createElement('article');item.className='comment';item.innerHTML=`<div class="comment-avatar">${escapeHtml(result.author.slice(0,1).toUpperCase())}</div><div><strong>${escapeHtml(result.author)}</strong><p>${escapeHtml(result.text)}</p></div>`;list.prepend(item);
    const count=list.querySelectorAll('.comment').length;document.querySelector('#comment-count').textContent=`Комментарии (${count})`;input.value='';status.textContent='';
  }catch(error){status.textContent=error.message}finally{button.disabled=false}
});
document.addEventListener('click',async event=>{
  const next=event.target.closest('[data-watch-next]');if(next){openVideo(next.dataset.watchNext);return}
  if(event.target.closest('#like-button')){
    event.preventDefault();event.stopImmediatePropagation();
    const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const button=event.target.closest('#like-button');if(!button||!activeVideoId)return;
    button.disabled=true;
    try{const response=await fetch(`/api/videos/${activeVideoId}/like`,{method:'PUT',headers:tokenHeaders()});const result=await response.json();if(!response.ok)throw new Error(result.detail||'Не удалось поставить лайк');button.setAttribute('aria-pressed',String(result.liked));button.classList.toggle('is-liked',result.liked);button.querySelector('[aria-hidden="true"]').textContent=result.liked?'♥':'♡';button.querySelector('[data-like-count]').textContent=formatCount(result.count)}catch(error){document.querySelector('#comment-status').textContent=error.message}finally{button.disabled=false}
  }
  const watchReport=event.target.closest('#report-watch-button');
  if(watchReport){
    event.preventDefault();
    const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const reason=prompt('Что не так с этим видео?');if(!reason)return;
    const response=await fetch(`/api/videos/${activeVideoId}/reports`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({reason})});
    if(response.ok){watchReport.textContent='✓';watchReport.setAttribute('aria-label','Жалоба отправлена')}
    else document.querySelector('#comment-status').textContent='Не удалось отправить жалобу.';
  }
  const reportButton=event.target.closest('[data-report]');
  if(reportButton){
    event.preventDefault();event.stopImmediatePropagation();
    const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const reason=prompt('Что не так с этим видео?');if(!reason)return;
    const response=await fetch(`/api/videos/${reportButton.dataset.report}/reports`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({reason})});
    if(response.ok){reportButton.textContent='⚑';reportButton.title='Жалоба отправлена'}
  }
},true);
document.querySelector('#upload-form').onsubmit=event=>{
  event.preventDefault();
  const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const form=event.currentTarget;const values=new FormData(form);const file=document.querySelector('#video-file').files[0];const status=document.querySelector('#upload-status');const progress=document.querySelector('#upload-progress');
    if(!file){status.textContent='Сначала выбери видео';return}
    const uploadRequest=async()=>{
      const start=await fetch('/api/videos/upload-url',{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({title:values.get('title'),description:values.get('description'),visibility:values.get('visibility'),grant_email:values.get('grant_email')||null,content_type:file.type||'application/octet-stream',size:file.size})});
      const ticket=await start.json();if(!start.ok)throw new Error(ticket.detail||'Не удалось начать загрузку');
      await new Promise((resolve,reject)=>{const request=new XMLHttpRequest();request.open('PUT',ticket.upload_url);request.setRequestHeader('Content-Type',ticket.content_type);request.upload.onprogress=event=>{if(event.lengthComputable)progress.value=Math.round(event.loaded/event.total*90)};request.onload=()=>request.status>=200&&request.status<300?resolve():reject(new Error('Хранилище отклонило файл. Проверь настройки CORS у bucket.'));request.onerror=()=>reject(new Error('Соединение с хранилищем прервалось. Можно начать загрузку снова.'));request.send(file)});
      const finish=await fetch(`/api/videos/${ticket.id}/complete`,{method:'POST',headers:tokenHeaders()});const result=await finish.json();if(!finish.ok)throw new Error(result.detail||'Не удалось проверить загруженный файл');progress.value=100;
      const grantEmail=values.get('grant_email');if(values.get('visibility')==='private'&&grantEmail){const grant=await fetch(`/api/videos/${ticket.id}/access`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({email:grantEmail})});if(!grant.ok){status.textContent='Видео загружено, но доступ не выдан. Проверь почту получателя.';return}}
      status.innerHTML=`Видео сохранено. <a href="/?v=${encodeURIComponent(ticket.id)}">Открыть ролик</a>`;
    };
    status.textContent='Подготавливаем безопасную загрузку…';progress.value=0;uploadRequest().catch(error=>{status.textContent=error.message});
};
const originalRender=render;
async function renderRoute(){
  const params=new URLSearchParams(location.search);const page=params.get('page');const channelId=params.get('channel');const videoId=params.get('v');
  if(videoId){const response=await fetch(`/api/videos/${videoId}`,{headers:tokenHeaders()});const item=await response.json();if(response.ok){if(!videos.some(video=>video.id===item.id))videos.unshift({...item,scene:'🎬',word:'ТВОЁ ВИДЕО'});openVideo(videoId)}else{feed.innerHTML=`<p>${escapeHtml(item.detail||'Видео недоступно')}</p>`}return}
  if(!page&&!channelId){
    try{const response=await fetch('/api/videos');if(response.ok){const uploaded=await response.json();for(const item of uploaded){if(!item.uploaded)continue;const normalized={id:item.id,title:item.title,description:item.description,channel:item.channel,views:item.views,age:item.age,color:item.color||'slate',duration:item.duration||'--:--',category:item.category||'Новое',scene:'▶',word:'СВЕЖАЯ ЗАПИСЬ',uploaded:true,ownerId:item.owner_id,thumbnail:item.thumbnail};const index=videos.findIndex(video=>video.id===item.id);if(index<0)videos.unshift(normalized);else videos[index]={...videos[index],...normalized}}}}catch{};
    originalRender();return;
  }
  chips.innerHTML='';feed.innerHTML='';
  if(page==='moderation'){
    feed.innerHTML='<h1>Модераторская: место, где спорные ролики ждут вердикта</h1><p>Загружаем жалобы…</p>';
    const response=await fetch('/api/moderation/reports',{headers:tokenHeaders()});const payload=await response.json();
    if(!response.ok){feed.innerHTML=`<h1>Модераторская</h1><p>${escapeHtml(payload.detail||'Нужно войти с ролью модератора')}</p>`;return}
    feed.innerHTML='<h1>Очередь жалоб</h1>'+payload.map(item=>`<article class="report-row"><b>${escapeHtml(item.video_id)}</b><p>${escapeHtml(item.reason)}</p><button data-hide="${item.video_id}">Скрыть видео</button></article>`).join('')||'<p>Пока никто ни на кого не пожаловался. Подозрительно.</p>';return;
  }
  if(page==='playlists'){
    const response=await fetch('/api/playlists',{headers:tokenHeaders()});const payload=await response.json();
    feed.innerHTML=`<h1>Плейлисты, которые ты точно пересмотришь</h1><form id="playlist-create"><input name="title" required placeholder="Название плейлиста"><select name="visibility"><option value="public">Открытый</option><option value="private">Приватный</option></select><button>Создать</button></form>${response.ok?payload.map(item=>`<article class="playlist-row"><b>${escapeHtml(item.title)}</b><small>${item.visibility==='private'?'Только ты':'Доступен всем'}</small></article>`).join(''):`<p>${escapeHtml(payload.detail||'Войди, чтобы открыть плейлисты')}</p>`}`;
    document.querySelector('#playlist-create')?.addEventListener('submit',async event=>{event.preventDefault();const values=Object.fromEntries(new FormData(event.currentTarget));const result=await fetch('/api/playlists',{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify(values)});if(result.ok)renderRoute()});return;
  }
  if(page==='history'){
    const history=JSON.parse(localStorage.getItem('history')||'[]');const entries=history.map(id=>videos.find(item=>item.id===id)).filter(Boolean);
    feed.innerHTML=`<h1>История твоих «я только одним глазком»</h1>${entries.map(item=>`<article class="playlist-row"><button data-open-video="${item.id}">${escapeHtml(item.title)}</button><small>${escapeHtml(item.channel)}</small></article>`).join('')||'<p>История пока чистая. Наслаждайся этим недолго.</p>'}`;return;
  }
  if(page==='you'){
    const response=await fetch('/api/auth/me',{headers:tokenHeaders()});const profile=await response.json();
    feed.innerHTML=response.ok?`<h1>Твой уголок Видосферы</h1><p>Привет, ${escapeHtml(profile.name)}. Роль: ${escapeHtml(profile.role)}.</p><a href="/?page=playlists">Открыть плейлисты</a><p><a href="/?channel=${profile.id}">Открыть свой канал</a></p><p>Подписки и история лежат в меню слева.</p>`:`<h1>Твой уголок Видосферы</h1><p>${escapeHtml(profile.detail||'Войди, чтобы открыть свой профиль')}</p><button class="outline-button" id="profile-login">Войти</button>`;document.querySelector('#profile-login')?.addEventListener('click',()=>document.querySelector('#account-dialog').showModal());return;
  }
  if(page==='channels'){
    const response=await fetch('/api/channels/subscriptions',{headers:tokenHeaders()});const payload=await response.json();
    feed.innerHTML=`<h1>Каналы, которым ты доверил своё время</h1>${response.ok?payload.map(item=>`<article class="playlist-row"><a href="/?channel=${item.id}">${escapeHtml(item.name)}</a></article>`).join(''):`<p>${escapeHtml(payload.detail||'Войди, чтобы увидеть подписки')}</p>`}`;return;
  }
  if(channelId){
    const response=await fetch(`/api/channels/${channelId}/videos`);const payload=await response.json();
    const lists=await fetch(`/api/channels/${channelId}/playlists`).then(result=>result.ok?result.json():[]);
    feed.innerHTML=`<h1>${escapeHtml(payload.channel?.name||'Канал')}</h1><p>Открытые видео и плейлисты автора.</p><button id="channel-follow" class="outline-button">Подписаться на канал</button><h2>Видео</h2>${(payload.videos||[]).map(item=>`<article class="playlist-row"><button data-open-video="${item.id}">${escapeHtml(item.title)}</button></article>`).join('')||`<p>${escapeHtml(payload.detail||'Пока автор ничего не выложил')}</p>`}<h2>Плейлисты</h2>${lists.map(item=>`<article class="playlist-row"><b>${escapeHtml(item.title)}</b></article>`).join('')||'<p>Публичных плейлистов пока нет.</p>'}`;
    document.querySelector('#channel-follow').onclick=async()=>{const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}const result=await fetch(`/api/channels/${channelId}/subscribe`,{method:'PUT',headers:tokenHeaders()});if(result.ok)document.querySelector('#channel-follow').textContent=(await result.json()).subscribed?'Вы подписаны':'Подписаться на канал'};return;
  }
  originalRender();
}
renderRoute();
document.addEventListener('click',async event=>{
  const hide=event.target.closest('[data-hide]');if(hide){const result=await fetch(`/api/moderation/videos/${hide.dataset.hide}/hide`,{method:'POST',headers:tokenHeaders()});if(result.ok)hide.closest('.report-row').remove()}
  const open=event.target.closest('[data-open-video]');if(open)openVideo(open.dataset.openVideo);
});

document.querySelector('#video-visibility').addEventListener('change',event=>{document.querySelector('#grant-field').hidden=event.target.value!=='private'});
const voiceButton=document.querySelector('#voice-search');
voiceButton.addEventListener('click',()=>{
  const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SpeechRecognition){voiceButton.title='Голосовой поиск не поддерживается этим браузером';voiceButton.setAttribute('aria-label',voiceButton.title);return}
  const recognition=new SpeechRecognition();recognition.lang='ru-RU';recognition.interimResults=false;
  voiceButton.setAttribute('aria-label','Слушаю запрос');
  recognition.onresult=event=>{document.querySelector('#search-input').value=event.results[0][0].transcript;document.querySelector('#search-form').requestSubmit()};
  recognition.onerror=()=>{voiceButton.setAttribute('aria-label','Голосовой поиск');voiceButton.title='Не удалось распознать запрос'};
  recognition.onend=()=>voiceButton.setAttribute('aria-label','Голосовой поиск');
  recognition.start();
});

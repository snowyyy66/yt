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
const escapeHtml=(value)=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
function render(){
  chips.innerHTML=categories.map(category=>`<button class="chip ${activeCategory===category?'active':''}" data-category="${category}">${category}</button>`).join('');
  const shown=videos.filter(video=>(activeCategory==='Все'||video.category===activeCategory)&&(`${video.title} ${video.channel}`.toLowerCase().includes(query.toLowerCase())));
  feed.innerHTML=shown.length?shown.map(video=>`<article class="video-card" data-video="${video.id}" tabindex="0"><div class="thumbnail ${video.color}">${video.thumbnail?`<img class="thumb-img" src="${escapeHtml(video.thumbnail)}" alt="Превью: ${escapeHtml(video.title)}">`:`<span class="thumb-word">${video.word}</span><span class="scene">${video.scene}</span>`}<span class="duration">${video.duration}</span></div><div class="video-info"><div class="channel-avatar">${video.scene}</div><div class="video-copy"><h3>${escapeHtml(video.title)}</h3><p>${escapeHtml(video.channel)} ✓</p><p>${video.views} · ${video.age}</p></div><button class="video-menu" data-report="${video.id}" aria-label="Пожаловаться">⋮</button></div></article>`).join(''):'<p>Ничего не нашлось. Алгоритм уже переживает.</p>';
}
function openVideo(id){
  const video=videos.find(item=>item.id===id); if(!video)return;
  const history=JSON.parse(localStorage.getItem('history')||'[]').filter(item=>item!==id);history.unshift(id);localStorage.setItem('history',JSON.stringify(history.slice(0,50)));
  const liked=JSON.parse(localStorage.getItem('liked')||'{}')[id];
  document.querySelector('#player-content').innerHTML=`<div class="player-frame ${video.color}"><span>${video.scene}</span></div><div class="player-details"><h2>${escapeHtml(video.title)}</h2><p>${escapeHtml(video.channel)} · ${video.views}</p><div class="player-actions"><button id="like-button">${liked?'♥':'♡'} Нравится <span>${liked?'1 248':'1 247'}</span></button><button id="subscribe-button">Подписаться, пока не передумал</button><button id="share-button">Поделиться</button><button id="save-video-button">Сохранить в плейлист</button></div><div id="save-video-panel" class="hidden"></div><div class="comment-box"><b>Комментарии (3)</b><p><input id="comment-input" placeholder="Оставь комментарий, он попадёт в интернет"><button id="comment-submit">Отправить</button></p><div id="comments"><div class="comment">@чайник_с_крышкой: пришёл за рецептом, остался из-за рекламы</div><div class="comment">@алгоритм: вам также понравится это видео (возможно)</div></div></div></div>`;
  document.querySelector('#player-dialog').showModal();
  fetch(`/api/videos/${id}/comments`).then(response=>response.ok?response.json():[]).then(items=>{if(items.length){document.querySelector('#comments').innerHTML=items.map(item=>`<div class="comment">@${escapeHtml(item.author)}: ${escapeHtml(item.text)}</div>`).join('')}}).catch(()=>{});
  if(video.uploaded){fetch(`/api/videos/${id}/play`,{headers:tokenHeaders()}).then(async response=>{const result=await response.json();if(!response.ok)throw new Error(result.detail||'Видео недоступно');const frame=document.querySelector('.player-frame');frame.innerHTML=`<video controls autoplay playsinline src="${escapeHtml(result.url)}" style="width:100%;height:100%;object-fit:contain"></video>`}).catch(error=>{const frame=document.querySelector('.player-frame');frame.innerHTML=`<p class="demo-player-note">${escapeHtml(error.message)}</p>`})}else{document.querySelector('.player-frame').innerHTML='<p class="demo-player-note">Демо-заставка: исходного ролика нет. Загрузи своё видео, чтобы проверить настоящий плеер.</p>'}
  document.querySelector('#like-button').onclick=()=>{const state=JSON.parse(localStorage.getItem('liked')||'{}');state[id]=!state[id];localStorage.setItem('liked',JSON.stringify(state));openVideo(id)};
  document.querySelector('#subscribe-button').onclick=async(event)=>{const item=videos.find(entry=>entry.id===id);const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}if(!item?.ownerId){event.currentTarget.textContent='Демо-канал не принимает подписки';return}const response=await fetch(`/api/channels/${item.ownerId}/subscribe`,{method:'PUT',headers:tokenHeaders()});if(response.ok){const result=await response.json();event.currentTarget.textContent=result.subscribed?'Вы подписаны':'Подписаться, пока не передумал'}};
  document.querySelector('#share-button').onclick=async()=>{await navigator.clipboard?.writeText(location.href+'?v='+id);document.querySelector('#share-button').textContent='Ссылка скопирована'};
  document.querySelector('#save-video-button').onclick=async()=>{
    if(!localStorage.getItem('token')){document.querySelector('#account-dialog').showModal();return}
    const response=await fetch('/api/playlists',{headers:tokenHeaders()});const playlists=await response.json();const panel=document.querySelector('#save-video-panel');
    if(!response.ok||playlists.length===0){panel.classList.remove('hidden');panel.textContent='Сначала создай плейлист в разделе «Плейлисты».';return}
    panel.classList.remove('hidden');panel.innerHTML=`<label>Добавить в <select id="save-playlist">${playlists.map(item=>`<option value="${item.id}">${escapeHtml(item.title)}</option>`).join('')}</select></label><button id="confirm-save-video">Сохранить</button>`;
    document.querySelector('#confirm-save-video').onclick=async()=>{const playlistId=document.querySelector('#save-playlist').value;const result=await fetch(`/api/playlists/${playlistId}/videos/${id}`,{method:'POST',headers:tokenHeaders()});panel.textContent=result.ok?'Добавлено. Теперь оно точно не потеряется.':'Не удалось добавить видео'};
  };
  document.querySelector('#comment-submit').onclick=()=>{const input=document.querySelector('#comment-input');if(!input.value.trim())return;const item=document.createElement('div');item.className='comment';item.textContent='@ты: '+input.value;document.querySelector('#comments').prepend(item);input.value=''};
}
render();
chips.addEventListener('click',event=>{if(event.target.dataset.category){activeCategory=event.target.dataset.category;render()}});
feed.addEventListener('click',event=>{const report=event.target.closest('[data-report]');if(report){event.stopPropagation();if(confirm('Пожаловаться на видео? Модератор посмотрит, когда закончит смотреть своё.'))report.closest('.video-card').remove();return}const card=event.target.closest('[data-video]');if(card)openVideo(card.dataset.video)});
feed.addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-video]'))openVideo(event.target.dataset.video)});
document.querySelector('#search-form').addEventListener('submit',event=>{event.preventDefault();query=document.querySelector('#search-input').value;activeCategory='Все';render()});
document.querySelector('#menu-button').onclick=()=>document.querySelector('#sidebar').classList.toggle('hidden');
document.querySelector('#upload-open').onclick=()=>document.querySelector('#upload-dialog').showModal();
document.querySelector('#account-open').onclick=()=>document.querySelector('#account-dialog').showModal();
document.querySelector('#signin-side').onclick=()=>document.querySelector('#account-dialog').showModal();
document.querySelectorAll('[data-close]').forEach(button=>button.onclick=()=>button.closest('dialog').close());
document.querySelector('#register-toggle').onclick=()=>{const name=document.querySelector('#name-field');const isHidden=name.hidden;name.hidden=!isHidden;document.querySelector('#account-title').textContent=isHidden?'Создание аккаунта':'Вход в Видосферу';document.querySelector('#account-form [name=password]').autocomplete=isHidden?'new-password':'current-password';document.querySelector('#register-toggle').textContent=isHidden?'Уже есть аккаунт? Войти':'Впервые здесь? Создать аккаунт'};
document.querySelector('#account-form').onsubmit=event=>{event.preventDefault();document.querySelector('#account-status').textContent='Форма готова. Подключение регистрации появится вместе с серверной авторизацией.'};
document.querySelector('#upload-form').onsubmit=event=>{event.preventDefault();const file=document.querySelector('#video-file').files[0];if(!file)return;const bar=document.querySelector('#upload-progress');const status=document.querySelector('#upload-status');let value=0;const timer=setInterval(()=>{value=Math.min(100,value+8);bar.value=value;if(value===100){clearInterval(timer);status.textContent='Демо-загрузка завершена. Серверное хранилище подключается в следующем этапе.'}},120)};
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
    document.querySelector('#account-open').textContent=values.name?.[0]?.toUpperCase()||values.email[0].toUpperCase();
  }catch(error){status.textContent=error.message}
};
const tokenHeaders=()=>{const token=localStorage.getItem('token');return token?{Authorization:`Bearer ${token}`}:{}};
document.addEventListener('click',async event=>{
  if(event.target.id==='like-button'){
    event.preventDefault();event.stopImmediatePropagation();
    const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const id=document.querySelector('#player-dialog').querySelector('.player-details h2').textContent;
    const video=videos.find(item=>item.title===id);if(!video)return;
    const response=await fetch(`/api/videos/${video.id}/like`,{method:'PUT',headers:tokenHeaders()});
    if(response.ok){const result=await response.json();event.target.textContent=result.liked?'♥ Нравится':'♡ Нравится'}
  }
  if(event.target.id==='comment-submit'){
    event.preventDefault();event.stopImmediatePropagation();
    const token=localStorage.getItem('token');if(!token){document.querySelector('#account-dialog').showModal();return}
    const input=document.querySelector('#comment-input');const videoTitle=document.querySelector('#player-dialog .player-details h2').textContent;const video=videos.find(item=>item.title===videoTitle);
    if(!input.value.trim()||!video)return;
    const response=await fetch(`/api/videos/${video.id}/comments`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({text:input.value})});
    if(response.ok){const comment=await response.json();const item=document.createElement('div');item.className='comment';item.textContent=`@${comment.author}: ${comment.text}`;document.querySelector('#comments').prepend(item);input.value=''}
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
  const form=event.currentTarget;const values=new FormData(form);const status=document.querySelector('#upload-status');
  const request=new XMLHttpRequest();request.open('POST','/api/videos');request.setRequestHeader('Authorization',`Bearer ${token}`);
  request.upload.onprogress=progress=>{if(progress.lengthComputable)document.querySelector('#upload-progress').value=Math.round(progress.loaded/progress.total*100)};
  request.onload=async()=>{const result=JSON.parse(request.responseText||'{}');if(request.status>=300){status.textContent=result.detail||'Не удалось загрузить видео';return}const grantEmail=values.get('grant_email');if(values.get('visibility')==='private'&&grantEmail){const grant=await fetch(`/api/videos/${result.id}/access`,{method:'POST',headers:{...tokenHeaders(),'Content-Type':'application/json'},body:JSON.stringify({email:grantEmail})});if(!grant.ok){status.textContent='Видео загружено, но доступ не выдан. Проверь почту получателя.';return}}status.innerHTML=`Видео сохранено. <a href="/?v=${encodeURIComponent(result.id)}">Открыть ролик</a>`};
  request.onerror=()=>{status.textContent='Сеть прервалась. Попробуй загрузить ещё раз.'};
  request.send(values);
};
const originalRender=render;
async function renderRoute(){
  const params=new URLSearchParams(location.search);const page=params.get('page');const channelId=params.get('channel');const videoId=params.get('v');
  if(videoId){const response=await fetch(`/api/videos/${videoId}`,{headers:tokenHeaders()});const item=await response.json();if(response.ok){if(!videos.some(video=>video.id===item.id))videos.unshift({...item,scene:'🎬',word:'ТВОЁ ВИДЕО'});openVideo(videoId)}else{feed.innerHTML=`<p>${escapeHtml(item.detail||'Видео недоступно')}</p>`}return}
  if(!page&&!channelId){
    try{const response=await fetch('/api/videos');if(response.ok){const uploaded=await response.json();for(const item of uploaded){const normalized={id:item.id,title:item.title,channel:item.channel,views:item.views,age:item.age,color:item.color||'slate',duration:item.duration||'--:--',category:item.category||'Новое',scene:'🎬',word:'НОВЫЙ РОЛИК',uploaded:Boolean(item.uploaded),ownerId:item.owner_id,thumbnail:item.thumbnail};const index=videos.findIndex(video=>video.id===item.id);if(index<0)videos.unshift(normalized);else videos[index]={...videos[index],...normalized}}}}catch{};
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

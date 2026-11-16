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
  feed.innerHTML=shown.length?shown.map(video=>`<article class="video-card" data-video="${video.id}" tabindex="0"><div class="thumbnail ${video.color}"><span class="thumb-word">${video.word}</span><span class="scene">${video.scene}</span><span class="duration">${video.duration}</span></div><div class="video-info"><div class="channel-avatar">${video.scene}</div><div class="video-copy"><h3>${escapeHtml(video.title)}</h3><p>${escapeHtml(video.channel)} ✓</p><p>${video.views} · ${video.age}</p></div><button class="video-menu" data-report="${video.id}" aria-label="Пожаловаться">⋮</button></div></article>`).join(''):'<p>Ничего не нашлось. Алгоритм уже переживает.</p>';
}
function openVideo(id){
  const video=videos.find(item=>item.id===id); if(!video)return;
  const liked=JSON.parse(localStorage.getItem('liked')||'{}')[id];
  document.querySelector('#player-content').innerHTML=`<div class="player-frame ${video.color}"><span>${video.scene}</span></div><div class="player-details"><h2>${escapeHtml(video.title)}</h2><p>${escapeHtml(video.channel)} · ${video.views}</p><div class="player-actions"><button id="like-button">${liked?'♥':'♡'} Нравится <span>${liked?'1 248':'1 247'}</span></button><button id="subscribe-button">Подписаться, пока не передумал</button><button id="share-button">Поделиться</button></div><div class="comment-box"><b>Комментарии (3)</b><p><input id="comment-input" placeholder="Оставь комментарий, он попадёт в интернет"><button id="comment-submit">Отправить</button></p><div id="comments"><div class="comment">@чайник_с_крышкой: пришёл за рецептом, остался из-за рекламы</div><div class="comment">@алгоритм: вам также понравится это видео (возможно)</div></div></div></div>`;
  document.querySelector('#player-dialog').showModal();
  document.querySelector('#like-button').onclick=()=>{const state=JSON.parse(localStorage.getItem('liked')||'{}');state[id]=!state[id];localStorage.setItem('liked',JSON.stringify(state));openVideo(id)};
  document.querySelector('#subscribe-button').onclick=(event)=>{event.currentTarget.textContent='Вы подписаны. Отписаться будет сложно';event.currentTarget.disabled=true};
  document.querySelector('#share-button').onclick=async()=>{await navigator.clipboard?.writeText(location.href+'?v='+id);document.querySelector('#share-button').textContent='Ссылка скопирована'};
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
document.querySelector('#register-toggle').onclick=()=>{const name=document.querySelector('#name-field');const isHidden=name.hidden;name.hidden=!isHidden;document.querySelector('#account-title').textContent=isHidden?'Создание аккаунта':'Вход в Видосферу';document.querySelector('#register-toggle').textContent=isHidden?'Уже есть аккаунт? Войти':'Впервые здесь? Создать аккаунт'};
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

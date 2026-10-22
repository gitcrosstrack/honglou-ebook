(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const sections = $$('.chapter-page');
  const key = 'yijuan-honglou-volume1-v2';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch {}
  saved.positions ||= {};
  saved.bookmarks ||= {};
  const initialResume = saved.last ? {...saved.last} : null;
  let chapter = 1, current = 0, timer;
  let font = Number(saved.font) || (matchMedia('(max-width:600px)').matches ? 18 : 20);
  const persist = () => { try { localStorage.setItem(key, JSON.stringify(saved)); } catch {} };
  const smooth = () => matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth';
  function toast(text) {
    $('.toast').textContent = text;
    $('.toast').classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(() => $('.toast').classList.remove('show'), 2800);
  }
  function theme(value) {
    document.documentElement.dataset.theme = value;
    saved.theme = value;
    $$('#theme-options button').forEach(b => b.setAttribute('aria-pressed', b.dataset.theme === value));
    $$('[data-action=night]').forEach(b => b.setAttribute('aria-pressed', value === 'night'));
    persist();
  }
  function setFont(value) {
    font = Math.min(28, Math.max(16, value));
    document.documentElement.style.setProperty('--font-size', font + 'px');
    $('#font-value').value = font;
    $('#smaller').disabled = font === 16;
    $('#larger').disabled = font === 28;
    saved.font = font;
    persist();
  }
  function leading(value) {
    document.documentElement.style.setProperty('--leading', value);
    saved.leading = value;
    $$('[data-leading]').forEach(b => b.setAttribute('aria-pressed', b.dataset.leading === String(value)));
    persist();
  }
  function closeDialogs() { $$('dialog[open]').forEach(d => d.close()); }
  function updateBookmarks() {
    $$('[data-action=bookmark]').forEach(b => b.setAttribute('aria-pressed', Number(saved.bookmarks[chapter]) === current && saved.bookmarks[chapter] !== undefined));
    const list = $('#saved-list');
    list.replaceChildren();
    const entries = Object.entries(saved.bookmarks).filter(([c]) => sections[Number(c)-1]);
    $('#bookmark-empty').hidden = entries.length > 0;
    for (const [c, index] of entries) {
      const button = document.createElement('button');
      button.className = 'saved-item';
      button.textContent = sections[Number(c)-1].dataset.label + ' · 已保存的位置 ↗';
      button.addEventListener('click', () => { closeDialogs(); selectChapter(Number(c), {index:Number(index)}); });
      list.append(button);
    }
  }
  function updateProgress(index) {
    current = index;
    const section = sections[chapter-1];
    const nodes = [...section.querySelectorAll('.original')];
    const total = nodes.reduce((n,p) => n + p.textContent.length, 0);
    const before = nodes.filter(p => Number(p.dataset.index) < index).reduce((n,p) => n + p.textContent.length, 0);
    const value = Math.round(before / Math.max(1,total) * 100);
    $$('.progress').forEach(e => e.textContent = value);
    saved.positions[chapter] = index;
    saved.last = {chapter, index};
    persist();
    updateBookmarks();
  }
  function setHash(value) { try { history.replaceState(null, '', value); } catch {} }
  function selectChapter(number, {index=0, scroll=true, route=true}={}) {
    number = Number(number);
    if (!Number.isInteger(number) || number < 1 || number > sections.length) return;
    chapter = number;
    current = index;
    sections.forEach((section,i) => section.hidden = i !== number-1);
    const section = sections[number-1];
    $$('[data-chapter]').forEach(b => {
      const active = Number(b.dataset.chapter) === number;
      b.classList.toggle('active', active);
      if (active) b.setAttribute('aria-current','page'); else b.removeAttribute('aria-current');
    });
    $$('.current-chapter').forEach(e => e.textContent = section.dataset.label);
    $('#current-select').value = String(number);
    $$('[data-action=prev]').forEach(b => b.disabled = number === 1);
    $$('[data-action=next]').forEach(b => b.disabled = number === sections.length);
    $('#current-stat').textContent = '本回 ' + Number(section.dataset.characters).toLocaleString('zh-CN') + ' 字 · 共十回';
    document.title = '红楼梦 · ' + section.dataset.label + ' | 一卷红楼';
    const target = (index > 0 ? document.getElementById('ch'+number+'-p'+index) : section) || section;
    if (route) setHash('#chapter-'+number);
    closeDialogs();
    if (scroll) {
      target.scrollIntoView({behavior:smooth(),block:'start'});
      section.querySelector('h2').focus({preventScroll:true});
    }
    $$('.progress').forEach(e => e.textContent = '0');
    updateBookmarks();
  }
  function route() {
    const match = location.hash.match(/^#(?:chapter-|ch)(\d+)(?:-p(\d+))?$/);
    if (match) selectChapter(Number(match[1]), {index:Number(match[2]||0),route:false});
  }
  $$('[data-chapter]').forEach(b => b.addEventListener('click', () => selectChapter(b.dataset.chapter)));
  $('#current-select').addEventListener('change', e => selectChapter(e.target.value));
  $$('[data-action]').forEach(b => b.addEventListener('click', () => {
    switch (b.dataset.action) {
      case 'toc': updateBookmarks(); $('#toc-dialog').showModal(); break;
      case 'settings': $('#settings').showModal(); break;
      case 'night': theme(saved.theme === 'night' ? 'paper' : 'night'); break;
      case 'prev': selectChapter(chapter-1); break;
      case 'next': selectChapter(chapter+1); break;
      case 'start': selectChapter(1); break;
      case 'bookmark': saved.bookmarks[chapter]=current; persist(); updateBookmarks(); toast(sections[chapter-1].dataset.label+'书签已保存'); break;
      case 'saved': updateBookmarks(); $('#toc-dialog').showModal(); break;
      case 'top': window.scrollTo({top:0,behavior:smooth()}); break;
      case 'source': {
        const detail = sections[chapter-1].querySelector('.source');
        detail.open = true;
        detail.scrollIntoView({behavior:smooth(),block:'start'});
        break;
      }
    }
  }));
  $$('[data-jump]').forEach(b => b.addEventListener('click', () => {
    document.getElementById(b.dataset.jump)?.scrollIntoView({behavior:smooth(),block:'start'});
  }));
  $$('[data-close]').forEach(b => b.addEventListener('click', () => b.closest('dialog').close()));
  $$('dialog').forEach(d => d.addEventListener('click', e => {
    if (e.target !== d) return;
    const r=d.getBoundingClientRect();
    if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();
  }));
  $('#smaller').onclick=()=>setFont(font-1);
  $('#larger').onclick=()=>setFont(font+1);
  $$('[data-leading]').forEach(b=>b.onclick=()=>leading(b.dataset.leading));
  $$('#theme-options button').forEach(b=>b.onclick=()=>theme(b.dataset.theme));
  if (initialResume && sections[initialResume.chapter-1]) {
    $('#resume').style.display='block';
    $('#resume').textContent='续读 · '+sections[initialResume.chapter-1].dataset.label;
    $('#resume').onclick=()=>selectChapter(initialResume.chapter,{index:initialResume.index});
  }
  theme(saved.theme||'paper'); setFont(font); leading(saved.leading||2.15);
  selectChapter(1,{scroll:false,route:false});
  if(location.hash) requestAnimationFrame(route);
  window.addEventListener('hashchange',route);
  const observer=new IntersectionObserver(()=>{
    const visible=[...sections[chapter-1].querySelectorAll('.original')].filter(p=>{
      const r=p.getBoundingClientRect();return r.bottom>innerHeight*.1&&r.top<innerHeight*.75;
    });
    if(visible.length)updateProgress(Number(visible[0].dataset.index));
  },{rootMargin:'-10% 0px -25% 0px',threshold:0});
  $$('.original').forEach(p=>observer.observe(p));
  const coverObserver=new IntersectionObserver(entries=>{
    entries.forEach(e=>$('.reader-bar').classList.toggle('visible',!e.isIntersecting));
  });
  coverObserver.observe($('.hero'));
})();

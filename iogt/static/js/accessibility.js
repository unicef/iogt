/**
 * IOGT Uzbekistan – Accessibility Module  v4
 * File: iogt/static/js/accessibility.js
 *
 * v4: multi-language UI (Russian, Karakalpak, Uzbek, English fallback).
 *     Language is detected from the URL prefix (/ru/, /kaa/, /uz/, /en/)
 *     and falls back to the <html lang> attribute.
 *
 * Earlier features preserved: profiles, all toggles, body{zoom} text
 * scaling, UI mounted on <html>, local OpenDyslexic font, no backdrop blur.
 */

(function () {
  'use strict';

  /* ==================================================================
     TRANSLATIONS
     NOTE: Karakalpak (kaa) strings are a best-effort translation and
     should be reviewed by a native speaker before going live.
     ================================================================== */

  const TRANSLATIONS = {
    en: {
  title: 'Accessibility',
  reset: 'Reset',
  close: 'Close',
  open: 'Open Accessibility Options',

  profiles: 'Quick Profiles',
  pVision: 'Visually Impaired',
  pAdhd: 'ADHD Friendly',
  pSeizure: 'Seizure Safe',
  pCognitive: 'Cognitive Support',

  secText: 'Text',
  textSize: 'Text Size',
  textSpacing: 'Text Spacing',
  lineHeight: 'Line Height',

  sDefault: 'Default',
  sWide: 'Wide',
  sWider: 'Wider',
  lhTall: 'Tall',
  lhXTall: 'Extra Tall',

  dyslexia: 'Dyslexia Font',
  legible: 'Legible Font',

  secColour: 'Colour & Vision',
  invert: 'Invert Colours',
  grey: 'Grey Hues',
  contrast: 'High Contrast',
  lowSat: 'Low Saturation',
  highSat: 'High Saturation',

  secReading: 'Reading & Focus',
  guide: 'Reading Guide',
  mask: 'Reading Mask',
  focus: 'Highlight Focused Elements',
  hover: 'Highlight Hovered Elements',

  secNav: 'Navigation & Content',
  underline: 'Underline Links',
  hlLinks: 'Highlight Links',
  hlHeadings: 'Highlight Headings',
  cursor: 'Large Cursor',
  hideImages: 'Hide Images',
  stopAnim: 'Stop Animations',
},

ru: {
  title: 'Доступность',
  reset: 'Сбросить',
  close: 'Закрыть',
  open: 'Открыть параметры доступности',

  profiles: 'Быстрые профили',
  pVision: 'Для слабовидящих',
  pAdhd: 'Для людей с СДВГ',
  pSeizure: 'Защита от приступов',
  pCognitive: 'Когнитивная поддержка',

  secText: 'Текст',
  textSize: 'Размер текста',
  textSpacing: 'Интервал между буквами',
  lineHeight: 'Высота строки',

  sDefault: 'Обычный',
  sWide: 'Широкий',
  sWider: 'Шире',
  lhTall: 'Высокая',
  lhXTall: 'Очень высокая',

  dyslexia: 'Шрифт для дислексии',
  legible: 'Разборчивый шрифт',

  secColour: 'Цвет и зрение',
  invert: 'Инвертировать цвета',
  grey: 'Оттенки серого',
  contrast: 'Высокий контраст',
  lowSat: 'Низкая насыщенность',
  highSat: 'Высокая насыщенность',

  secReading: 'Чтение и фокус',
  guide: 'Линейка для чтения',
  mask: 'Маска для чтения',
  focus: 'Выделение активного элемента',
  hover: 'Выделение при наведении',

  secNav: 'Навигация и контент',
  underline: 'Подчёркивать ссылки',
  hlLinks: 'Выделять ссылки',
  hlHeadings: 'Выделять заголовки',
  cursor: 'Большой курсор',
  hideImages: 'Скрыть изображения',
  stopAnim: 'Остановить анимацию',
},

uz: {
  title: 'Maxsus imkoniyatlar',
  reset: 'Tiklash',
  close: 'Yopish',
  open: 'Maxsus imkoniyatlarni ochish',

  profiles: 'Tezkor profillar',
  pVision: 'Zaif ko‘ruvchilar uchun',
  pAdhd: 'Diqqatni jamlashga qulay',
  pSeizure: 'Tutqanoqdan himoya',
  pCognitive: 'Kognitiv yordam',

  secText: 'Matn',
  textSize: 'Matn hajmi',
  textSpacing: 'Harflar oralig‘i',
  lineHeight: 'Qator balandligi',

  sDefault: 'Standart',
  sWide: 'Keng',
  sWider: 'Kengroq',
  lhTall: 'Baland',
  lhXTall: 'Juda baland',

  dyslexia: 'Disleksiya shrifti',
  legible: 'Oson o‘qiladigan shrift',

  secColour: 'Rang va ko‘rish',
  invert: 'Ranglarni teskari qilish',
  grey: 'Kulrang ranglar',
  contrast: 'Yuqori kontrast',
  lowSat: 'Past to‘yinganlik',
  highSat: 'Yuqori to‘yinganlik',

  secReading: 'O‘qish va diqqat',
  guide: 'O‘qish chizig‘i',
  mask: 'O‘qish oynasi',
  focus: 'Faol elementni ajratish',
  hover: 'Kursor ostidagini ajratib ko‘rsatish',

  secNav: 'Navigatsiya va kontent',
  underline: 'Havolalar tagiga chizish',
  hlLinks: 'Havolalarni ajratish',
  hlHeadings: 'Sarlavhalarni ajratish',
  cursor: 'Katta kursor',
  hideImages: 'Rasmlarni yashirish',
  stopAnim: 'Animatsiyani to‘xtatish',
},
    kaa: {
      title:'Arnawlı múmkinshilikler', reset:'Qayta tiklew', close:'Jabıw', open:'Arnawlı múmkinshiliklerdi ashıw',
      profiles:'Jıldam profiller', pVision:'Kóriwi sheklengen', pAdhd:'Diqqat ushın qolaylı', pSeizure:'Tutqanaq waqtǵnda qáwipsiz', pCognitive:'Kognitiv',
      secText:'Tekst', textSize:'Tekst kólemi', textSpacing:'Háripler aralıǵı', lineHeight:'Qatar biyikligi',
      sDefault:'Standart', sWide:'Keń', sWider:'Keńirek', lhTall:'Biyik', lhXTall:'Júdá biyik',
      dyslexia:'Disleksiya ushın shrift', legible:'Ańsat oqılatuǵın shrift',
      secColour:'Reń hám kóriw', invert:'Reńlerdi kerisine aylandırıw', grey:'Sur reńler', contrast:'Joqarı kontrast', lowSat:'Tómen toyǵınlıq', highSat:'Joqarı toyǵınlıq',
      secReading:'Oqıw hám dıqqat', guide:'Oqıw ushın kórsetpe', mask:'Oqıw maskası', focus:'Fokustı ayırıw', hover:'Kursor astın ayırıw',
      secNav:'Navigaciya hám kontent', underline:'Siltemelerdiń astın sızıw', hlLinks:'Siltemelerdi ayırıw', hlHeadings:'Tema atamaların ayırıw', cursor:'Úlken kursor', hideImages:'Súwretlerdi jasırıw', stopAnim:'Animaciyanı toqtatıw',
    },
  };

  function detectLang() {
    // 1) URL prefix: /ru/, /kaa/, /uz/, /en/
    const seg = (location.pathname.split('/').filter(Boolean)[0] || '').toLowerCase();
    if (TRANSLATIONS[seg]) return seg;
    // 2) <html lang="..">
    const hl = (document.documentElement.getAttribute('lang') || '').toLowerCase();
    if (TRANSLATIONS[hl]) return hl;
    const two = hl.slice(0, 2);
    if (TRANSLATIONS[two]) return two;
    // 3) default (site has no English; Uzbek is the safest default)
    return 'uz';
  }

  const LANG = detectLang();
  const T = TRANSLATIONS[LANG] || TRANSLATIONS.en;
  function t(key) { return (T[key] !== undefined ? T[key] : TRANSLATIONS.en[key]) || key; }

  /* ------------------------------------------------------------------ */
  /*  Constants                                                           */
  /* ------------------------------------------------------------------ */

  const STORAGE_KEY = 'iogt_a11y_v3';

  const FONT_SCALES = [0.70, 0.80, 0.90, 0.95, 1.0, 1.1, 1.2, 1.35, 1.5, 1.75, 2.0];
  const FONT_LABELS = ['70%','80%','90%','95%','100%','110%','120%','135%','150%','175%','200%'];
  const DEFAULT_SCALE_IDX = 4;

  const SPACING_CLASSES = ['', 'a11y-spacing-wide', 'a11y-spacing-wider'];
  const LH_CLASSES      = ['', 'a11y-line-height-tall', 'a11y-line-height-xtall'];

  function spacingLabel(i){ return [t('sDefault'), t('sWide'), t('sWider')][i]; }
  function lhLabel(i){ return [t('sDefault'), t('lhTall'), t('lhXTall')][i]; }

  /* ------------------------------------------------------------------ */
  /*  State                                                               */
  /* ------------------------------------------------------------------ */

  const DEFAULT_STATE = {
    scaleIdx: DEFAULT_SCALE_IDX, spacingIdx: 0, lineHeightIdx: 0,
    invertColours:false, greyHues:false, highContrast:false, lowSaturation:false, highSaturation:false,
    readingGuide:false, readingMask:false, focusHighlight:false, highlightHover:false,
    dyslexiaFont:false, legibleFont:false,
    underlineLinks:false, highlightLinks:false, highlightHeadings:false,
    bigCursor:false, hideImages:false, stopAnimations:false,
  };

  const TOGGLES = {
    'a11y-btn-invert':'invertColours','a11y-btn-greyscale':'greyHues','a11y-btn-contrast':'highContrast',
    'a11y-btn-low-sat':'lowSaturation','a11y-btn-high-sat':'highSaturation',
    'a11y-btn-guide':'readingGuide','a11y-btn-mask':'readingMask','a11y-btn-focus':'focusHighlight','a11y-btn-hover':'highlightHover',
    'a11y-btn-dyslexia':'dyslexiaFont','a11y-btn-legible':'legibleFont',
    'a11y-btn-underline':'underlineLinks','a11y-btn-hl-links':'highlightLinks','a11y-btn-hl-headings':'highlightHeadings',
    'a11y-btn-cursor':'bigCursor','a11y-btn-hide-images':'hideImages','a11y-btn-stop-anim':'stopAnimations',
  };

  const TOGGLE_CLASSES = {
    invertColours:'a11y-invert', greyHues:'a11y-greyscale', highContrast:'a11y-high-contrast',
    lowSaturation:'a11y-low-saturation', highSaturation:'a11y-high-saturation',
    focusHighlight:'a11y-focus-highlight', highlightHover:'a11y-highlight-hover',
    dyslexiaFont:'a11y-dyslexia-font', legibleFont:'a11y-legible-font',
    underlineLinks:'a11y-underline-links', highlightLinks:'a11y-highlight-links', highlightHeadings:'a11y-highlight-headings',
    bigCursor:'a11y-big-cursor', hideImages:'a11y-hide-images', stopAnimations:'a11y-stop-animations',
    readingMask:'a11y-reading-mask-on',
  };

  const PROFILES = {
    vision:   ['highContrast','legibleFont','highlightLinks'],
    adhd:     ['readingMask','stopAnimations','lowSaturation'],
    seizure:  ['stopAnimations','lowSaturation'],
    cognitive:['highlightHeadings','highlightLinks','stopAnimations','legibleFont'],
  };

  let state = Object.assign({}, DEFAULT_STATE);

  function loadState(){ try{ const s=localStorage.getItem(STORAGE_KEY); if(s) Object.assign(state, JSON.parse(s)); }catch(_){} }
  function saveState(){ try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }catch(_){} }

  /* ------------------------------------------------------------------ */
  /*  Apply                                                               */
  /* ------------------------------------------------------------------ */

  function applyAll() {
    const body = document.body, html = document.documentElement;

    const scale = FONT_SCALES[state.scaleIdx];
    html.style.setProperty('--a11y-font-scale', scale);
    if (scale === 1) body.style.removeProperty('zoom'); else body.style.zoom = scale;

    SPACING_CLASSES.forEach(c => c && body.classList.remove(c));
    if (state.spacingIdx > 0) body.classList.add(SPACING_CLASSES[state.spacingIdx]);

    LH_CLASSES.forEach(c => c && body.classList.remove(c));
    if (state.lineHeightIdx > 0) body.classList.add(LH_CLASSES[state.lineHeightIdx]);

    Object.keys(TOGGLE_CLASSES).forEach(key => {
      const target = (key === 'readingMask') ? html : body;
      target.classList.toggle(TOGGLE_CLASSES[key], !!state[key]);
    });

    html.classList.toggle('a11y-reading-guide-on', state.readingGuide);
    const guide = document.getElementById('a11y-reading-guide');
    if (guide) guide.style.display = state.readingGuide ? 'block' : 'none';
    const mask = document.getElementById('a11y-reading-mask');
    if (mask) mask.style.display = state.readingMask ? 'block' : 'none';

    updatePointerListener();
    syncUI();
  }

  /* ------------------------------------------------------------------ */
  /*  Reading guide + mask                                                */
  /* ------------------------------------------------------------------ */

  let guideEl=null, maskTop=null, maskBot=null;
  function onPointerMove(e){
    const y = e.clientY;
    if (state.readingGuide){
      if(!guideEl) guideEl=document.getElementById('a11y-reading-guide');
      if(guideEl) guideEl.style.top=(y-16)+'px';
    }
    if (state.readingMask){
      if(!maskTop) maskTop=document.getElementById('a11y-mask-top');
      if(!maskBot) maskBot=document.getElementById('a11y-mask-bottom');
      if(maskTop&&maskBot){ maskTop.style.height=Math.max(0,y-40)+'px'; maskBot.style.top=(y+40)+'px'; }
    }
  }
  function updatePointerListener(){
    if (state.readingGuide || state.readingMask) document.addEventListener('mousemove', onPointerMove, {passive:true});
    else document.removeEventListener('mousemove', onPointerMove);
  }

  /* ------------------------------------------------------------------ */
  /*  Sync UI                                                             */
  /* ------------------------------------------------------------------ */

  function syncUI(){
    setTxt('a11y-text-size-value', FONT_LABELS[state.scaleIdx]);
    setTxt('a11y-spacing-value', spacingLabel(state.spacingIdx));
    setTxt('a11y-lh-value', lhLabel(state.lineHeightIdx));
    setDisabled('a11y-btn-text-inc', state.scaleIdx>=FONT_SCALES.length-1);
    setDisabled('a11y-btn-text-dec', state.scaleIdx<=0);
    setDisabled('a11y-btn-spacing-inc', state.spacingIdx>=SPACING_CLASSES.length-1);
    setDisabled('a11y-btn-spacing-dec', state.spacingIdx<=0);
    setDisabled('a11y-btn-lh-inc', state.lineHeightIdx>=LH_CLASSES.length-1);
    setDisabled('a11y-btn-lh-dec', state.lineHeightIdx<=0);
    Object.keys(TOGGLES).forEach(id => setActive(id, state[TOGGLES[id]]));
  }
  function setTxt(id,v){ const e=document.getElementById(id); if(e) e.textContent=v; }
  function setDisabled(id,v){ const e=document.getElementById(id); if(e) e.disabled=v; }
  function setActive(id,v){ const e=document.getElementById(id); if(!e)return; e.classList.toggle('a11y-active',!!v); e.setAttribute('aria-pressed', v?'true':'false'); }

  /* ------------------------------------------------------------------ */
  /*  Icons + builders                                                    */
  /* ------------------------------------------------------------------ */

  const I = {
    invert:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0 0 20V2z"/><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    grey:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><line x1="12" y1="3" x2="12" y2="21"/></svg>',
    contrast:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 2v16a8 8 0 0 1 0-16z"/></svg>',
    lowSat:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v18M5 8l14 8M19 8L5 16"/></svg>',
    highSat:'<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="7" cy="9" r="4"/><circle cx="15" cy="14" r="4" opacity="0.6"/></svg>',
    guide:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="10" width="20" height="4" rx="1" fill="currentColor" fill-opacity="0.3"/><line x1="2" y1="10" x2="22" y2="10"/><line x1="2" y1="14" x2="22" y2="14"/></svg>',
    mask:'<svg viewBox="0 0 24 24" fill="currentColor"><rect x="0" y="0" width="24" height="8" opacity="0.5"/><rect x="0" y="16" width="24" height="8" opacity="0.5"/></svg>',
    focus:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="3" stroke-dasharray="4 2"/></svg>',
    hover:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 2l5 18 3-7 7-3z"/><circle cx="17" cy="17" r="3" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    dyslexia:'<svg viewBox="0 0 24 24" fill="currentColor"><text x="2" y="17" font-size="13" font-weight="bold" font-family="serif">Aa</text></svg>',
    legible:'<svg viewBox="0 0 24 24" fill="currentColor"><text x="3" y="17" font-size="13" font-family="sans-serif">Ag</text></svg>',
    underline:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3v9a6 6 0 0 0 12 0V3h-2v9a4 4 0 0 1-8 0V3H6zM4 20h16v2H4v-2z"/></svg>',
    hlLinks:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
    hlHead:'<svg viewBox="0 0 24 24" fill="currentColor"><text x="2" y="18" font-size="15" font-weight="bold">H</text></svg>',
    cursor:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 2l5 18 3-7 7-3z"/></svg>',
    hideImg:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 3l18 18M8 10a1.5 1.5 0 1 0 0-.01"/></svg>',
    stopAnim:'<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg>',
    // profile icons
    pVision:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>',
    pAdhd:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
    pSeizure:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L4 14h6l-1 8 9-12h-6z"/></svg>',
    pCognitive:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 3a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 0V3a3 3 0 0 0-3 0z"/><path d="M15 3a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 0"/></svg>',
  };

  function row(id, label, icon){
    return `<button id="${id}" class="a11y-toggle-row" aria-pressed="false">
      <span class="a11y-toggle-row__icon" aria-hidden="true">${icon}</span>
      <span class="a11y-toggle-row__label">${label}</span>
      <span class="a11y-toggle-row__pill" aria-hidden="true"></span>
    </button>`;
  }

  /* ------------------------------------------------------------------ */
  /*  Build                                                               */
  /* ------------------------------------------------------------------ */

  function buildPanel(){
    const docEl = document.documentElement;

    const guide = document.createElement('div');
    guide.id='a11y-reading-guide'; guide.setAttribute('aria-hidden','true'); docEl.appendChild(guide);

    const mask = document.createElement('div');
    mask.id='a11y-reading-mask'; mask.setAttribute('aria-hidden','true');
    mask.innerHTML='<div id="a11y-mask-top"></div><div id="a11y-mask-bottom"></div>'; docEl.appendChild(mask);

    const backdrop = document.createElement('div');
    backdrop.id='a11y-backdrop'; backdrop.setAttribute('aria-hidden','true'); docEl.appendChild(backdrop);

    const btn = document.createElement('button');
    btn.id='a11y-toggle-btn'; btn.setAttribute('aria-label', t('open'));
    btn.setAttribute('aria-expanded','false'); btn.setAttribute('aria-controls','a11y-panel'); btn.setAttribute('title', t('title'));
    btn.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true" fill="white"><circle cx="12" cy="3.6" r="2.2"/><path d="M12 7c-1.1 0-5.6.7-6.2.8-.6.1-1 .7-.9 1.3.1.6.7 1 1.3.9L10 9.4v2.3l-1.9 7.1c-.2.7.2 1.4.9 1.6.7.2 1.4-.2 1.6-.9L12 15l1.4 4.5c.2.7.9 1.1 1.6.9.7-.2 1.1-.9.9-1.6L14 11.7V9.4l3.8.6c.6.1 1.2-.3 1.3-.9.1-.6-.3-1.2-.9-1.3C17.6 7.7 13.1 7 12 7z"/></svg>';
    docEl.appendChild(btn);

    const panel = document.createElement('div');
    panel.id='a11y-panel'; panel.setAttribute('role','dialog'); panel.setAttribute('aria-label', t('title')); panel.setAttribute('aria-modal','true');
    panel.setAttribute('lang', LANG);

    panel.innerHTML = `
      <div class="a11y-panel__header">
        <div class="a11y-panel__header-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="white"><circle cx="12" cy="3.6" r="2.2"/><path d="M12 7c-1.1 0-5.6.7-6.2.8-.6.1-1 .7-.9 1.3.1.6.7 1 1.3.9L10 9.4v2.3l-1.9 7.1c-.2.7.2 1.4.9 1.6.7.2 1.4-.2 1.6-.9L12 15l1.4 4.5c.2.7.9 1.1 1.6.9.7-.2 1.1-.9.9-1.6L14 11.7V9.4l3.8.6c.6.1 1.2-.3 1.3-.9.1-.6-.3-1.2-.9-1.3C17.6 7.7 13.1 7 12 7z"/></svg></div>
        <h2 class="a11y-panel__title">${t('title')}</h2>
        <button class="a11y-panel__reset" id="a11y-btn-reset">${t('reset')}</button>
        <button class="a11y-panel__close" id="a11y-panel-close" aria-label="${t('close')}">&times;</button>
      </div>
      <div class="a11y-panel__body">

        <p class="a11y-section-label">${t('profiles')}</p>
        <div class="a11y-profiles">
          <button class="a11y-profile" data-profile="vision"><span class="a11y-profile__icon" aria-hidden="true">${I.pVision}</span><span>${t('pVision')}</span></button>
          <button class="a11y-profile" data-profile="adhd"><span class="a11y-profile__icon" aria-hidden="true">${I.pAdhd}</span><span>${t('pAdhd')}</span></button>
          <button class="a11y-profile" data-profile="seizure"><span class="a11y-profile__icon" aria-hidden="true">${I.pSeizure}</span><span>${t('pSeizure')}</span></button>
          <button class="a11y-profile" data-profile="cognitive"><span class="a11y-profile__icon" aria-hidden="true">${I.pCognitive}</span><span>${t('pCognitive')}</span></button>
        </div>

        <p class="a11y-section-label">${t('secText')}</p>
        <div class="a11y-stepper">
          <div class="a11y-stepper__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><text x="1" y="16" font-size="10" fill="currentColor" stroke="none">A</text><text x="10" y="18" font-size="14" fill="currentColor" stroke="none">A</text></svg></div>
          <div class="a11y-stepper__label">${t('textSize')}<small id="a11y-text-size-value">100%</small></div>
          <button id="a11y-btn-text-dec" class="a11y-step-btn" aria-label="−">−</button>
          <button id="a11y-btn-text-inc" class="a11y-step-btn" aria-label="+">+</button>
        </div>
        <div class="a11y-stepper">
          <div class="a11y-stepper__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 10h16M4 14h10"/></svg></div>
          <div class="a11y-stepper__label">${t('textSpacing')}<small id="a11y-spacing-value">${spacingLabel(0)}</small></div>
          <button id="a11y-btn-spacing-dec" class="a11y-step-btn" aria-label="−">−</button>
          <button id="a11y-btn-spacing-inc" class="a11y-step-btn" aria-label="+">+</button>
        </div>
        <div class="a11y-stepper">
          <div class="a11y-stepper__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16M4 9h16M4 13h16M4 17h16"/></svg></div>
          <div class="a11y-stepper__label">${t('lineHeight')}<small id="a11y-lh-value">${lhLabel(0)}</small></div>
          <button id="a11y-btn-lh-dec" class="a11y-step-btn" aria-label="−">−</button>
          <button id="a11y-btn-lh-inc" class="a11y-step-btn" aria-label="+">+</button>
        </div>
        ${row('a11y-btn-dyslexia', t('dyslexia'), I.dyslexia)}
        ${row('a11y-btn-legible',  t('legible'),  I.legible)}

        <p class="a11y-section-label">${t('secColour')}</p>
        ${row('a11y-btn-invert',   t('invert'),  I.invert)}
        ${row('a11y-btn-greyscale',t('grey'),    I.grey)}
        ${row('a11y-btn-contrast', t('contrast'),I.contrast)}
        ${row('a11y-btn-low-sat',  t('lowSat'),  I.lowSat)}
        ${row('a11y-btn-high-sat', t('highSat'), I.highSat)}

        <p class="a11y-section-label">${t('secReading')}</p>
        ${row('a11y-btn-guide', t('guide'), I.guide)}
        ${row('a11y-btn-mask',  t('mask'),  I.mask)}
        ${row('a11y-btn-focus', t('focus'), I.focus)}
        ${row('a11y-btn-hover', t('hover'), I.hover)}

        <p class="a11y-section-label">${t('secNav')}</p>
        ${row('a11y-btn-underline',   t('underline'),  I.underline)}
        ${row('a11y-btn-hl-links',    t('hlLinks'),    I.hlLinks)}
        ${row('a11y-btn-hl-headings', t('hlHeadings'), I.hlHead)}
        ${row('a11y-btn-cursor',      t('cursor'),     I.cursor)}
        ${row('a11y-btn-hide-images', t('hideImages'), I.hideImg)}
        ${row('a11y-btn-stop-anim',   t('stopAnim'),   I.stopAnim)}

      </div>`;
    docEl.appendChild(panel);
  }

  /* ------------------------------------------------------------------ */
  /*  Events                                                              */
  /* ------------------------------------------------------------------ */

  function wireEvents(){
    const panel=document.getElementById('a11y-panel');
    const trigger=document.getElementById('a11y-toggle-btn');
    const backdrop=document.getElementById('a11y-backdrop');
    const closeBtn=document.getElementById('a11y-panel-close');
    const resetBtn=document.getElementById('a11y-btn-reset');

    const open =()=>{panel.classList.add('a11y-open');backdrop.classList.add('a11y-open');trigger.setAttribute('aria-expanded','true');closeBtn.focus();};
    const close=()=>{panel.classList.remove('a11y-open');backdrop.classList.remove('a11y-open');trigger.setAttribute('aria-expanded','false');trigger.focus();};

    trigger.addEventListener('click',()=>panel.classList.contains('a11y-open')?close():open());
    closeBtn.addEventListener('click',close);
    backdrop.addEventListener('click',close);
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&panel.classList.contains('a11y-open'))close();});

    function stepper(inc,dec,key,max){
      document.getElementById(inc).addEventListener('click',()=>{if(state[key]<max){state[key]++;applyAll();saveState();}});
      document.getElementById(dec).addEventListener('click',()=>{if(state[key]>0){state[key]--;applyAll();saveState();}});
    }
    stepper('a11y-btn-text-inc','a11y-btn-text-dec','scaleIdx',FONT_SCALES.length-1);
    stepper('a11y-btn-spacing-inc','a11y-btn-spacing-dec','spacingIdx',SPACING_CLASSES.length-1);
    stepper('a11y-btn-lh-inc','a11y-btn-lh-dec','lineHeightIdx',LH_CLASSES.length-1);

    Object.keys(TOGGLES).forEach(id=>{
      const el=document.getElementById(id); if(!el)return;
      el.addEventListener('click',()=>{
        const key=TOGGLES[id]; state[key]=!state[key];
        if(key==='lowSaturation'&&state[key]) state.highSaturation=false;
        if(key==='highSaturation'&&state[key]) state.lowSaturation=false;
        applyAll(); saveState();
      });
    });

    panel.querySelectorAll('.a11y-profile').forEach(b=>{
      b.addEventListener('click',()=>applyProfile(b.getAttribute('data-profile'),b));
    });

    resetBtn.addEventListener('click',()=>{
      state=Object.assign({},DEFAULT_STATE);
      document.body.style.removeProperty('zoom');
      document.documentElement.style.setProperty('--a11y-font-scale','1');
      panel.querySelectorAll('.a11y-profile.a11y-active').forEach(b=>b.classList.remove('a11y-active'));
      applyAll(); saveState();
    });
  }

  function applyProfile(name,btn){
    const keys=PROFILES[name]; if(!keys)return;
    const panel=document.getElementById('a11y-panel');
    const wasActive=btn.classList.contains('a11y-active');
    panel.querySelectorAll('.a11y-profile.a11y-active').forEach(b=>b.classList.remove('a11y-active'));
    if(wasActive){
      keys.forEach(k=>state[k]=false);
      if(name==='vision') state.scaleIdx=DEFAULT_SCALE_IDX;
    } else {
      keys.forEach(k=>state[k]=true);
      if(name==='vision'&&state.scaleIdx<6) state.scaleIdx=6;
      btn.classList.add('a11y-active');
    }
    applyAll(); saveState();
  }

  /* ------------------------------------------------------------------ */
  /*  Init                                                                */
  /* ------------------------------------------------------------------ */

  function init(){ loadState(); buildPanel(); wireEvents(); applyAll(); }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init);
  else init();

})();

/**
 * aioshad Documentation Script
 * Exact interaction mechanics modeled on peyk
 */

(function () {
  'use strict';

  // 1. Theme toggle
  const themeBtn = document.getElementById('themeBtn');
  function getTheme() {
    return localStorage.getItem('aioshad.theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  }

  function setTheme(t) {
    document.documentElement.dataset.theme = t;
    localStorage.setItem('aioshad.theme', t);
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.dataset.theme || getTheme();
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
  setTheme(getTheme());

  // 2. Language toggle
  const langBtn = document.getElementById('langBtn');
  const translations = {
    en: {
      dir: 'ltr',
      lang: 'en',
      langLabel: 'فا',
      navDocs: 'Documentation',
      navFeatures: 'Features',
      navExamples: 'Examples',
      navCompare: 'Comparison',
      heroL1: 'Modern AsyncIO',
      heroL2: 'for Shad Messenger.',
      heroSub: 'High-throughput self-bot & automation framework built on HTTP/2 multiplexing, native cryptography, and aiogram-inspired dispatcher architecture.',
      btnDocs: 'Read Documentation',
      btnGithub: 'View on GitHub',
      stripTitle: 'Native Shad Protocols',
      copyDone: 'Copied',
      bento1Title: 'Multiplexed Edge Conns',
      bento1Desc: 'Persistent HTTP/2 streams across *.iranlms.ir gateways with zero per-request handshake overhead.',
      bento2Title: 'Native Cryptography',
      bento2Desc: 'AES-256-CBC, PKCS7 padding, RSA-1024 OAEP SHA1 decryption, and temporary handshake sessions.',
      bento3Title: 'Aiogram-Style Dispatcher',
      bento3Desc: 'Intuitive @client.on_message decorators, modular Router trees, and magic filter F expressions.',
      bento4Title: 'Interactive Conversations',
      bento4Desc: 'Linear async with client.conversation(...) context manager for step-by-step forms and surveys.',
      bento5Title: 'WebRTC Voice Chat',
      bento5Desc: 'Create, join, speak, mute, and list live participants in group or channel voice chats natively.',
      bento6Title: 'Multi-Account Manager',
      bento6Desc: 'Concurrently orchestrate dozens of self-bot accounts on a single asyncio event loop.'
    },
    fa: {
      dir: 'rtl',
      lang: 'fa',
      langLabel: 'EN',
      navDocs: 'مستندات',
      navFeatures: 'قابلیت‌ها',
      navExamples: 'نمونه‌ها',
      navCompare: 'مقایسه',
      heroL1: 'فریم‌ورک مدرن آسنکرون',
      heroL2: 'پیام‌رسان شاد.',
      heroSub: 'کتابخانه پرسرعت و مدرن پایتون برای ساخت سلف‌بات و ربات با اتصال مالتی‌پکسینگ HTTP/2، رمزنگاری بومی شاد و معماری سبک aiogram.',
      btnDocs: 'مطالعه مستندات',
      btnGithub: 'مشاهده گیت‌هاب',
      stripTitle: 'پروتکل‌های اختصاصی شاد',
      copyDone: 'کپی شد',
      bento1Title: 'اتصال سریع HTTP/2',
      bento1Desc: 'استفاده از استریم‌های همزمان به درگاه‌های *.iranlms.ir بدون تاخیر اتصال مجدد.',
      bento2Title: 'رمزنگاری کامل و بومی',
      bento2Desc: 'پیاده‌سازی AES-256-CBC، کلیدهای موقت و رمزگشایی RSA-1024 OAEP SHA1.',
      bento3Title: 'دیسپچر سبک aiogram',
      bento3Desc: 'دکوراتورهای سرراست، ساختار درختی روترها و فیلترهای جادویی F.',
      bento4Title: 'مکالمات مرحله‌به‌مرحله',
      bento4Desc: 'کانتکست منیجر کاربردی client.conversation برای فرم‌ها و پرسش و پاسخ خطی.',
      bento5Title: 'مدیریت ویس‌چت WebRTC',
      bento5Desc: 'ورود، خروج، صحبت و مدیریت وضعیت کاربران در ویس‌چت‌های گروهی و کانالی.',
      bento6Title: 'مدیریت چند اکانت همزمان',
      bento6Desc: 'اجرای ده‌ها اکانت به صورت همزمان روی یک ایونت‌لوپ واحد با ClientManager.'
    }
  };

  function setLanguage(lang) {
    localStorage.setItem('aioshad.lang', lang);
    const t = translations[lang];
    document.documentElement.dir = t.dir;
    document.documentElement.lang = t.lang;

    if (langBtn) {
      langBtn.textContent = t.langLabel;
    }

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      if (t[key]) el.textContent = t[key];
    });
  }

  if (langBtn) {
    langBtn.addEventListener('click', () => {
      const current = localStorage.getItem('aioshad.lang') || 'en';
      setLanguage(current === 'en' ? 'fa' : 'en');
    });
  }
  setLanguage(localStorage.getItem('aioshad.lang') || 'en');

  // 3. Tab switching (Hero tabs & Examples tabs)
  document.querySelectorAll('.tabs, .ex-tabs').forEach(tabGroup => {
    const tabs = tabGroup.querySelectorAll('[role="tab"]');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetId = tab.getAttribute('aria-controls');
        const parentContainer = tabGroup.closest('.demo, .section') || document;

        // Deactivate siblings in this tablist
        tabs.forEach(t => t.setAttribute('aria-selected', 'false'));
        tab.setAttribute('aria-selected', 'true');

        // Show target panel, hide others
        const panels = parentContainer.querySelectorAll('[role="tabpanel"]');
        panels.forEach(p => {
          if (p.id === targetId) {
            p.hidden = false;
          } else if (Array.from(tabs).some(t => t.getAttribute('aria-controls') === p.id)) {
            p.hidden = true;
          }
        });
      });
    });
  });

  // 4. Copy button functionality
  document.querySelectorAll('.copy').forEach(btn => {
    btn.addEventListener('click', async () => {
      let codeToCopy = '';
      if (btn.dataset.copy) {
        codeToCopy = btn.dataset.copy;
      } else {
        const container = btn.closest('.code-panel, .ex-panel, .cell, .install');
        if (container) {
          const el = container.querySelector('code, pre');
          if (el) codeToCopy = el.innerText;
        }
      }

      if (codeToCopy) {
        try {
          await navigator.clipboard.writeText(codeToCopy.trim());
          btn.dataset.state = 'done';
          setTimeout(() => {
            delete btn.dataset.state;
          }, 1800);
        } catch (e) {
          console.error(e);
        }
      }
    });
  });

  // 5. Mobile header navigation toggle
  const menuBtn = document.getElementById('menuBtn');
  const siteHeader = document.getElementById('siteHeader');
  if (menuBtn && siteHeader) {
    menuBtn.addEventListener('click', () => {
      const open = siteHeader.getAttribute('data-open') === 'true';
      siteHeader.setAttribute('data-open', !open);
      menuBtn.setAttribute('aria-expanded', !open);
    });
  }

  // 6. Mobile docs sidebar toggle
  const docsAsideBtn = document.getElementById('docsAsideBtn');
  const docsAside = document.getElementById('docsAside');
  if (docsAsideBtn && docsAside) {
    docsAsideBtn.addEventListener('click', () => {
      const open = docsAside.getAttribute('data-open') === 'true';
      docsAside.setAttribute('data-open', !open);
    });
  }

  // 7. Docs ScrollSpy
  const docSections = document.querySelectorAll('.docs-article section');
  const docNavLinks = document.querySelectorAll('.docs-nav-link');
  const tocNavLinks = document.querySelectorAll('.toc-nav a');

  if (docSections.length > 0) {
    window.addEventListener('scroll', () => {
      let currentId = '';
      docSections.forEach(sec => {
        const top = sec.offsetTop - 100;
        if (window.pageYOffset >= top) {
          currentId = sec.getAttribute('id');
        }
      });
      if (currentId) {
        docNavLinks.forEach(l => {
          l.classList.toggle('active', l.getAttribute('href') === `#${currentId}`);
        });
        tocNavLinks.forEach(l => {
          l.classList.toggle('active', l.getAttribute('href') === `#${currentId}`);
        });
      }
    });
  }

})();

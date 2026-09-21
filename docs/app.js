/**
 * aioshad-py Documentation & Showcase Interactive Script
 */

(function () {
  'use strict';

  // 1. Particle Canvas Background Animation
  const canvas = document.getElementById('particle-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];
    const particleCount = 45;

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = Math.min(window.innerHeight, 750);
    }

    class Particle {
      constructor() {
        this.reset();
      }
      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.6;
        this.vy = (Math.random() - 0.5) * 0.6;
        this.radius = Math.random() * 1.8 + 0.8;
        this.alpha = Math.random() * 0.5 + 0.2;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
          this.reset();
        }
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(59, 130, 246, ${this.alpha})`;
        ctx.fill();
      }
    }

    function initParticles() {
      resize();
      particles = [];
      for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
      }
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      // Connect nearby particles
      for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();

        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 110) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(6, 182, 212, ${0.15 * (1 - dist / 110)})`;
            ctx.lineWidth = 0.75;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    initParticles();
    animate();
  }

  // 2. Interactive Code Sandbox Tabs
  const codeSnippets = {
    quickstart: `# Quickstart: Echo & Ping Selfbot
import asyncio
from aioshad import Client, F
from aioshad.filters import IsMe
from aioshad.types import Message

client = Client(session="my_account")

@client.on_message(F.text.startswith("echo "))
async def echo_handler(msg: Message):
    await msg.reply(f"📣 {msg.text[5:].strip()}")

@client.on_message(IsMe(), F.text == "!ping")
async def ping_handler(msg: Message):
    await msg.edit("🏓 Pong! aioshad is active.")

if __name__ == "__main__":
    client.run()`,

    routers: `# Modular Routers & Commands
from aioshad import Client, Dispatcher, Router
from aioshad.filters import Command, CommandObject, IsGroup
from aioshad.types import Message

router = Router(name="group_router")

@router.message(Command("start", prefix="/!"))
async def start_cmd(msg: Message, command: CommandObject):
    await msg.reply(f"Hello! Command: {command.command}")

@router.message(IsGroup(), Command("info"))
async def info_cmd(msg: Message):
    chat = await msg.get_chat()
    await msg.reply(f"Group: {chat.title} ({chat.members_count} members)")

dp = Dispatcher()
dp.include_router(router)
client = Client(session="my_account", dispatcher=dp)`,

    conversation: `# Linear Interactive Conversation
@client.on_message(Command("register"))
async def register_flow(msg: Message):
    async with client.conversation(msg.chat_guid, timeout=60) as conv:
        await conv.send_message("What is your name?")
        name_msg = await conv.get_response()
        
        await conv.send_message(f"Welcome, {name_msg.text}! How old are you?")
        age_msg = await conv.get_response()
        
        await conv.send_message(f"Registered: {name_msg.text} ({age_msg.text} y/o)")`,

    media: `# High-Speed Photos, Docs & Voice Notes
# Send photo with auto-generated thumbnail
await client.send_photo(chat_guid, "photo.jpg", caption="Sunset")

# Send document
await client.send_file(chat_guid, "report.pdf", caption="Q3 Audit")

# Send audio voice note
await client.send_voice(chat_guid, "voice.ogg")

# Download file from incoming message
if msg.file_inline:
    path = await client.download_file(msg.file_inline, "saved.jpg")`,

    voicechat: `# Group WebRTC Voice Chat Controls
# Start or join group voice chat
await client.create_voice_chat(group_guid)

# Join active voice chat
await client.join_voice_chat(group_guid, voice_chat_id)

# Set mic speaking state (True = Speaking)
await client.change_voice_chat_voice_status(group_guid, voice_chat_id, True)

# Get participant list
parts = await client.get_voice_chat_participants(group_guid, voice_chat_id)`
  };

  const sandboxTabs = document.querySelectorAll('.sandbox-tab');
  const sandboxPre = document.getElementById('sandbox-code');

  function renderCode(code) {
    if (!sandboxPre) return;
    // Simple syntax colorizer for Python keywords
    const formatted = code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/(#.*$)/gm, '<span class="syn-comm">$1</span>')
      .replace(/\b(import|from|async|await|def|if|return|class|with|as)\b/g, '<span class="syn-kw">$1</span>')
      .replace(/\b(Client|Dispatcher|Router|Message|Command|CommandObject|IsMe|IsGroup|F)\b/g, '<span class="syn-cls">$1</span>')
      .replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, '<span class="syn-str">$&</span>');
    sandboxPre.innerHTML = formatted;
  }

  sandboxTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      sandboxTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const snippetKey = tab.dataset.tab;
      if (codeSnippets[snippetKey]) {
        renderCode(codeSnippets[snippetKey]);
      }
    });
  });

  if (codeSnippets.quickstart) {
    renderCode(codeSnippets.quickstart);
  }

  // 3. Copy to Clipboard Functionality
  document.querySelectorAll('.copy-btn, .code-copy-floating').forEach(btn => {
    btn.addEventListener('click', async () => {
      let textToCopy = '';
      if (btn.dataset.copy) {
        textToCopy = btn.dataset.copy;
      } else {
        const container = btn.closest('.code-sandbox-card, .code-block, .install-pill');
        if (container) {
          const codeEl = container.querySelector('pre, .install-cmd');
          if (codeEl) textToCopy = codeEl.innerText;
        }
      }

      if (textToCopy) {
        try {
          await navigator.clipboard.writeText(textToCopy);
          const originalText = btn.innerHTML;
          btn.innerHTML = '✓ Copied!';
          btn.style.color = '#10b981';
          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.color = '';
          }, 2000);
        } catch (err) {
          console.error('Failed to copy', err);
        }
      }
    });
  });

  // 4. Documentation Sidebar Search
  const searchInput = document.getElementById('docsSearchInput');
  const navLinks = document.querySelectorAll('.sidebar-nav-link');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      navLinks.forEach(link => {
        const text = link.textContent.toLowerCase();
        const listItem = link.parentElement;
        if (!q || text.includes(q)) {
          listItem.style.display = '';
        } else {
          listItem.style.display = 'none';
        }
      });
    });
  }

  // 5. ScrollSpy for TOC & Sidebar Highlighting
  const sections = document.querySelectorAll('.docs-section');
  const tocLinks = document.querySelectorAll('.toc-link');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.pageYOffset >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    tocLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });

  // 6. Dual Language Toggle (EN / FA)
  const langToggle = document.getElementById('langToggle');
  const translations = {
    en: {
      dir: 'ltr',
      lang: 'en',
      navDocs: 'Docs',
      navFeatures: 'Features',
      navExamples: 'Examples',
      navGithub: 'GitHub',
      badgeStatus: 'v0.1.0 • High-Throughput Async Framework',
      heroTitlePrefix: 'Next-Generation',
      heroTitleHighlight: 'Self-Bot Framework',
      heroTitleSuffix: 'for Shad Messenger',
      heroDesc: 'Modern, fully asynchronous Python framework built on HTTP/2 multiplexing, reverse-engineered cryptography, and Aiogram-inspired dispatcher architecture.',
      btnGetStarted: 'Get Started',
      btnQuickstart: 'Quickstart Guide',
      searchPlaceholder: 'Search documentation...',
      langBtnText: 'فارسی'
    },
    fa: {
      dir: 'rtl',
      lang: 'fa',
      navDocs: 'مستندات',
      navFeatures: 'ویژگی‌ها',
      navExamples: 'نمونه‌ها',
      navGithub: 'گیت‌هاب',
      badgeStatus: 'نسخه ۰.۱.۰ • فریم‌ورک سریع و ناهمگام',
      heroTitlePrefix: 'نسل جدید',
      heroTitleHighlight: 'فریم‌ورک سلف‌بات',
      heroTitleSuffix: 'پیام‌رسان شاد',
      heroDesc: 'کتابخانه کاملاً آسنکرون و مدرن پایتون با اتصال پرسرعت HTTP/2، رمزنگاری بومی شاد و معماری الهام‌گرفته از aiogram.',
      btnGetStarted: 'شروع کنید',
      btnQuickstart: 'راهنمای سریع',
      searchPlaceholder: 'جستجو در مستندات...',
      langBtnText: 'English'
    }
  };

  let currentLang = localStorage.getItem('aioshad.lang') || 'en';

  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('aioshad.lang', lang);
    const t = translations[lang];
    document.documentElement.dir = t.dir;
    document.documentElement.lang = t.lang;

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      if (t[key]) el.textContent = t[key];
    });

    if (searchInput) searchInput.placeholder = t.searchPlaceholder;
    if (langToggle) langToggle.textContent = t.langBtnText;
  }

  if (langToggle) {
    langToggle.addEventListener('click', () => {
      applyLanguage(currentLang === 'en' ? 'fa' : 'en');
    });
    applyLanguage(currentLang);
  }

  // 7. Theme Toggle (Dark / Light)
  const themeToggle = document.getElementById('themeToggle');
  let currentTheme = localStorage.getItem('aioshad.theme') || 'dark';

  function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('aioshad.theme', theme);
    document.documentElement.dataset.theme = theme;
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
    applyTheme(currentTheme);
  }

  // 8. Mobile Navigation Drawer Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.querySelector('.docs-sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }

})();

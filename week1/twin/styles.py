"""Classic, elegant styling for the digital twin Gradio app.
Light mode: ivory + navy + antique gold.  Dark mode: midnight navy + gold.
app.py imports EXAMPLES, CSS and JS from here."""

EXAMPLES = [
    "Tell me about your background and experience.",
    "Which technologies do you work with?",
    "What are you looking for next in your career?",
    "How can I get in touch with you?",
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg: #f7f3ec;
  --surface: #fffdf9;
  --surface-2: #f1ebe0;
  --border: #e3d9c6;
  --text: #2b2a33;
  --muted: #8a8374;
  --navy: #1f2a44;
  --user-bg: #1f2a44;
  --user-text: #ffffff;
  --gold: #b8923a;
  --gold-soft: #e9d9b0;
  --shadow: 0 6px 24px rgba(31, 42, 68, 0.08);
}

body.dark {
  --bg: #12151f;
  --surface: #1a1f2e;
  --surface-2: #222839;
  --border: #2f364a;
  --text: #ece8df;
  --muted: #9a98a3;
  --navy: #c9a24b;
  --user-bg: #2c3a5e;
  --user-text: #ffffff;
  --gold: #c9a24b;
  --gold-soft: #4a4126;
  --shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
}

footer, .built-with, .show-api, .api-docs { display: none !important; }

html, body, gradio-app { background: var(--bg) !important; }

/* ---------- Page ---------- */
.gradio-container {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important;
  width: 100% !important;
  max-width: 820px !important;
  margin: 0 auto !important;
  padding: 40px 24px 56px !important;
}
.gradio-container .main, .gradio-container .contain, .gradio-container .wrap {
  width: 100% !important;
  max-width: 100% !important;
}
.gradio-container * { min-width: 0; }
.block, .form { background: transparent !important; box-shadow: none !important; border: 0 !important; }

/* ---------- Title ---------- */
.gradio-container h1 {
  font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
  color: var(--text) !important;
  font-size: 38px !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em !important;
  text-align: center !important;
  margin: 0 0 6px !important;
}
.gradio-container h1::after {
  content: "";
  display: block;
  width: 64px;
  height: 2px;
  background: var(--gold);
  margin: 14px auto 0;
}

/* ---------- Description under the title ---------- */
.gradio-container .prose p, .gradio-container .md p {
  text-align: center;
  color: var(--muted) !important;
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-size: 16px;
  margin: 12px 0 22px !important;
}

/* ---------- Hide the "Chatbot" label tab ---------- */
.chatbot > .block-label,
.chatbot > label,
.chatbot .label-wrap,
.chatbot .block-label,
.chatbot > .label-container { display: none !important; }

/* ---------- Chat frame ---------- */
.chatbot, .chatbot.block {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  box-shadow: var(--shadow) !important;
  min-height: 480px !important;
  overflow: hidden;
}
.chatbot .placeholder, .chatbot .placeholder * { color: var(--muted) !important; }

/* ---------- Message rows ---------- */
.message-row,
.message-row > div,
.message-row .role,
.message-wrap, .bubble-wrap {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.message-row .message,
.message-row .message-bubble,
.message-row .bubble {
  border: 0 !important;
  box-shadow: none !important;
  border-radius: 14px !important;
  padding: 10px 16px !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
}

/* your messages */
.message-row.user-row .message,
.message-row.user-row .message-bubble,
.message-row.user-row .bubble,
.message-row[data-role="user"] .message,
.message-row[data-role="user"] .message-bubble {
  background: var(--user-bg) !important;
  color: var(--user-text) !important;
}

/* the twin's messages */
.message-row.bot-row .message,
.message-row.bot-row .message-bubble,
.message-row.bot-row .bubble,
.message-row[data-role="assistant"] .message,
.message-row[data-role="assistant"] .message-bubble {
  background: var(--surface-2) !important;
  color: var(--text) !important;
  border-left: 3px solid var(--gold) !important;
}

/* gold stripe only on the outermost bubble */
.message-row.bot-row .message .message,
.message-row.bot-row .message .bubble,
.message-row.bot-row .message .message-bubble,
.message-row.bot-row .bubble .message,
.message-row.bot-row .bubble .bubble,
.message-row.bot-row .bubble .message-bubble,
.message-row.bot-row .message-bubble .message,
.message-row.bot-row .message-bubble .bubble,
.message-row.bot-row .message-bubble .message-bubble,
.message-row[data-role="assistant"] .message .message,
.message-row[data-role="assistant"] .message .bubble,
.message-row[data-role="assistant"] .bubble .message,
.message-row[data-role="assistant"] .bubble .bubble,
.message-row[data-role="assistant"] .message-bubble .message,
.message-row[data-role="assistant"] .message-bubble .bubble {
  border-left: 0 !important;
}

.message-row .message p,
.message-row .message-bubble p,
.message-row .bubble p,
.message-row .prose p {
  font-size: 15px !important;
  line-height: 1.6 !important;
  margin: 0 0 8px !important;
  color: inherit !important;
  font-style: normal !important;
  text-align: left !important;
}
.message-row .message p:last-child,
.message-row .message-bubble p:last-child,
.message-row .bubble p:last-child { margin-bottom: 0 !important; }

.message-row .message *,
.message-row .message-bubble *,
.message-row .bubble * {
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
  color: inherit !important;
}
.message-row .message a, .message-row .message-bubble a {
  color: var(--gold) !important;
  text-decoration: underline;
}

/* ---------- Input ---------- */
textarea, input[type="text"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Inter', -apple-system, sans-serif !important;
  font-size: 15px !important;
  padding: 14px 16px !important;
  min-height: 52px !important;
  box-shadow: var(--shadow) !important;
}
textarea:focus, input[type="text"]:focus {
  border-color: var(--gold) !important;
  outline: none !important;
  box-shadow: 0 0 0 3px var(--gold-soft) !important;
}
textarea::placeholder, input::placeholder { color: var(--muted) !important; }

/* ---------- Buttons ---------- */
button {
  font-family: 'Inter', -apple-system, sans-serif !important;
  border-radius: 12px !important;
  transition: all 0.15s ease;
  cursor: pointer;
}

button.primary,
button[variant="primary"],
button.submit,
button.submit-button,
.submit-button,
button.lg.primary {
  background: var(--navy) !important;
  border: 1px solid var(--navy) !important;
  color: #ffffff !important;
  min-height: 52px !important;
  padding: 0 18px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
body.dark button.primary,
body.dark button.submit,
body.dark button.submit-button,
body.dark .submit-button { color: #12151f !important; }

button.primary:hover,
button.submit:hover,
.submit-button:hover {
  background: var(--gold) !important;
  border-color: var(--gold) !important;
  color: #ffffff !important;
}

button.submit svg, button.submit-button svg, .submit-button svg,
button.primary svg {
  width: 18px !important;
  height: 18px !important;
  margin: 0 auto !important;
  display: block !important;
  color: inherit !important;
  fill: currentColor !important;
  stroke: currentColor !important;
}

/* ---------- Example questions ---------- */
.examples, .examples-holder, [data-testid="examples"] {
  background: transparent !important;
  padding: 0 !important;
  margin-top: 18px !important;
}
.examples table, .examples-table { background: transparent !important; border: 0 !important; }
.examples button, .example, .examples td button, [data-testid="examples"] button {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  color: var(--text) !important;
  font-size: 13.5px !important;
  font-weight: 400 !important;
  padding: 9px 18px !important;
  text-align: left !important;
  min-height: 0 !important;
  box-shadow: none !important;
}
.examples button:hover, .example:hover, [data-testid="examples"] button:hover {
  border-color: var(--gold) !important;
  color: var(--gold) !important;
  background: var(--surface) !important;
}

/* ---------- Small icon buttons (copy, retry, clear) ---------- */
.icon-button, .chatbot .icon-button {
  color: var(--muted) !important;
  background: transparent !important;
  border: 0 !important;
  min-height: 0 !important;
  padding: 4px !important;
}
.icon-button:hover, .chatbot .icon-button:hover { color: var(--gold) !important; }

/* ---------- Scrollbar and selection ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }
::selection { background: var(--gold); color: #ffffff; }

/* ---------- Mobile ---------- */
@media (max-width: 640px) {
  .gradio-container { padding: 24px 14px 40px !important; }
  .gradio-container h1 { font-size: 28px !important; }
}
"""

JS = """
() => {
  document.title = 'Digital Twin';

  const focusInput = () => {
    const areas = document.querySelectorAll('textarea');
    if (areas.length) areas[areas.length - 1].focus();
  };
  setTimeout(focusInput, 300);

  // Put the cursor back in the message box after the twin finishes replying
  const watchTextarea = (area) => {
    if (area.dataset.twinWatched) return;
    area.dataset.twinWatched = '1';
    let wasDisabled = area.disabled || area.readOnly;
    new MutationObserver(() => {
      const isDisabled = area.disabled || area.readOnly;
      if (wasDisabled && !isDisabled) area.focus();
      wasDisabled = isDisabled;
    }).observe(area, { attributes: true, attributeFilter: ['disabled', 'readonly'] });
  };

  const scan = () => document.querySelectorAll('textarea').forEach(watchTextarea);
  setTimeout(scan, 500);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
}
"""
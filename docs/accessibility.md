# Accessibility Features – IOGT Uzbekistan
## Change Documentation & Setup Guide

**Prepared for:** UNICEF Uzbekistan – IOGT Uzbekistan IT Team  
**Date:** May 2025  
**Prepared by:** UNICEF Uzbekistan Content Team

---

## Table of Contents

1. [Summary of Changes](#1-summary-of-changes)
2. [Files Changed / Added](#2-files-changed--added)
3. [Accessibility Features Implemented](#3-accessibility-features-implemented)
4. [Technical Details](#4-technical-details)
5. [How to Run the Project on Your Computer (Step-by-Step)](#5-how-to-run-the-project-on-your-computer-step-by-step)
6. [How to Test the Accessibility Features](#6-how-to-test-the-accessibility-features)
7. [FAQ](#7-faq)

---

## 1. Summary of Changes

We added a **self-contained accessibility panel** to the IOGT Uzbekistan website.  
A small floating button (wheelchair/person icon, purple) appears in the **bottom-right corner** of every page. Clicking it opens a slide-in panel with 11 accessibility options. All settings are remembered automatically in the visitor's browser, so they persist across page visits.

**No changes were made to:**
- Python / Django / Wagtail backend code
- Database models or migrations
- Existing CSS files
- Any existing JavaScript files

---

## 2. Files Changed / Added

### 2.1 New Files (created)

| File | Purpose |
|------|---------|
| `iogt/static/css/accessibility.css` | All styles for the accessibility panel and the visual effects (invert colours, greyscale, big cursor, etc.) |
| `iogt/static/js/accessibility.js` | All JavaScript logic – builds the panel, saves settings to the browser, applies CSS classes |
| `docs/accessibility.md` | This documentation file |

### 2.2 Modified Files (2 lines changed)

#### `iogt/templates/base.html`

Two lines were added. No existing lines were removed or changed.

**Line added in `<head>` section** (after the existing `iogt.css` link):
```html
{# Accessibility panel styles #}
<link rel="stylesheet" type="text/css" href="{% static 'css/accessibility.css' %}">
```

**Line added before `</body>`** (after the `{% block extra_js %}` block):
```html
{# Accessibility panel – loaded last so it overlays everything #}
<script src="{% static 'js/accessibility.js' %}"></script>
```

---

## 3. Accessibility Features Implemented

The panel includes the following 11 features:

### 3.1 Text Size
- **Increase Text Size** – Makes all text on the page larger (6 steps: 85 % → 92 % → **100 %** → 112 % → 125 % → 140 %)
- **Decrease Text Size** – Makes all text smaller

### 3.2 Text Spacing
- **Increase Text Spacing** – Adds extra letter-spacing and word-spacing to all text (3 steps: Default → Wide → Wider)
- **Decrease Text Spacing** – Reduces spacing back

### 3.3 Line Height
- **Increase Line Height** – Increases the vertical space between lines of text (3 steps: Default → Tall → Extra Tall)
- **Decrease Line Height** – Reduces it back

### 3.4 Invert Colours
- Flips all colours on the page (like a "dark mode" but inverted). Images and videos are re-inverted so they still look natural.

### 3.5 Grey Hues
- Removes all colour from the page (full greyscale). Useful for users with colour-vision deficiency.

### 3.6 High Contrast
- Forces a black background with white text and yellow links – maximum contrast for users with low vision.

### 3.7 Underline Links
- Adds an underline to every link on the page, making them easier to identify without relying on colour alone.

### 3.8 Big Cursor
- Replaces the mouse cursor with a large, high-visibility cursor. Useful for users with motor difficulties or low vision.

### 3.9 Reading Guide
- Displays a yellow horizontal band that follows the mouse cursor, acting as a ruler to help users keep their place while reading. Useful for users with dyslexia or ADHD.

### 3.10 Highlight Focus
- Adds a bright orange outline around any element that has keyboard focus. This makes it much easier to see where you are when navigating with the keyboard (Tab key).

### 3.11 Dyslexia-Friendly Font
- Switches all text to **OpenDyslexic** – a free, open font designed to help people with dyslexia read more easily. The font is loaded from a CDN (jsDelivr) only when the user activates this option – it does not slow down normal page loads.

### 3.12 Reset All
- A "Reset all" button in the panel header restores everything to the default state and clears saved settings.

---

## 4. Technical Details

### Technology used
- **Pure CSS** for all visual effects (no external CSS libraries)
- **Vanilla JavaScript (ES6)** for the panel logic (no external JS libraries)
- **OpenDyslexic font** loaded on-demand from jsDelivr CDN only when the user turns on the dyslexia font feature
- **localStorage** to persist user preferences across pages and browser sessions

### How settings are saved
Settings are saved in the browser's `localStorage` under the key `iogt_a11y` as a JSON object. This means:
- Settings survive page navigation
- Settings survive browser restart
- Each user's settings are private to their own browser
- The server never receives or stores accessibility preferences

### RTL (right-to-left) language support
The floating button and slide-in panel automatically move to the **left side** of the screen when the website is in a right-to-left language (e.g. Arabic, Uzbek in Arabic script). This is handled by CSS targeting the existing `body.rtl` class that the website already uses.

### Reduced-motion support
The panel animation respects the user's operating system "reduce motion" preference (`prefers-reduced-motion: reduce`). If the user has enabled this OS-level setting, the panel appears instantly without animation.

### No backend changes required
Because the feature is entirely CSS + JavaScript served as static files, there is no need to:
- Run database migrations
- Restart the Django/Wagtail server (after `collectstatic` has been run)
- Change any Python code
- Change any Wagtail settings

### collectstatic
After deploying the new files, the IT team must run Django's `collectstatic` command so the new CSS and JS files are picked up by the web server:

```bash
python manage.py collectstatic --noinput
```

Or with Docker:
```bash
docker compose run --rm django python manage.py collectstatic --noinput
```

---

## 5. How to Run the Project on Your Computer (Step-by-Step)

> **You do not need to know Python.** Everything runs inside Docker containers. You only need to install Docker.

### Step 1 – Install Docker Desktop

1. Go to **https://www.docker.com/products/docker-desktop/**
2. Download **Docker Desktop** for your operating system (Windows or Mac)
3. Install it and start it. You will see the Docker whale icon in your taskbar/menu bar when it is running.

> On Windows, Docker Desktop may ask you to install "WSL 2" (Windows Subsystem for Linux). Follow the on-screen instructions – it is safe and required.

### Step 2 – Get the project files

If you received the project as a ZIP file:
1. Unzip the file to a folder, for example `C:\projects\iogt-main\` on Windows or `~/projects/iogt-main/` on Mac.

If you are working from GitHub (the IT team may prefer this):
1. Open **Terminal** (Mac) or **Command Prompt / PowerShell** (Windows)
2. Run:
   ```
   git clone https://github.com/unicef/iogt.git
   cd iogt
   ```

### Step 3 – Open a Terminal in the project folder

**Windows:**  
Open File Explorer, navigate to the project folder, then in the address bar type `cmd` and press Enter.

**Mac:**  
Open Terminal, then type `cd ` (with a space), drag the project folder onto the Terminal window, and press Enter.

### Step 4 – Create the database (first time only)

Run this command (copy and paste it exactly):

```
docker compose run --rm django python manage.py migrate
```

This will take a few minutes the first time. Docker will download everything needed automatically.

### Step 5 – Create an admin account (first time only)

```
docker compose run --rm django python manage.py createsuperuser
```

It will ask you for a username, email, and password. Remember these – you will use them to log into the admin area.

### Step 6 – (Optional) Add test content

```
docker compose run --rm django python manage.py create_initial_data
docker compose run --rm django python manage.py autopopulate_main_menus
```

### Step 7 – Start the website

```
docker compose up -d
```

Wait about 30 seconds, then open your browser and go to:

- **Website:** http://localhost:8000/
- **Admin panel:** http://localhost:8000/admin/ (use the username/password from Step 5)

### Step 8 – See the accessibility button

Open http://localhost:8000/ in your browser. You should see a **purple circle button** in the bottom-right corner of the page. Click it to open the Accessibility Options panel.

### Step 9 – Stop the website

When you are done:

```
docker compose down
```

### Step 10 – Start again later

Next time you want to run the site, you only need Step 3 and Step 7 (you do not need to repeat Steps 4–6).

---

## 6. How to Test the Accessibility Features

After starting the website (see Section 5):

1. Open http://localhost:8000/ in your browser
2. Click the **purple button** in the bottom-right corner
3. The "Accessibility Options" panel will slide in from the right
4. Test each feature:

| Feature | What to look for |
|---------|-----------------|
| Text Size (+) | All text on the page gets bigger |
| Text Size (−) | All text gets smaller |
| Text Spacing (+) | Letters and words are further apart |
| Line Height (+) | Lines of text have more space between them |
| Invert Colours | Page colours flip (dark background, light text) |
| Grey Hues | Page becomes black and white |
| High Contrast | Page goes fully black with white text and yellow links |
| Underline Links | All links now have underlines |
| Big Cursor | Your mouse cursor becomes large and bold |
| Reading Guide | A yellow band follows your mouse vertically |
| Highlight Focus | Press Tab – you will see an orange box around focused items |
| Dyslexia Font | All text changes to the rounded OpenDyslexic font |
| Reset All | Everything returns to normal |

5. Reload the page – your settings should be **remembered automatically**
6. Close and re-open the browser – settings should still be remembered

---

## 7. FAQ

**Q: Will this slow down the website?**  
A: No. The CSS file is small (~5 KB) and the JavaScript file is small (~7 KB). The OpenDyslexic font is only loaded if the user explicitly enables the dyslexia font option.

**Q: Does this work on mobile phones?**  
A: Yes. The floating button and panel are fully responsive. On very small screens the panel takes up the full width.

**Q: What happens if a user does not have JavaScript?**  
A: The accessibility button will not appear. This is acceptable because a very small percentage of users have JavaScript disabled, and the rest of the website already requires JavaScript to function (as noted in the existing `<noscript>` block in `base.html`).

**Q: Will the settings be shared between users on the same computer?**  
A: No. Each browser profile has its own `localStorage`. Settings are per-person, per-browser.

**Q: Can we translate the panel labels into Uzbek or Russian?**  
A: Yes. The label text is in `iogt/static/js/accessibility.js`. Search for strings like `'Accessibility Options'`, `'Text Size'`, etc. and replace them with translated versions. If you need help with this, please contact the team who prepared this documentation.

**Q: The IT team asked about `collectstatic` – what is that?**  
A: Django does not serve static files (CSS, JS, images) directly in production. It copies them to a special folder using the `collectstatic` command. The IT team will know how to run this as part of their deployment process.

---

*End of documentation*

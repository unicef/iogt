# IOGT Accessibility — Integration Guide for the IT Team

This package adds an **accessibility options panel** to the IOGT website.
It is **pure front-end** (CSS + JavaScript + a bundled font). **No Python,
database, settings, or dependency changes are required.**

> IMPORTANT: Apply these on top of your CURRENT codebase. Do **not** replace
> `base.py`, `production.py`, `media-video.html`, or `range_request_middleware.py`
> — those are unrelated to accessibility.

---

## 1. Files to add (copy as-is into the project)

```
iogt/static/css/accessibility.css
iogt/static/js/accessibility.js
iogt/static/fonts/opendyslexic/OpenDyslexic-Regular.woff2
iogt/static/fonts/opendyslexic/OpenDyslexic-Bold.woff2
```

These are all new files — they don't overwrite anything.

---

## 2. Edit `iogt/templates/base.html` — add 2 lines (do NOT replace the file)

**a) In the `<head>`**, near the other stylesheet links, add:

```django
<link rel="stylesheet" type="text/css" href="{% static 'css/accessibility.css' %}?v=10">
```

**b) Just before the closing `</body>` tag**, add:

```django
<script src="{% static 'js/accessibility.js' %}?v=10"></script>
```

(The `?v=10` is a cache-buster; bump the number whenever the files change so
browsers fetch the new version.)

> Make sure `{% load static %}` is already present at the top of the template
> (it is, in the standard IOGT base template).

---

## 3. (Optional, recommended) make `<html lang>` reflect the active language

The panel auto-detects language from the URL prefix (`/ru/`, `/kaa/`, `/uz/`),
so this step is optional. But for correct screen-reader behaviour, you may set
the real language on the `<html>` tag. At the top of `base.html` (after
`{% load %}`), add:

```django
{% get_current_language as A11Y_LANGUAGE_CODE %}
```

and change:

```django
<html class="no-js" lang="en">
```
to:
```django
<html class="no-js" lang="{{ A11Y_LANGUAGE_CODE|default:'en' }}">
```

`{% get_current_language %}` comes from the `i18n` tag library, already loaded
in the IOGT base template.

---

## 4. Collect static files & deploy

After adding the files, run your normal static pipeline:

```bash
python manage.py collectstatic --noinput
```

Then deploy/restart as usual. No migrations, no new packages.

---

## 5. What it does

A floating button (universal accessibility symbol, bottom-left) opens a panel with:

- Text: size (70–200%, scales the whole page), spacing, line height, dyslexia
  font, legible font
- Colour & vision: invert, grey hues, high contrast, low/high saturation
- Reading & focus: reading guide, reading mask, highlight focus, highlight hover
- Navigation & content: underline links, highlight links, highlight headings,
  big cursor, hide images, stop animations
- One-click profiles: Vision Impaired, ADHD Friendly, Seizure Safe, Cognitive

Settings persist per visitor via `localStorage`. The panel UI is fully translated
into **Russian, Uzbek, and Karakalpak**, chosen automatically from the URL
language prefix.

---

## 6. Notes

- **No external dependencies.** The OpenDyslexic font is bundled locally; nothing
  is loaded from a CDN. Works offline and behind firewalls.
- **Self-contained.** All CSS is scoped to the panel's own elements/classes
  (`#a11y-panel`, `#a11y-toggle-btn`, `.a11y-*`). It will not affect existing
  site styles. (One defensive reset neutralises the site's global `button`
  styling inside the panel only.)
- **To edit translations**, see the `TRANSLATIONS` block at the very top of
  `accessibility.js` — labelled by language code.
- **Mobile:** on screens ≤480px the panel becomes a bottom sheet with a sticky
  header.

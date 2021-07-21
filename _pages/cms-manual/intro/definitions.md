---
title: Definitions
permalink: /cms-manual/intro/definitions/
---

There are several terms and concepts that the IoGT CMS relies on. These terms are presented here.

<dl class="row">
    {% for item in site.data.definitions %}
        <dt class="col-lg-3" id="{{ item.title | slugify}}">{{ item.title }}</dt>
        <dd class="col-lg-9" id="{{ item.title | slugify}}-desc">{{ item.desc | markdownify }}</dd>
    {% endfor %}
</dl>
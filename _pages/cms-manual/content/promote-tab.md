---
title: The Promote Tab
permalink: /cms-manual/content/promote-tab/
---

The Promote tab is one of the tabs prominent at the top of the Edit screen on any section, subsection or article. The tabs are:

- Content: where you build the content of the page itself
- Promote: where you can view metadata information about pages
- Settings: where you can schedule pages to be published/unpublished at a future date and time.
- Comments: where you can enable or disable user comments on the page (_availble for Articles only_)

The Promote tab enables you to view and edit the Common Page Configuration and the Metadata for the page.

## Common Page Configuration

Here, you can set all the metadata (which is essentially data about data) for the page. Below is a description of all default fields in the Promote tab and what they do.

- **Slug**: The last part of the web address for a page. E.g. the slug for a Blog page called ‘The best things on the web’ would be the-best-things-on-the-web (www.example.com/blog/the-best-things-on-the-web). This is automatically generated from the main page title set in the Content tab. This can be overridden by adding a new slug into the field. Slugs should be entirely lowercase, with words separated by hyphens (-).
- **Page title**: An optional, search engine-friendly page title. This is the title that appears in the tab of your browser window. It is also the title that would appear in a search engine if the page was returned in a set of search results.
- **Show in menus**: Ticking this box will ensure that the page is included in automatically-generated menus on your site. Note: Pages will only display in menus if all of its Parent pages also have Show ticked in menus.
- **Search description**: This field allows you to add text that will be displayed if the page appears in search results. This is especially useful to distinguish between similarly-named pages.

## Metadata

The metadata has a single field: a list of comma-separated tags to assign to the article, section, or subsction. These tags can be used throughout Wagtail to create configurations that affect only a certain tag or group of tags.

{% include figure.html src="/assets/img/docs/promote-tab.png" alt="The Promote Tab" caption="The Promote Tab" %}
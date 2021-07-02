---
title: Navigating the CMS
permalink: /cms-manual/intro/navigating-wagtail/
---

Once you have logged in, you will be redirected to the CMS home page, also known as the Dashboard.

{% include figure.html src="/assets/img/docs/wagtail-dashboard.png" alt="Wagtail Dashboard" caption="Wagtail dashboard." %}

Navigate to the Dashboard by clicking on the bird icon on the top-left of the screen (this is the Wagtail logo).

- The Dashboard shows the number of pages, images, documents and associated languages currently stored on Wagtail.
- It shows pages awaiting moderation (if you have permission to view this), as well as your most recent edits.
- The stats at the top of the page describe the total volume of content on Wagtail.
- Clicking on the name of a page will take you to its Edit page interface.
- Clicking Approve or Reject will either change the page status to Live or return the page to Draft status. (An email will be sent to the creator of the page letting them know the decision.)
- The Parent column of a page awaiting moderation tells you its Parent page. Clicking the Parent page will take you to the Edit page. (Pages and sub-pages on Molo are called Parent and Child pages. This describes their relationship to each other. The Parent page is on a higher navigational level than the Child page. Read the article Structuring your content for more information on Parent pages.) 
- Most Recent Edits displays the five pages that have been edited most recently.
- The Date column shows you the date when the page was last edited. Hover your mouse over the date for more detailed info.
- The Status column will indicate one of the following:
    - Live: the page is accessible to site visitors.
    - Draft: the page is not yet live (it is unpublished).
    - Live + Draft: a version of the page is live, but a newer version is in Draft mode.
- You can return to the Dashboard at any time by clicking the Wagtail logo on the top-left of the screen.

## The Pages menu

The Pages Menu enables quick navigation from the highest to the lowest level of the site. Navigation using this menu enables you to move past a navigational level by clicking on the right arrow - or to click onto a navigational level by clicking its name. You can also navigate back by clicking the name of the containing folder above the list.

The top level of the Pages menu will be the different languages your country's site is available in. For example, the site shown below is available in both English
and in French. 

{% include figure.html src="/assets/img/docs/pages-top-level.png" alt="Pages menu" caption="Wagtail Pages menu. Notice that this site has two languages: English and French." %}

**Here's what you need to know:**
- Click the Explorer button in the sidebar to access the Menu.
- Clicking the name of a page will take you to the Pages view for the Banner, Section, Footer pages or Polls _within that page_. 
- Clicking the right arrow displays the pages and enables you to navigate through the content structure.
- The more right arrows you click, the further down the content structure you move.

## The Pages view

As noted above, the root Pages view contains the different language versions your country site is available in. Any child pages created here will not be accessible from any URL; you must create child pages within an existing site _not the root_.

{% include figure.html src="/assets/img/docs/pages-root.png" alt="Pages root view" caption="Pages root view. You should not create child pages here." %}

From the Pages view, you can navigate to any immediate child Index. An Index group similar content. Some common Indicies you will be using include:
- Polls
- Sections
- Footer
- Banners

These Indicies will be covered in detail in sepeate sections of this documentation.

**Here's what you need to know:**

Polls, Footer Page, Sections and Banner are displayed below the breadcrumb (the row of page names beginning with the folder icon). Each section is also a page (in this case the Home page). Clicking the title of the section takes you to the Edit screen for the page.

As you move down through the site, the breadcrumb will display the path you have taken. Clicking on the page titles in the breadcrumb will take you to its Pages view. In the image below, the breadcrumbs are 'Kenya Internet of Good Things (French)' > Sections > COVID-19 > Sur la plage'. Notice that this Section does not contain any further sub-Section; all of the content here are Articles. Also notice at the top of the screen, you can see the breadcrumbs (trail of pages) navigated to reach this Section view.

{% include figure.html src="/assets/img/docs/pages-breadcrumb.png" alt="Pages breadcrumb and Section view" caption="Pages breadcrumb and Section view. In this example,  we have naviagated through 'Kenya Internet of Good Things (French)' > Sections > COVID-19 > Sur la plage, where we now are looking at the Article content within the 'Sur la plage' section." %}

Just below the title of the Section, there are several toolbar buttons, each with a different function that will be explained briefly here, and in more depth in separate sections of this documentation:

- Edit: Edit properties of the parent Section (in the image above, the "Sur la plage" section)
- View Live: View the production version of the site, as a user would see
- Add child page: Adding a new child page from one of six different types:
    - Article
    - Home page
    - Poll
    - Quiz
    - Section
    - Survey
- More
    - Move: Change the parent page of the currently selected Section (example: Sur la plage)
    - Copy: Duplicate the current Section
    - Delete: Complete remove the current section and all of its subpages
    - Unpublish: Disallow users from accessing this Section from the live site, optionally disallowing access to subpages. _Note: if access to subpages is **not** removed, they will become_ orphaned _meaning that they can be accessed by users, but only through direct URL._
    - History: View a log of the actions taken on this Section

Hovering over the right edge of a child page from this view reveals a plus button. Clicking on this plus button allows you to add a child page to that subpage (not the Section currently viewed, which in the example above is "Sur la plage").

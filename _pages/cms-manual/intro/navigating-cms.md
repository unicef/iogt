---
title: Navigating the CMS
permalink: /cms-manual/intro/navigating-wagtail/
---

Once you have logged in, you will be redirected to the CMS home page, also known as the Dashboard.

{% include figure.html src="/assets/img/docs/wagtail-dashboard.png" alt="Wagtail Dashboard" caption="Wagtail dashboard. On the left is the Main Menu which is used to nagivate to and edit various parts of the CMS. At the top of the Dashboard shows the numbers of different types of content. Below these counts will be a list of Pages awaiting review. Below this list will be a second list of Pages which you most recently edited, if any." %}

You can return to the Dashboard at any time by clicking the Wagtail logo.

- The Dashboard shows the number of Pages, images, documents and associated languages currently stored on Wagtail.
- The Dashboard will also alert you to a Wagtail version update, if applicable. System administrators will determine when the best time to update is.
- If you are authorized to moderate/review Pages, there will be a list of Pages awaiting your approval. Hovering over the title of the Page will give you several options:
  - Request changes - reject the changes and a comment explaining why
  - Approve - approve the changes and publish the Page
  - Approve with comment - approve the changes and publish the Page, adding a comment
  - Edit - edit the Page yourself
  - Preview - preview the changes on the frontend of the site
- If you have recently edited Pages, there will also be a list of your 5 most-recently edited Pages
- Clicking on the title of any Page in the Dashboard will take you to its Edit interface
- Each of the Page lists on the Dashboard also have a status.
  - Pages awaiting review will show the review status
  - Pages you have recently edited will show whether it is Live, Draft, or Live + Draft (indicating the Page is published but newer revisions are in a Draft state)

## The Pages menu

The Pages Menu enables quick navigation through the levels of the site. Navigation using this menu enables you to move past a navigational level by clicking on the right arrow - or to open a navigational level by clicking its name. You can also navigate back by clicking the name of the containing folder above the list.

The top level of the Pages menu will be the different languages your country's site is available in. For example, the site shown below is available in both English and in French. 

{% include figure.html src="/assets/img/docs/pages-top-level.png" alt="Pages menu" caption="Wagtail Pages menu. Notice that this site has two languages: English and French." %}

{% include figure.html src="/assets/img/docs/pages-hierarchy.png" alt="Pages hierarchy diagram" caption="This is the pages hierarchy. Remember, Sections can be infinitely nested and can contain any Page type except Banner Pages and Index Pages. There can also be as many Site Languages as required." %}

**Here's what you need to know:**
- Click the Pages button in the sidebar to access the Menu.
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

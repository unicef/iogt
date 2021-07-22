---
title: Creating Sections
permalink: /cms-manual/content/creating-sections/
---

Content structure builds the navigation for the end user. Sections, subsections and articles are the terms best used to describe how your content can be structured.

On the IoGT Wagtail CMS, the terms Parent and Child describe the navigational relationship between any higher page (or section) and lower page (or subsection). On the CMS, a Child page becomes a Parent page when an additional navigation level is created below it and populated with additional Child pages. The Article is the last in the lineage.

Adding main sections to your site is like creating content 'buckets' for your content. Inside a main section, you can put more 'buckets' (subsections) - and, inside of these, your articles.

If you have a limited amount of content, you may only need to create sections for your articles without adding subsections.

Typically a website has minimum three navigational levels, but it is up to you how many you want:

_Section > Subsection > Article;_ or,

_Parent > Parent (Child of a Parent) > Child._

And in the example below: _Sport > Soccer > Doe Injured._

{% include figure.html src="/assets/img/docs/pages-hierarchy.png" alt="Pages hierarchy diagram" caption="This is the pages hierarchy. Remember, Sections can be infinitely nested and can contain any Page type except Banner Pages and Index Pages. There can also be as many Site Languages as required." %}

{% include figure.html src="/assets/img/docs/subsection-hierarchy.png" alt="Example of a subsection hierarchy" caption="Example of a subsection hierarchy" %}

On Wagtail, **a section is a Content Channel**, such as "Facts for Life" or "Early Life Tips". **A subsection is a category**, such as "Facts for New Moms". Subsections can nest as deep as content organizers would like. **Articles** are always children of subsections, though they can appear at any nesting depth.

{% include figure.html src="/assets/img/docs/subsection-hierarchy-example.png" alt="Subsection hierarchy in IoGT" caption="IoGT site demonstration of the subsection hierarchy. In this situation, 'Facts for Life' is the Section/Content Channel, 'About Facts for Life' and 'Facts For: New Moms' are both subsections/categories, and 'Birth and family life planning' and 'Having a baby and keeping it healthy' are Articles under the 'Facts For: New Moms' subsection." %}

## Creating Subsections

- To create a section, navigate through Pages > Site language > Sections
  - To create a subsection, continue selecting deeper subsections as required. Your new subsection will be contained within the subsection of your choice. The process for creating a Section versus a subsection is the same.

{% include figure.html src="/assets/img/docs/section-view.png" alt="Sections root view" caption="This is the Sections root. Any Sections created here will be parent Sections/Content Channels. To create a subsection, keep navigating down a Section." %}

- Next, select `ADD CHILD PAGE`. The only required field is the title, as indicated by the red asterisk. However, it is recommend to add a section description as well.

{% include figure.html src="/assets/img/docs/new-section.png" alt="Adding a new section" caption="Adding a new Section/Content Channel. The title field is required, but the description field is highly recommended." %}

- Main sections or content channels (e.g Facts For Life, Connect Smart, Your rights etc…) will always be displayed on the Home page. Your readers will use these sections (or categories) to navigate through your content.
- For advanced settings click on Promote to adjust the URL slug page title, search descriptions
- Click on Settings to schedule the publishing / unpublishing of this page at a future date and time of your choice.
- Once you have completed all the required fields, select Publish from the dropdown menu at the bottom. Choose Preview if you’d like to see what it will look like first.
- This section will now be listed under Sections on the Main page, where you can navigate your list of sections.
- Hover over the section title to edit, view live, move to another section or unpublish.
- There is no limit to the number of main sections you can add to your site. However, because these will be displayed on the Home page as your site Menu items, try not to exceed 4 main sections or content categories.
- To create a section under a section (a subsection or a category) you can add a Child page to that section.
- To add a child page, hover over the section title where a button bar will be displayed.

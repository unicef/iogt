---
title: Creating Articles
permalink: /cms-manual/content/creating-articles/
---

There are three core components of the Article:

1. Title: The title of the article
2. Lead image: The "thumbnail" image that is associated with the article
3. Body: The main content of the article

## Adding articles to a section/subsection

- Navigate to either the section or subsection under which the article must appear and click Add Child Page.
- Select Article as the type of of page that you wish to create and provide a title and image. (Information on how to add images to Wagtail will be provided in a separate section.) 
- In the article body, you will see a + sign. Click on this to reveal the Rich Text Toolbar. This toolbar offers a range of editorial tools you can use to create headings, paragraphs, add images, bulleted or unordered lists and numbered lists. You can also add links to other articles or pages within your site by selecting the 'page' option.

{% include figure.html src="/assets/img/docs/rich-text-toolbar.png" alt="Rich Text Toolbar" caption="Click the + button to open the Rich Text Toolbar."%}

- For advanced settings, click on Promote to adjust the URL slug page title, search descriptions. The Promote tab also lets you promote (or feature) an article to the Home page or other Section landing pages of the site. Find out more about featuring articles under the Promote Tab
- If you want to add a link to an external page, you can use this mark down: example `[link](http://www.example.com/)`
- Important note : On Free Basics your end user could incur data charges if you link them to a page outside of the Free Basics App so it’s a good idea to put (data charges may apply) next to the link so people are aware.
- Click on Settings to schedule the publishing / unpublishing of this page at a future date and time of your choice. 
- Once you have completed all the main required fields, select Publish from the dropdown menu at the bottom. Choose Preview if you’d like to see what it will look like first.
- This article will now be listed within the section (or category) selected.
- Navigate to this section to view all its articles.
- Hover over the article title to edit, view live, move to another section (or category) or unpublish.

{% include figure.html src="/assets/img/docs/article-publishing-options.png" alt="Article publishing options" caption="Article publishing options" %}

## Article content formatting table

<table class="table">
    <thead>
        <tr>
            <th scope="col">Action</th>
            <th scope="col">Markdown Syntax</th>
            <th scope="col">Example</th>
        </tr>
    </thead>
    <tbody>
    {% for row in site.data.markdown_syntax %}
        <tr>
            <th scope="col">{{ row.Action }}</th>
            <td>{{ row.Markdown }}</td>
            <td>{{ row.Example | xml_escape }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
---
title: Changing Section Colors
permalink: /cms-manual/content/section-colors/
---

Each content channel (Section) can have a color associated with it to help differentiate it between other sections.

To change colors of the different Sections, navigate to the Section you would like to change from the Pages menu. Then click the Section title. In the example below, the Section `COVID-19` is selected.

{% include figure.html src="/assets/img/docs/section-view.png" alt="Section view" caption="This is the Section view. Click on the title of the section whose color you want to change." %}

On the Section editing page, make sure you are on the `Content` tab. You can check this by clicking `Content` just below the Section title and publishing date. Then scroll down to the `Color` option. This color setting requires a hexadecimal color code. To get the hex color code, use the [Google Color Picker tool](https://www.google.com/search?q=color+picker). On the Google Color Picker, select the hue from the horizontal slider just below the color field. Then select the specfic color from this hue by clicking in the color field. A sample of color you have chosen will appear on the left of the color field. Once you are satisfied with your color, copy the text in the `HEX` textbox, _**but do not copy the pound sign (#)**_.

{% include figure.html src="/assets/img/docs/google-color-picker.png" alt="Google Color Picker" caption="Google Color Picker. Step 1: select the hue from the horizontal slider (circled in red). Step 2: Select the specfic color from the color field (right cyan arrow). A preview of the selected color is shown on the left of color field (left cyan arrow). Step 3: Copy the hex code, leaving out the pound sign (circled in green)." %}

Finally, navigate back to Wagtail and paste the hex code into the `Color` field on the Section editing page. Capitalize all letters. For example, the color in the image above (`#92c92a`) should be pasted into Wagtail as `92C92A`.

Below are some examples of IoGT color palettes used in the v1.0 global site for your reference. Additonally, there is a table where you can easily copy and paste the hex color codes from.

{% include figure.html src="/assets/img/docs/color-palette-1.png" alt="Color palette 1" caption="Color palette 1." %}

{% include figure.html src="/assets/img/docs/color-palette-2.png" alt="Color palette 2" caption="Color palette 2."%}

{% include color-table.html %}
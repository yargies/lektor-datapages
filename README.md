# lektor-datapages
This plugin will create pages from a databag. I had a lot of data in json format, and the lektor way of creating a page (e.g. one folder for each page) would have needed an unwieldy amount of folders. This little plugin allows you to specify a databag path and pages will be automatically generated for each item in the data.

## How to use
Create a field in your model of type “data pages”:

    [fields.pages]
    label = Data pages
    type = datapages
    size = large

Note that currently the name of the field must be "pages”.

In your contents.lr file specify a value like so:

    pages: databag.array, name, template.html

The plugin looks for three values separated by a comma.

1. *Databag path*. It must point to an array. A page will be created for each item in the array.
2. *Name path*. A key to a value that will be used as the _slug value of the page (the plugin will “slugify” it to make it valid)
3. *Template*. The template to use for each page that will be created.

In the template you can access the item with the following variables:

1. **item**: The databag item that was used to generate the page.
2. **item_name**: The value in the databag item indicated by the *name path* as described above.

## Installation
Add lektor-datapages to your project from command line:

    lektor plugins add lektor-datapages

See the Lektor documentation for more instructions on installing plugins.
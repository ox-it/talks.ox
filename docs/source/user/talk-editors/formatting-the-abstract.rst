Formatting text
===============

Formatting using the Textile markup language
--------------------------------------------

Text in the Talk **Abstract** field and the Series **Description** field can be formatted using Textile markup.

The basics are very easy to remember:

**Headings** (Abstract only)

::

     h1. Main Heading
     h2. Sub heading

**Paragraphs**

::

     Separate paragraphs with a blank line.
     
     This is a new paragraph.

**Bold and Italic**

::

     *This will create bold text*
     _This will create italics_

**Bullet Points and Numbered Lists** (Abstract only)

::

     * First Item
     * Second Item
     # Item One
     # Item Two

**Links**

A web address should convert into a link automatically when you save the talk. To give the link a title rather than just show the web address:

::

     "Oxford University":http://www.ox.ac.uk 

To make an email clickable use the following:

::

     "$":mailto:joe.blogs@ox.ac.uk

If you need more, there is a comprehensive manual on `txstyle.org <http://txstyle.org>`_ 

Pasting from Word
-----------------

You can copy and paste from Word, but you will need to format the text again.

If you have a number of abstracts and lots of formatting, then try:

* adjusting the styles in your Word document following the guidelines below
* saving your Word document as a plain text file 
* opening the file in a plain text editor (e.g.: Notepad) and copying from there

**Headings**

* Format > Style > Modify > Numbering ...
* Choose Numbering, click any numbering style and click the Customize ... button
* Set the Number style to None and type 'h1' in the Number format box

**Bullet Points**

* Format > Bullets and Numbering
* Click the Customize ... button
* Select an asterisk from the Bullet Character options

**Numbered Lists**

* Format > Bullets and Numbering
* Click the Customize ... button
* Set the Number style to None and type '#' in the Number format box

Other useful tools
------------------

* `Table converter <http://txstyle.org/tools/50/data-converter>`_ - turning a CSV file (e.g.: exported from Excel) into a Textile table of information
* `Pandoc <http://johnmacfarlane.net/pandoc/index.html>`_ - open source software to convert to Textile from other formats


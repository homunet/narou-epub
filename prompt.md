# Python script generation for web scraping and text combination
https://ncode.syosetu.com
is a website for novel submission.
## Step 1
* Write a Python script to download HTML from the URL below. Look at the number at the end of the URL; this number continues up to 10. The script should download all HTML files in a single execution.
https://ncode.syosetu.com/n9669bk/1/
* Prevent the error of "Error downloading page 10: 403 Client Error:"
* Find the content in <title> in the first HTML. Delete　' - - ' and 'characters after " - - "' in the content. Save the rest in a variable named [novel_title].
* Find meta with the "twitter:creator" attiribute and save the content attibute of the meta in a variable named [novel_author].
## Step 2
* Change the script to receive three command-line arguments.
    * The first: Novel code
    * The second: Start episode
    * The third: End episode
* Change the script to replace the "n9669bk" in the URL with the Novel code.
* Change the script to replace the "1" in the URL with Start episode.
* Change the script to continue downloading up to the End episode number instead of 10.
## Step 3
* In each HTML file downloaded in step 1, remove everything except the following:
	* div with the class "p-novel__number"
	* h1
	* div with the class "p-novel__body"
    * Note: Keep all child elements under these elements.
* Find the content in the div with the class "p-novel__number". 
* Insert the content and "&nbsp;" in front of the content of the div with the class "p-novel__body".
    * Example: <h1 class="p-novel__title p-novel__title--rensai">1/286&nbsp;プロローグ</h1>
* Delete div with the class "p-novel__number".
## Step 4
* Combine all files processed in Step 3 in the numerical order from Step 1.
* Set HTML title as [novel_title]:[Start episode]-[End episode].
* Set meta with author attribute with content [novel_author].
* Save the combined file with the name in the format :[Novel code]-[Start episode]-[End episode].html
    * Example: "n9669bk-1-10.html"
* Prevent the error of "An error occurred: invalid literal for int() with base 10: 'html/page'".
## File name
The file name of the generated Python script should be "narou-dl.py".
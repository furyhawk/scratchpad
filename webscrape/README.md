# Web Scraping With Python


**Table of contents:**

<!--ts-->
  * [Objective](#objective)
  * [Motivation](#motivation)
  * [How Does It Work?](#how-does-it-work)
  * [HTML (Optional)](#html-optional)
  * [Web Scraping Workflow](#web-scraping-workflow)
  * [Ethics of Web Scraping](#ethics-of-web-scraping)
<!--te-->

<br>

## Objective

This tutorial aims to show how to use the Python programming language to web scrape a website. Specifically, we will use the `requests` and `Beautiful Soup` libraries to scrape and parse data from [companiesmarketcap.com](https://companiesmarketcap.com/) and retrieve the “*Largest Companies by Market Cap*”. Finance details are scrape and parse from [finance.yahoo.com](https://finance.yahoo.com/quote/).

We will learn how to scale the web scraping process by first retrieving the first company/row of the table, then all companies on the website’s first page, and finally, all 6024 companies from multiple pages. Once the scraping process is complete, we will preprocess the dataset and transform it into a more readable format before using `matplotlib` to visualise the most important information.

<br>

## Motivation

There are many reasons why people might want to perform web scraping. Some of the most common motivations include:

  - Data collection: Web scraping can be a quick and efficient way to collect large amounts of data from websites. This can be particularly useful for companies or organizations that want to gather data for research or analysis.

  - Price comparison: Web scraping can be used to gather data from multiple online retailers in order to compare prices and make informed purchasing decisions.

  - Lead generation: Web scraping can be used to gather contact information for potential clients or customers from websites.

  - Market research: Web scraping can be used to gather data from websites and social media platforms in order to understand consumer behavior and preferences.

  - Content aggregation: Web scraping can be used to gather data from multiple sources in order to create a curated news feed or to create a summary of the latest developments in a particular field.

  - Monitoring: Web scraping can be used to monitor a website for changes or updates, and to send notifications when such changes occur.

  - Personal projects: Some people use web scraping as a way to gather data for personal projects or to learn more about a particular topic.

<br>

## How Does It Work?

Web scraping involves making HTTP requests to a website's server to retrieve the HTML source code of web pages. The HTML source code contains the content and structure of the web page, including the text, images, and links.

Once the HTML source code has been retrieved, a web scraper can then parse the code to extract the desired information. This is typically done using a programming language, such as Python or Java, and a library or framework designed specifically for web scraping, such as Beautiful Soup or Selenium.

There are many different approaches to web scraping, and the specific technique used will depend on the structure and complexity of the website being scraped, as well as the data being targeted. Some web scrapers are simple scripts that make HTTP requests and extract specific information from the HTML source code of web pages, while others are more advanced and can simulate the behavior of a human user, including filling out forms and clicking on links.

Regardless of the approach taken, the goal of web scraping is to extract data from websites in an automated and efficient manner.

<br>

## HTML (Optional)

HTML (HyperText Markup Language) is a markup language used to structure and format content on the web. It consists of a series of tags that define the structure of a document and the meaning of the content within those tags.

HTML is used to create the layout and design of a website, as well as to add interactive elements like forms and media. The content of a web page, such as the text, images, and links, is written in HTML code and then interpreted by a web browser to be displayed to the user.

Here is an example of a simple HTML document:

```
<html>
<head>
  <title>My Website</title>
</head>
<body>
  <h1>Welcome to my website</h1>
  <p>This is a paragraph of text.</p>
  <ul>
    <li>Home</li>
    <li>About</li>
    <li>Contact</li>
  </ul>
</body>
</html>

```
The `<html>` element indicates the start of the HTML document. The `<head>` element contains information about the document, such as the title, and the `<body>` element contains the actual content of the page. The `<h1>` element indicates a heading, and the `<p>` element indicates a paragraph. The `<ul>` element is used to create an unordered list, and the `<li>` elements are used to define the items in the list.


HTML tags are usually written in pairs, with an opening tag and a closing tag. The closing tag includes a forward slash (/) after the opening angle bracket (<). For example, the opening and closing tags for a heading might be written like this: `<h1>` and `</h1>`.

HTML tags can have attributes, which provide additional information about the element. Attributes are specified in the opening tag of an element and are written as name-value pairs. For example, the href attribute of an anchor tag (`<a>`) specifies the URL that the link points to: `<a href="http://www.example.com">Click here</a>`.

HTML documents can be styled using CSS (Cascading Style Sheets). CSS is a separate language that is used to define the look and layout of an HTML document.

HTML5 is the latest version of HTML, and it includes new features such as support for video and audio playback, the ability to draw graphics using the canvas element, and new form elements.


<br>
  
## Web Scraping Workflow

The workflow for web scraping typically involves the following steps:

  1. Identify the target website and the data you want to extract.

  2. Inspect the page source to determine the HTML elements that contain the data you want to extract.

  3. Write code to send an HTTP request to the website's server to retrieve the HTML source code of the web page.

  4. Parse the HTML source code to extract the desired data. This is typically done using a library or framework specifically designed for web scraping, such as Beautiful Soup or Selenium.

  5. Store the extracted data in a structured format, such as a CSV file or a database.

  6. Optionally, clean and transform the data to make it more suitable for the intended use.

  7. Visualize or analyze the data, or use it to perform some other task.

This is a general outline of the web scraping process, and the specific steps involved can vary depending on the complexity of the website and the data being targeted.

To complete those steps, we need two third-party Python libraries:
1. **[Requests](https://docs.python-requests.org/en/master/)**: a simple but powerful library for sending all kinds of HTTP requests to a web server,
  
2. **[Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)**: a library for parsing HTML and XML documents. It works with a user-selected parser to provide idiomatic ways of navigating, searching, and modifying the parse tree.

<br>
  
## Ethics of Web Scraping
  
Web scraping can raise ethical concerns, particularly when it is done without the permission of the website owner. Some websites explicitly prohibit web scraping in their terms of service, while others may have more permissive policies.

There are a few ethical considerations to keep in mind when performing web scraping:

  - Respect the terms of service: Most websites have terms of service that outline what is and is not allowed. Make sure to read and understand the terms of service before beginning to scrape a website, and respect any restrictions that are in place.

  - Don't overburden the website: Web scraping can place a significant load on a website's server, especially if it is done on a large scale. Make sure to respect the website's resources and avoid scraping the site excessively or in a way that could disrupt its normal functioning.

  - Be transparent: If you are using web scraping for research or other purposes, it is important to be transparent about your methods and to cite the sources of your data.

  - Protect privacy: If you are scraping websites that contain personal data, make sure to protect the privacy of the individuals whose data you are collecting. Follow best practices for data privacy and security.

Overall, the ethics of web scraping depend on the specific context in which it is being performed. It is important to be mindful of the potential impact of your actions and to act responsibly when scraping websites.

<br>

These resources should provide a good starting point for learning more about web scraping. I hope they are helpful!
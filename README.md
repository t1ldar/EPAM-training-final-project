# RSS reader

RSS reader is a command-line / web application for all human beings.

## Install a CLI application

Python >= 3.9, pip and setuptools are required. Setuptools install with command:
```bash
pip install setuptools
```
Create virtual environment if necessary, activate it, then go to RSS-parser folder,
install requirements, afterwards run setup.py with following commands:
```bash
pip install -r requirements.txt
python setup.py install
```

## Install a web application
Download and install a docker compose on your machine. Then go to project's root folder
and install web application with a command. Ports 8000 and 5432 are used.
```bash
docker-compose up
```
Wait until everything is installed. Check that two containers with names 'rss-parser' and 'db-pg' (postgres) are running with a command:
```bash
docker ps
```
Then open a browser and check that web application is running with url:
```bash
http://localhost:8000/
```
If you see start page with 'RSS reader wed app' title, you are good to use it.

## Web application info
Web application is developed using FastAPI and Postgres database. PostgreSQL database is managed through SQLAlchemy.
Dbeaver software (database manager) was used to test the application behaviour. 

## Usage of Web application
Usage of web application is pretty much intuitive and provides with same functionality as CLI application. 
Go to http://localhost:8000, fill in one of the two forms and get news in human-readable format:
+ Read news form with following fields. 
  * URL - RSS source url.
  * Number of news - limit number of news to show or leave it empty to get all.
  * Publication date in YYYYMMDD format. If publication date argument provided,
  then app will try to fetch news from the database with exact publication date, otherwise news fetched from the internet
  * Checkbox to convert fetched new into PDF/HTML/EPUB formats in  background. 
  Filename should be provided with or without files extension. 
  All converted files are saved in 'app/converted_files_dump' folder.
  
  This form uses '/read-rss' endpoint with POST method and works more or less as CLI application.


+ Read news directly from cache:
  * Available RSS sources. This field shows all available RSS sources in the database. 
  At first start of application it is empty, for obvious reason - database is empty. 
  Get news with upper form and then update http://localhost:8000 to update available sources.
  * Number of news - limit number of news to show or leave it empty to get all.
  * Publication date in YYYYMMDD format. If publication date argument provided,
  then app will try to fetch news from the database with exact publication date.
  
  This form uses '/read-cache' endpoint with GET method. 
  
  Then reading news from cache, generated page have 'delete' button which will delete a news item
  and will update the page. Updated page is '/news' endpoint which gets all news from the table 
  no matter the original query parameters.

## Web application API endpoints
All API endpoints could be viewed, used and tested on the page http://localhost:8000/docs. Open the page,
select an endpoint, press 'try it out' button, fill in query parameters, press 'execute' and check the output.

Endpoints:

- '/', GET method. Main page, gets list of RSS sources and renders HTML page with news in human-readable format.
- '/read-rss', POST method. Sends FORM with arguments, retrieves news, caches them and renders an HTML page with news.
- '/read-cache', GET method. Gets news from the database with provided query parameters and renders a page.
- '/news', GET method. Gets all news entries from the database and renders a page.
- '/news/{pubdate}', GET method. Gets all news with specified publication date and renders a page.
- '/news/delete/{news_id}', POST method. Removes an entry by id in the database, 
   renders page with all left news in the database.
- '/rss', GET method. Gets all rss sources with related news, according to schema.
- '/rss/create', POST method. Manually add rss source with query parameters.
- '/rss/delete/', DELETE method. Delete the rss source by it's id.

## Usage of CLI application

```shell
usage: rss_reader.py [-h] [--version] [--json] [--verbose] [--limit LIMIT] [--date DATE]
                          [--to-html PATH_HTML] [--to-pdf PATH_PDF] [--to-epub PATH_EPUB] [--colorize] [source]


Pure Python command-line RSS reader.

positional arguments:
  source         RSS URL

optional arguments:
  -h, --help           Show this help message and exit
  --version            Print version info
  --json               Print result as JSON in stdout
  --verbose            Outputs verbose status messages
  --limit LIMIT        Limit news topics if this parameter provided
  --date DATE          Get news from cache, use date format: YYYYMMDD
  --to-html PATH_HTML  Convert news into HTML file. Indicate path, filename is optional
  --to-pdf PATH_PDF    Convert news into PDF file. Indicate path, filename is optional
  --to-epub PATH_EPUB  Convert news into EPUB file. Indicate path, filename is optional
  --colorize           Colorize output
```

## Usage of CLI app version examples
```shell
rss_reader https://lifehacker.com/rss --limit 2
```
or 
```shell
python rss_reader.py https://lifehacker.com/rss --limit 2
```





## JSON structure

```
[
    {
    "Feed": "RSS feed header",
    "URL": "RSS URL",
    "Article": {
            "title": "article's title",
            "pubdate": "publishing date",
            "description": "article's description if exists, else 'Empty'",
            "link": "link to a full article",
            "img_link": "link to an article's image if exists, else 'Empty'"
        }
    },
    ...
]
```

## Caching feature
Caching feature saves all parsed news into a local database file - 'rss_parser/caching/cached_news.db'
under 'cached_news' table. Which is created using Sqlite3. Database entries could be retrieved by news publication date
or both 'source url' and publication date. In order to do so  '--date' optional argument should be specified 
with date in YYYYMMDD format. Examples:

- rss_reader https://lifehacker.com/rss --date 20220417
- rss_reader --date 20220417 

If RSS feed url is not specified, all news with selected publication date will be shown.

Images are also cached into a local folder 'rss_parser/caching/cached_images' and used for format converter feature,
if internet connection is not available during converting.


## Format converter feature
Application format converter feature converts news into selected format and generates file with specified path.
If path doesn't contain filename (checked how path 'endswith'), then it will be generated automatically. Path should exists.


If specified folder doesn't exist, error 
will be raised.

Argument examples:

- for win OS: 'c:\temp', 'c:\temp\example.pdf' etc.
- for Ubuntu: './', '~/Documents', '~Documents/example.html' etc.

Format converter templates are located in project 'rss_parser/converters/templates' folder.

EPUB format checked  with 'calibre' software(v.5.41.0 windows version).


## PEP8 check
Included into project 'tox.ini' file used for pycodestyle configuration, setting max line length to 120. Pycodestyle locates it in any parent folder of the
path(s) being processed. To check project files to pep8 accordance, add to the environment pycodestyle lib with command:
```shell
pip install -r requirements_dev.txt
```
Afterwards go to project's root folder and run commands (setup.py checked manually):
```shell
pycodestyle rss_parser
pycodestyle setup.py
```

## RSS reader tested on URLs:
- https://news.yahoo.com/rss
- https://lifehacker.com/rss
- https://moxie.foxnews.com/feedburner/world.xml
- http://rss.cnn.com/rss/edition.rss
- https://rss.nytimes.com/services/xml/rss/nyt/World.xml
- http://feeds.bbci.co.uk/news/world/rss.xml
- https://www.techrepublic.com/rssfeeds/topic/cloud


## RSS reader tested with:
- Windows 10 / 11
- Ubuntu 20.04.3 LTS

## License
[MIT](https://choosealicense.com/licenses/mit/)

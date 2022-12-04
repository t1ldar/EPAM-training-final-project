import os
from typing import Any, List, Optional

import requests.exceptions
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates


from crud import crud
from errors import exception_handler
from rss_parser.caching.caching_images import ImageHandler
from rss_parser.converters import converter
from rss_parser.news_parser import news_parser
from schemas import schemas
from services import services, validator


app = FastAPI()

# Create database
services.create_database()
# Static files location with bootstrap elements
app.mount("/templates/static", StaticFiles(directory="templates/static"), name="static")
# Setup Jinja templates folder location
templates = Jinja2Templates(directory="templates")
# Location of dump folder for converted files
CONVERTED_FILES_FOLDER = os.path.join(os.path.dirname(__file__), 'converted_files_dump')


@app.get("/")
def start(request: Request, db: Session = Depends(services.get_db)):
    rss_list = crud.get_all_rss_sources(db=db)
    return templates.TemplateResponse('main.html', {"request": request,
                                                    "rss_list": rss_list})


@app.post("/read-rss",  response_class=HTMLResponse)
def read_rss_source(request: Request,
                    rss_url: Optional[str] = Form(None),
                    limit_arg: Optional[Any] = Form(None),
                    date_arg: Optional[str] = Form(None),
                    save_pdf: Optional[bool] = Form(None),
                    filename_pdf: Optional[str] = Form(None),
                    save_html: Optional[bool] = Form(None),
                    filename_html: Optional[str] = Form(None),
                    save_epub: Optional[bool] = Form(None),
                    filename_epub: Optional[str] = Form(None),
                    db: Session = Depends(services.get_db)):

    # Validate limit argument, if provided
    if limit_arg is not None:
        try:
            validator.validate_limit_arg(value=limit_arg)
            limit_arg = int(limit_arg)
        except exception_handler.NotValidLimitArg:
            raise HTTPException(status_code=418, detail="Not valid limit argument. Should be an integer <= 0")

    # Check internet connection and validate provided url and check if it is leading to a rss feed
    if not date_arg:
        try:
            validator.check_internet_connection()
            validator.validate_url_is_rss_feed(url=rss_url)
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=418, detail="No internet connection. Provide date arg. to read from cache")
        except exception_handler.NotRssFeedUrlError:
            raise HTTPException(status_code=418, detail="Provided URL doesn't lead to a RSS feed")
        except Exception as e:
            raise HTTPException(status_code=418, detail=f"Provided URL is not valid. {e}")

    parsed_news_list = []

    # Check rss type of provided link and parse news from provided rss source
    if not date_arg:
        rss_type = news_parser.rss_feed_type_checker(url=rss_url)
        if rss_type:
            parsed_news_list = news_parser.parse_rss_feed_with_non_xml(url=rss_url, limit_arg=limit_arg)
        else:
            parsed_news_list = news_parser.parse_rss_feed_regularly(url=rss_url, limit_arg=limit_arg)

        # Cache images and save them locally under 'rss_parser/caching/cached_images' folder
        cache_images = ImageHandler(parsed_news_list)
        cache_images.download_images_concurrently()
        cache_images.resize_cached_images_concurrently()

        # Check if provided rss source is already in the database, if not insert into 'rss_book' table
        if not crud.get_rss_source_by_url(db=db, rss_url=rss_url):
            rss_header = news_parser.get_rss_header(url=rss_url)
            crud.create_rss_entry(rss_url=rss_url, rss_header=rss_header, db=db)

        # Get rss source entry for further relation with news table (rss source id from database is needed)
        rss_entry_from_db = crud.get_rss_source_by_url(db=db, rss_url=rss_url)

        # Insert news into table if they aren't already in there
        for news in parsed_news_list:
            if not crud.get_news_by_title(db=db, title=news['title']):
                news['pubdate_format'] = services.format_pubdate(news['pubdate'])
                crud.create_news_entry(db=db, news=news, rss_id=rss_entry_from_db.id)

    # Get data from cache, if date argument provided
    if date_arg is not None:
        try:
            parsed_news_list = crud.get_news_by_date_source(db=db,
                                                            pubdate=date_arg,
                                                            source=rss_url,
                                                            limit_arg=limit_arg)
        except exception_handler.NewsNotFound:
            raise HTTPException(status_code=404, detail=f"No news found published on {date_arg} from {rss_url}")

        if not list(parsed_news_list):
            raise HTTPException(status_code=404, detail=f"No news found published on {date_arg} from {rss_url}")

    # Convert into pdf
    if save_pdf:
        try:
            validator.validate_filename(filename=filename_pdf)
            converter.Converter.convert_to_pdf(target_path=services.create_target_path(folder=CONVERTED_FILES_FOLDER,
                                                                                       extension='pdf',
                                                                                       filename=filename_pdf),
                                               news_list=parsed_news_list)
        except exception_handler.NotValidFilename:
            raise HTTPException(status_code=418, detail=f"Pdf filename field is empty")

    # Convert into html
    if save_html:
        try:
            validator.validate_filename(filename=filename_html)
            converter.Converter.convert_to_html(target_path=services.create_target_path(folder=CONVERTED_FILES_FOLDER,
                                                                                        extension='html',
                                                                                        filename=filename_html),
                                                news_list=parsed_news_list)
        except exception_handler.NotValidFilename:
            raise HTTPException(status_code=418, detail=f"Html filename field is empty")

    # Convert into epub
    if save_epub:
        try:
            validator.validate_filename(filename=filename_epub)
            # If date argument is provided, then data retrieved from the database and in that case we have to
            # convert list of sqlalchemy.orm objects into dictionary for correct EPUB converter work
            if date_arg:
                parsed_news_list = [services.object_as_dict(news) for news in parsed_news_list]
            converter.Converter.convert_to_epub(target_path=services.create_target_path(folder=CONVERTED_FILES_FOLDER,
                                                                                        extension='epub',
                                                                                        filename=filename_epub),
                                                news_list=parsed_news_list)
        except exception_handler.NotValidFilename:
            raise HTTPException(status_code=418, detail=f"Epub filename field is empty")

    # Render HTML with parsed news
    return templates.TemplateResponse('read_rss.html', {"request": request,
                                                        "news_list": parsed_news_list})


@app.post("/read-cache", response_class=HTMLResponse)
def read_news_from_cache(request: Request,
                         dropdown_choices: Optional[Any] = Form(None),
                         limit_arg_cache: Optional[int] = Form(None),
                         date_arg_cache: Optional[str] = Form(None),
                         db: Session = Depends(services.get_db)):
    # Validate limit argument
    if limit_arg_cache is not None:
        try:
            validator.validate_limit_arg(value=limit_arg_cache)
            limit_arg_cache = int(limit_arg_cache)
        except Exception:
            raise HTTPException(status_code=418, detail="Not valid limit argument. Should be an integer <= 0")
    # Get data from the database
    try:
        if dropdown_choices == "all":
            dropdown_choices = None
        news_list = crud.get_news_by_date_source(db=db,
                                                 pubdate=date_arg_cache,
                                                 source=dropdown_choices,
                                                 limit_arg=limit_arg_cache)
    except exception_handler.NewsNotFound:
        raise HTTPException(status_code=404,
                            detail=f"No news found published on {date_arg_cache} from {dropdown_choices}")

    if not list(news_list):
        raise HTTPException(status_code=404,
                            detail=f"No news found published on {date_arg_cache} from {dropdown_choices}")
    # Render the output
    return templates.TemplateResponse('get_news_from_db.html', {"request": request,
                                                                "news_list": news_list})


@app.get("/read-cache", response_model=List[schemas.News])
def read_news_from_cache(
                         rss_source_url: Optional[str] = None,
                         limit_arg: Optional[int] = None,
                         date_arg: Optional[str] = None,
                         db: Session = Depends(services.get_db)):
    # Validate limit argument
    if limit_arg is not None:
        try:
            validator.validate_limit_arg(value=limit_arg)
            limit_arg = int(limit_arg)
        except Exception:
            raise HTTPException(status_code=418, detail="Not valid limit argument. Should be an integer <= 0")
    # Get data from the database
    try:
        news_list_from_db = crud.get_news_by_date_source(db=db,
                                                         pubdate=date_arg,
                                                         source=rss_source_url,
                                                         limit_arg=limit_arg)
    except exception_handler.NewsNotFound:
        raise HTTPException(status_code=404, detail=f"No news found published on {date_arg} from {rss_source_url}")
    if not list(news_list_from_db):
        raise HTTPException(status_code=404, detail=f"No news found published on {date_arg} from {rss_source_url}")
    return news_list_from_db


@app.get("/news", response_class=HTMLResponse)
def get_all_news_from_db(request: Request,
                         db: Session = Depends(services.get_db)):
    news_list = crud.get_all_news(db=db)
    if not news_list:
        raise HTTPException(status_code=404, detail="News not found in the database")
    return templates.TemplateResponse('get_news_from_db.html', {"request": request,
                                                                "news_list": news_list})


@app.get("/news/{pubdate}", response_class=HTMLResponse)
def read_news_from_cache_by_date(request: Request,
                                 pubdate: str,
                                 db: Session = Depends(services.get_db)):
    # Get news from database for exact published date
    news_list = crud.get_news_by_date(db=db, pubdate=pubdate)
    if not list(news_list):
        raise HTTPException(status_code=404, detail=f"No news found published on {pubdate}")
    return templates.TemplateResponse('get_news_from_db.html', {"request": request,
                                                                "news_list": news_list})


@app.post("/news/delete/{news_id}")
def delete_news_from_db(request: Request,
                        news_id: int,
                        db: Session = Depends(services.get_db)):
    # Delete news from db by news id
    crud.delete_news_by_id(db=db, news_id=news_id)
    # Get all news from db after delete operation
    news_list = crud.get_all_news(db=db)
    # Return html with updated news_list from db
    return templates.TemplateResponse('get_news_from_db.html', {"request": request,
                                                                "news_list": news_list})


@app.get("/rss", response_model=List[schemas.Rss])
def get_all_rss_sources_from_db(db: Session = Depends(services.get_db)):
    # Get list of Rss entries from the database according to schema
    all_rss_in_db = crud.get_all_rss_sources(db=db)
    if not list(all_rss_in_db):
        raise HTTPException(status_code=404, detail="Rss sources not found in the database")
    # Return json response
    return all_rss_in_db


@app.post("/rss/create/", status_code=201)
def create_rss_source(rss_url: str,
                      rss_header: str,
                      db: Session = Depends(services.get_db)):
    check_rss_exists = crud.get_rss_source_by_url(db=db, rss_url=rss_url)
    if check_rss_exists:
        return {"message": f"rss source with url {rss_url} is already in the database"}
    crud.create_rss_entry(db=db, rss_url=rss_url, rss_header=rss_header)
    return {"message": f"rss source with url {rss_url} added to the database"}


@app.delete("/rss/delete")
def delete_rss_source(rss_source_id: int,
                      db: Session = Depends(services.get_db)):
    rss_source_to_delete = crud.get_rss_source_by_id(db=db, rss_id=rss_source_id)
    if rss_source_to_delete:
        crud.delete_rss_source(db=db, rss_source_id=rss_source_id)
        return {"message": f"Rss source with id {rss_source_id} deleted from the database with all related news"}
    else:
        raise HTTPException(status_code=404, detail=f"Rss source with id {rss_source_id} not found")

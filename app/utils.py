import openai
import os
from dotenv import load_dotenv
import mysql.connector
import requests
from newspaper import Article,fulltext
import json
from datetime import date
import logging
from pythonjsonlogger import jsonlogger

def setup_logging(log_level=logging.INFO, log_file=None):
    log_file = "request.log"
    # Create a JSON logger
    logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Create a console handler with the JSON formatter
    console_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(fmt='%(asctime)s %(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add a file handler if log_file path is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(log_level)


    return logger

logger = setup_logging()


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY","Error")
db_host = os.getenv("DB_HOST")
db_table = os.getenv("DB_TABLE")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

cnx = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name
    )

def get_tags():
    cursor = cnx.cursor()
    query = "SELECT * from tags"
    cursor.execute(query)
    rows = cursor.fetchall()
    tags_list = [row[1] for row in rows]
    cursor.close()

    return tags_list

def write_article_to_db(webpage_title,webpage_summary,webpage_text,webpage_markdown,url,tags):
    logger.info(f"Writing URL: {url} to database")
    current_date = date.today().isoformat()
    tags_str = ",".join(tags)
    cursor = cnx.cursor()
    #query = "INSERT INTO webpages (url, title, date_added, summary, raw_text, tags, markdown) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    query = f"INSERT INTO {db_table} (url, title, date_added, summary, raw_text, tags, markdown) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (url, webpage_title, current_date, webpage_summary, webpage_text, tags_str, webpage_markdown)
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()




def get_webpage_text(url):
    logger.info(f"Retrieving webpage text for {url}")
    # Convert this to an Article
    # html = requests.get(url).text
    # text = fulltext(html)
    article = Article(url)
    article.download()
    try:
        article.parse()
        article_title = article.title
        article_text = article.text
        logger.info(f" - parsed title: {article_title}")
    except:
        article_title = "No Title Found"
        html = requests.get(url).text
        article_text = fulltext(html)
    return article_title, article_text
        


def query_gpt_summary(body):
    tags = get_tags()
    # with open("examples/log4j.txt","r") as f:
    #     sample_article = f.read()

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages = [
        {
            "role":"system",
            "content":f"""
You are a helpful assistant who will summarize the body of a website for me. 
For the following article, you will do two things: Create a 1 paragraph summary, 
and assign any tags from my list you think are applicable. 
The list of tags I want you to consider is {tags}. Your response should be in JSON, for example:

    "tags":list_of_tags,
    "summary":webpage_summary

"""
        },
        {
            "role":"user",
            "content":body
        }
    ],
    temperature=.4,
    max_tokens=1024,
    api_key=openai_api_key 
    ) 

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def query_gpt_markdown(body):
    # with open("examples/log4j.txt","r") as f:
    #     sample_article = f.read()

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages = [
        {
            "role":"system",
            "content":f"""
You are an AI assistant. I am going to give you the raw text from a website
and you will transform it into markdown syntax, then send it back to me."""
        },
        {
            "role":"user",
            "content":body
        }
    ],
    temperature=.4,
    max_tokens=1024,
    api_key=openai_api_key
    ) 

    return response.choices[0].message.content

def add_bookmark(url):
    logger.info(f"Received request to download {url}")
    webpage_title, webpage_text = get_webpage_text(url)
    webpage_summary_payload = query_gpt_summary(webpage_text)
    webpage_dict = json.loads(webpage_summary_payload)
    tags = webpage_dict['tags']
    webpage_summary = webpage_dict['summary']
    webpage_markdown = query_gpt_markdown(webpage_text)
    # (webpage_title,webpage_summary,webpage_text,webpage_markdown,url,tags)
    write_article_to_db(webpage_title,webpage_summary,webpage_text,webpage_markdown,url,tags)

    #print(f"Webpage Summary: \n{webpage_summary_payload}")
    # print(f"Website Summary: \n{webpage_summary}")
    # print("")
    # print(f"Tags: {tags}")
    # print("")
    # print(f"Markdown:\n{webpage_markdown}")

if __name__ == "__main__":
    #query_gpt_summary("url","body")
    #query_gpt_markdown("url","body")
    #tags_list = get_tags()
    #print(f"Tags: {tags_list}")
    url = "https://www.linkedin.com/pulse/3-ways-vector-databases-take-your-llm-use-cases-next-level-mishra"
    add_bookmark(url)
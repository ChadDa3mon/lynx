import openai
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY","Error")

def get_tags():
    cnx = mysql.connector.connect(
    host='your_host',
    user='your_username',
    password='your_password',
    database='your_database'
    )
    tags_list = ["AI","Technology","Cybersecurity","Home Theater","Cooking"]
    return tags_list

def query_gpt_summary(url,body):
    tags = get_tags()
    with open("examples/log4j.txt","r") as f:
        sample_article = f.read()

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages = [
        {
            "role":"system",
            "content":f"""
You are a helpful assistant who will summarize the body of a website for me. 
For the following article, you will do two things: Create a 1 paragraph summary, 
and assign any tags from my list you think are applicable. 
The list of tags I want you to consider is {tags}"""
        },
        {
            "role":"user",
            "content":sample_article
        }
    ],
    temperature=.4,
    max_tokens=1024
    ) 

    print(response.choices[0].message.content)

def query_gpt_markdown(url,body):
    with open("examples/log4j.txt","r") as f:
        sample_article = f.read()

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
            "content":sample_article
        }
    ],
    temperature=.4,
    max_tokens=1024
    ) 

    print(response.choices[0].message.content)

if __name__ == "__main__":
    #query_gpt_summary("url","body")
    query_gpt_markdown("url","body")
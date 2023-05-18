import requests
from bs4 import BeautifulSoup
import re
import json
import argparse
import pika

def get_response_from_url(url):
    return requests.get(url)

def get_soup(response):
    return BeautifulSoup(response.text, 'html.parser')

def get_html_class(soup):
    return soup.find(attrs={'class': 'svelte-13ozom4'})

def get_news_child(soup):
    return soup.find_all('a', attrs={'class': 'svelte-13ozom4'})

def get_news_descriptions_child(soup):
    temp = soup.find_all('p')
    description = ''
    for tag in temp:
        description = description + tag.text + '\n'
    return description

def get_list_of_comments(soup):
    return soup.find('div', attrs={'class': 'list'})

def get_list_of_news(soup):
    final_list = []
    news_lst = []
    news_child = get_news_child(soup)
    for link in news_child:
        news_href = ("{}".format(link.get("href")))
        if 'https://adevarul.ro/' in news_href:
            news_lst.append(news_href)
    for url in news_lst:
        if '#comments' not in url:
            final_list.append(url)
    return final_list

def get_list_of_comments(soup):
    counter = 0
    final_list = []
    news_lst = []
    news_child = get_news_child(soup)
    for link in news_child:
        news_href = ("{}".format(link.get("href")))
        if 'https://adevarul.ro/' in news_href:
            counter += 1
            news_lst.append(news_href)
    for url in news_lst:
        if '#comments' in url:
            final_list.append(url)
    return final_list

def create_comment_list(comment_data, comments):
    users = []
    comment_users = []
    if len(comment_data) > 0:
        for comment in comment_data['comments']:
            family_name = comment['user']['family_name']
            comment_users.append(comment['user']['family_name'])
            comment_text = comment['text']
            comment_users.append(comment['text'])
            users.append(comment_users)  
            comment_users = []  
            comment = {
                "author": family_name,
                "text": comment_text
            }
            comments.append(comment)

    return comments

def get_description_of_news(news_list, param, posts):
    rabbitMQ_list_2 = []
    for news in news_list:
        post = {
            "article": None,
            "comments": None
        }
        comments = []

        # news description part
        response = get_response_from_url(news)
        soup = get_soup(response)
        news_description = get_news_descriptions_child(soup)

        post['article'] = news_description

        if param:
            # comment part
            comment_id = re.search(r"[0-9]{7}", news).group(0)
            comment_response = get_response_from_url(create_comment_url(comment_id))
            comment_soup = get_soup(comment_response)
            comment_data = json.loads(str(comment_soup))  # deserializare
            comment_list = create_comment_list(comment_data, comments)  # list of comments
            if len(comment_list) > 0:
                post['comments'] = comment_list

            # rabbitmq list part
            rabbitMQ_list_2.append([news_description, comment_list])
        else:
            rabbitMQ_list_2.append([news_description])
        posts.append(post)
    return posts

def create_comment_url(news_id):
    url_string = 'https://social.adh.reperio.news/adevarul.ro/comment/content/'
    url_string = url_string + news_id
    return url_string

def insert_into_queue(lst):
    # Create a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Define the queue to send messages to
    queue_name = 'news_queue'

    # Convert the list to a JSON string
    json_str = json.dumps(lst)

    # Send the JSON string to the queue
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=json_str)

    # Close the connection to RabbitMQ server
    connection.close()


parser = argparse.ArgumentParser()
parser.add_argument('--comments', action="store_true", default=None, required=False)
args = parser.parse_args()
param = args.comments

posts = []

response = get_response_from_url('https://adevarul.ro/') # response
soup = get_soup(response)
html_class = get_html_class(soup) 
list_of_news_links = get_list_of_news(soup)
list_news_description_and_comments = get_description_of_news(list_of_news_links, param, posts)
insert_into_queue(list_news_description_and_comments)

json_str = json.dumps(posts)

with open("adevarul.json", "w") as outfile:
    outfile.write(json_str)
import requests
from bs4 import BeautifulSoup
import re
import json
import argparse

def get_response_from_url(url):
    return requests.get(url)

def get_soup(response):
    return BeautifulSoup(response.text, 'html.parser')

def get_html_class(soup):
    return soup.find(attrs={'class': 'svelte-13ozom4'})

def get_news_url(soup):
    return soup.find_all('div', attrs={'class': 'svelte-13ozom4'})

def get_news_child(soup):
    return soup.find_all('a', attrs={'class': 'svelte-13ozom4'})

def get_news_descriptions(soup):
    return soup.find('main', attrs={'class': 'svelte-1m9guhq'})

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

def create_comment_list(comment_data):
    comments = []
    for comment in comment_data['comments']:
        comments.append(comment['text'])
    return comments

def get_description_of_news(news_list):
    i = 0
    rabbitMQ_list_2 = []

    for news in news_list:
        # comment part 
        comment_id = re.search(r"[0-9]{7}", news).group(0)
        comment_response = get_response_from_url(create_comment_url(comment_id))
        comment_soup = get_soup(comment_response)
        comment_data = json.loads(str(comment_soup)) # deserializare
        comment_list = create_comment_list(comment_data) # list of comments

        # news description part   
        response = get_response_from_url(news)
        soup = get_soup(response)
        news_description = get_news_descriptions_child(soup)

        # rabbitmq list part
        rabbitMQ_list_2.append([news_description, comment_list])
        if i == 1:
            break
        i += 1
    # print(rabbitMQ_list_2)
    return rabbitMQ_list_2

def create_comment_url(news_id):
    url_string = 'https://social.adh.reperio.news/adevarul.ro/comment/content/'
    url_string = url_string + news_id
    return url_string

response = get_response_from_url('https://adevarul.ro/') # response
soup = get_soup(response)
html_class = get_html_class(soup) 
list_of_news_links = get_list_of_news(soup)
list_news_description_and_comments = get_description_of_news(list_of_news_links)
print(list_news_description_and_comments)
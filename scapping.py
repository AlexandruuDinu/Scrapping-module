import requests
from bs4 import BeautifulSoup
import re
import json

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
    return soup.find_all('p')[:10]

def get_list_of_comments(soup):
    return soup.find('div', attrs={'class': 'list'})

def get_comment_text(soup):
    return soup.find_all('div', attrs={'class': 'svelte-3ygqb2'})

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


def get_description_of_news(news_list):
    i = 0
    count_news_list = len(news_list)
    items = 2
    rabbitMQ_list = [[0 for x in range(items)] for y in range(count_news_list)]
    for news in news_list:
        comment_id = re.search(r"[0-9]{7}", news).group(0)
        print("CommentID: ", comment_id)
        return 
        response = get_response_from_url(news)
        soup = get_soup(response)
        html_class = get_news_descriptions_child(soup)
        rabbitMQ_list[i][0] = html_class
        if i == 3:
            break
        i += 1
        comments = get_comment_text(soup)
        print(comments)
        return
    #     list_of_news_links = get_list_of_news(soup)

def get_comments_of_news(news_list_comments):
    for comment in news_list_comments:
        response = get_response_from_url(comment)
        soup = get_soup(response)
        comments = get_list_of_comments(soup)
        
# https://social.adh.reperio.news/adevarul.ro/comment/content/2263831?offset=3&limit=50
# [A-Za-z]+://[A-Za-z]+\.([A-Za-z]+(/[A-Za-z]+)+)-[A-Za-z]+/[A-Za-z]+/([A-Za-z]+(-[A-Za-z]+)+)-(?P<commentId>\d\d\d\d\d\d\d\).[A-Za-z]+


response = get_response_from_url('https://adevarul.ro/') # response
soup = get_soup(response)
html_class = get_html_class(soup) # CONTINUT HTML

list_of_news_links = get_list_of_news(soup) # captare stire
# print(list_of_news_links)

list_news_description_and_comments = get_description_of_news(list_of_news_links)
# get_description_of_news(soup)
# list_news_comments = get_comments_of_news(list_of_comments_links)
# print(list_news_description)

# print(list_news_comments)


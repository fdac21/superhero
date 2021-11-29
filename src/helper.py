"""
Helper functions to scrape all superrheroes data from 'https://www.superherodb.com/'
"""

from bs4 import BeautifulSoup
import urllib3
import pandas as pd
from collections import defaultdict
import requests
import re


def get_data(url):
    """
    Return BeautifulSoup html object.
    """
    r = requests.get(url)
    data = BeautifulSoup(r.text, "lxml")
    return data

def get_superheroes_links(data):
    herolinks = []

    home_url = "https://www.superherodb.com"

    for all_li in data.find_all(class_="list"):
        for link in all_li.find_all("li"):
            for hero in link.find_all("a"):
                herolinks.append(home_url + hero["href"])
    return herolinks

def get_id_from_about(filename):
    """
    Extract id from local filename.
    """
    return filename.replace("_about.html", "").split("/")[-1]


def get_soup(filename):
    with open(filename, "rb") as f:
        file = f.read()
        return BeautifulSoup(file, "lxml")


"""
About
"""


def get_image(data_about):
    if data_about.find(class_="portrait"):
        img = data_about.find(class_="portrait").find("img")
        if img:
            return dict(img=img["src"])
        else:
            return dict(img=None)
    else: return dict(img=None)


def get_name_real_name(data_about):
    if data_about.find("h1"):
        name = data_about.find("h1").text
        real_name = data_about.find("h2").text
    else:
        name = real_name = ""
    return dict(name=name, real_name=real_name)


def get_overall_score(data_about):
    if data_about.find(href="#class-info"):
        return dict(overall_score=data_about.find(href="#class-info").text)
    else: return dict(overall_score="")


# def get_power_stats(data_about):
#     #print(data_about)
#     scripts = data_about.findAll("script") or ["Error"]
#     script = ''
#     #print(scripts)
#     # Find script containng the 'stats_shdb'
#     if scripts != ['Error']:
#         for s in scripts:
#             if s.text.strip().startswith("var stats_shdb = ["):
#                 script = s
#         # script = [s.text for s in scripts if s.text.strip().startswith("var stats_shdb = [")]
# #         script = next(
# #             (s.text for s in scripts if s.text.strip().startswith("var stats_shdb = ["))
# #         )
#         # Extract the list of powers
#         values = re.findall(r"(\d+)", script.split(";")[0]) or [0]
#         values = [int(v) for v in values]
        
#         labels = data_about.find(class_="stat-holder").findAll("label") or ["Error"]
#         labels = [l.text for l in labels]
#     else:
#         labels, values = []

#     return dict(zip(labels, values))

def get_power_stats(data_about):
    script = ''
    if data_about.findAll("script"):
        scripts = data_about.findAll("script")
        for s in scripts:
            if s.text.strip().startswith("var stats_shdb = ["):
                script = s
        # Extract the list of powers
        values = re.findall(r"(\d+)", script.split(";")[0]) or [0]
        values = [int(v) for v in values]
        
        if data_about.find(class_="stat-holder"):
            labels = data_about.find(class_="stat-holder").findAll("label") or ["Error"]
            labels = [l.text for l in labels]
        else: labels = []
        return dict(zip(labels, values))
    else: return dict(zip([], []))


def get_super_powers(data_about):
    superpowers = data_about.find("h3", text="Super Powers")
    if superpowers:
        superpowers= superpowers.findParent().findAll("a")
        superpowers = [s.text for s in superpowers]
    return dict(superpowers=superpowers)


def get_all_links(td):
    links = td.findAll("a")
    links = [a.text for a in links]
    return links


def get_origin(data_about):
    if data_about.find("h3", text="Origin"):
        data = data_about.find("h3", text="Origin").findNext()

        origin = {}

        for row in data.find_all("tr"):
            key = row.find_all("td")[0].text
            value = row.find_all("td")[1]

            if "alter egos" in key.lower():
                origin[key] = get_all_links(value)
            else:
                origin[key] = value.text
        return origin
    else: return {}


def get_connections(data_about):
    if data_about.find("h3", text="Connections"):
        data = data_about.find("h3", text="Connections").findNext()

        connections = {}

        for row in data.find_all("tr"):
            key = row.find_all("td")[0].text
            value = row.find_all("td")[1]

            if "Teams" in key:
                connections[key] = get_all_links(value)
            else:
                connections[key] = value.text
    else: connections = {}

    return connections


def get_appearance(data_about):
    if data_about.find("h3", text="Appearance"):
        table = data_about.find("h3", text="Appearance").findParent()
        labels = table.findAll(class_="table-label") or ["Error"]
        return dict([(l.text, l.findNext().text) for l in labels])
    else: return dict([])


"""
History
"""


def get_history(data_history):
    content = data_history.find(class_="text-columns-2")
    if content:
        title = content.find("h3").text
        subtitles = [s.text for s in content.findAll("h4")]
        content = " ".join([p.text for p in content.findAll("p")]).replace("\s+", " ")
    else:
        title = subtitles = content = ""
    return {"hist_title": title, "hist_subtitles": subtitles, "hist_content": content}


"""
Powers
"""


def get_powers(data_powers):
    if len(data_powers.find_all(class_="col-8")) > 1:
        content = data_powers.find_all(class_="col-8")[1]
        title = content.find("h3").text
        subtitles = [s.text for s in content.findAll("h4")] or ["Error"]
        content = " ".join([p.text for p in content.findAll("p")]).replace("\s+", " ") or ["Error"]
        return {
            "powers_title": title,
            "powers_subtitles": subtitles,
            "powers_content": content,
        }
    else:
        return {
            "powers_title": "",
            "powers_subtitles": "",
            "powers_content": ""
        }


"""
Merge all
"""


def merge_data(data_about, data_history, data_powers):

    data = {}

    # Get from about page
    data.update(get_image(data_about))
    data.update(get_name_real_name(data_about))
    data.update(get_overall_score(data_about))
    data.update(get_power_stats(data_about))
    data.update(get_super_powers(data_about))
    data.update(get_origin(data_about))
    data.update(get_connections(data_about))
    data.update(get_appearance(data_about))

    # Get history data
    data.update(get_history(data_history))

    # Get powers data
    data.update(get_powers(data_powers))

    return data
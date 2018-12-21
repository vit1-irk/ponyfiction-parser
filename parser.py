#!/usr/bin/env python3

import urllib
import urllib.request
from io import StringIO, BytesIO
import lxml.html
import lxml.etree
import html2text
import pdb

topdomain = "https://ponyfiction.org"

def getFile(link):
    f = urllib.request.urlopen(link).read()
    return f
    
def totext(obj):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False

    return h.handle(lxml.etree.tounicode(obj)).replace("\.", ".").strip()

def fetchChapterData(doc):
    htmltext = doc.find_class("chapter-text-block")
    return totext(htmltext[0])

def fetchDescription(doc):
    desc = doc.find_class("story-description")
    notes = doc.find_class("story-notes")
    
    return totext(desc[0]) + "\n\n" + totext(notes[0])

def fetchTitle(doc):
    ttl = doc.get_element_by_id("story_title")
    return ttl[0][0].text

def fetchTags(doc):
    tags = []
    genres = doc.find_class("story-genres")[0].find_class("gen")
    for elem in genres:
        if elem.tag == "a":
            tags.append(elem.text)
    return tags
 
def storyMetaData(data):
    doc = lxml.html.fromstring(data)

    meta = {}
    chapters = []

    meta["description"] = fetchDescription(doc)
    meta["title"] = fetchTitle(doc)
    meta["tags"] = fetchTags(doc)
    
    elements = doc.find_class("story-chapters-list")

    if len(elements) == 0:
        fetchedtext = fetchChapterData(doc)
        chapter = {"title": "Единственная глава", "link": None, "text": fetchedtext}
        chapters.append(chapter)

        meta["chapters"] = chapters
        return meta, "single"

    ul = elements[0].getchildren()
    for li in ul:
        if len(li) > 0:
            a = li.getchildren()[0].getchildren()[0]
            chapter = {"title": a.text, "link": topdomain + a.get("href")}
            chapters.append(chapter)

    meta["chapters"] = chapters
    return meta, "many"

def chapterContents(data):
    doc = lxml.html.fromstring(data)
    return fetchChapterData(doc)

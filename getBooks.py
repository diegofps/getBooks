#!/usr/bin/python3

from lxml.html.soupparser import fromstring
from multiprocessing import Pool

import urllib.request
import unicodedata
import sys
import re
import os


FAILED = 0
SUCCESS = 1
SKIPPED = 2

r = re.compile("(http://link\.springer\.com/openurl\?genre=book&isbn=[0-9-]+)")
links = set()

with open("links", "r") as fin:
    for line in fin:
        s = r.search(line)
        if s:
            links.add(s.group(1))

def f(data):
    print("Checking", *data)
    
    page = urllib.request.urlopen(data[1])
    content = page.read()
    tree = fromstring(content)
    
    ee = [x.attrib["href"] for x in tree.xpath('//a') if x.attrib["href"].endswith(".pdf") and "title" in x.attrib and x.attrib["title"] == "Download this book in PDF format"]
    
    if len(ee) == 0:
        print("Unable to find link for ", *data)
        return None
    
    e = ee[0]
    
    title = tree.xpath('//div[@data-test="book-title"]/h1')
    if title:
        title = title[0].text_content()
    else:
        print("Unable to find title for ", *data)
    
    author = tree.xpath('//span[@class="authors__name"]')
    if author:
        author = author[0].text_content()
        author = unicodedata.normalize("NFKD", author)
    else:
        print("Unable to find author for ", *data)
    
    if title and author:
        filepath = title + " - " + author + ".pdf"
        
    elif title:
        filepath = title + ".pdf"
        
    else:
        filepath = str(data[0]) + ".pdf"
    
    filepath = filepath.replace("/", ",")
    url = "https://link.springer.com" + e
    
    return url, filepath, data[0]

def f2(data):
    url, filepath, idd = data
    
    if os.path.exists(filepath):
        print("Skipping:", filepath)
        return SKIPPED, filepath, idd
    
    tmpFilepath = filepath + ".tmp"
    
    cmd = "wget " + url + " -O \"" + tmpFilepath + "\""
    print("Downloading ", filepath, ":", cmd)
    status = os.system(cmd)
    
    if status != 0:
        print("FAILED TO DOWNLOAD ", filepath)
        return FAILED, filepath, idd
    
    status = os.system("mv \"" + tmpFilepath + "\" \"" + filepath + "\"")
    
    if status != 0:
        print("FAILED TO MOVE ", tmpFilepath)
        return FAILED, filepath, idd
    
    return SUCCESS, filepath, idd


jobs = [(i,x) for i,x in enumerate(links)]
threads = 8 if len(sys.argv) < 2 else int(sys.argv[1])

print("Number of candidate books:", len(jobs))

try:
    with Pool(threads) as p:
        print()
        print("Checking book names and urls...")
        result = p.map(f, jobs)
        failed_checks = len([x for x in result if not x])
        result = {x[1]:x for x in result if x}
        result = [x for x in result.values()]
    
        print()
        print("Downloading books...")
        result2 = p.map(f2, result)
    
    unique_names = len(result)
    failed_attempts = len([x for x in result2 if x[0] == FAILED])
    success_attempts = len([x for x in result2 if x[0] == SUCCESS])
    skipped_attempts = len([x for x in result2 if x[0] == SKIPPED])
    
    print()
    print("Candidate Books:", len(jobs))
    print("Failed Candidates:", failed_checks)
    print("Downloadable Books (removing duplicates):", unique_names)
    print("Success:", success_attempts)
    print("Fails:", failed_attempts)
    print("Skipped:", skipped_attempts)
    print()
    
    for a, b in zip(result, jobs):
        if a == FAILED:
            print("Failed to download:", *b)
except KeyboardInterrupt:
    print("Interrupted")


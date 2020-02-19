from bs4 import BeautifulSoup as Soup
import string
import urllib.request
import urllib.parse
import nltk
import sys
import re

def find_last(tag):
  return tag.name == "a" and tag.string == "Last »"

def scrape_page(soup):
  defs = soup.find_all(class_="def-panel")
  defs_text = []
  for defn in defs:
    meaning = defn.find(class_="meaning")
    text = ""
    for elem in meaning.contents:
      if elem.string:
        text += elem.string
      elif elem.name == "br":
        text += "\n"
    text = text.strip()
    defs_text.append(text)

  return defs_text

def scrape_term(term):
  term = urllib.parse.quote(term.lower())
  try:
    with urllib.request.urlopen("https://www.urbandictionary.com/define.php?term=" + term) as response:
      html = response.read()
      soup = Soup(html, features="html5lib")
      pagecnt = soup.find(find_last)
      if pagecnt:
        pagecnt = re.search("/define\.php\?term=" + term + "&page=(\d+)", pagecnt.attrs['href'], re.IGNORECASE)
        if pagecnt:
          pagecnt = int(pagecnt.group(1))

      defs = []

      defs.extend(scrape_page(soup))
      if pagecnt:
        for p in range(2, pagecnt + 1):
          with urllib.request.urlopen("https://www.urbandictionary.com/define.php?term=" + term + \
                               "&page=" + str(p)) as response:
            html = response.read()
            soup = Soup(html, features="html5lib")
            defs.extend(scrape_page(soup))
  except Exception:
    return [term]

  return defs

def replace_nouns(text, defn_cap):
  words = nltk.pos_tag(nltk.word_tokenize(text))
  output = ""
  for word in words:
    if word[1] == "NNP" or word[1] == "NN":
      defs = scrape_term(word[0])
      valid_defs = []
      for defn in defs:
        if len(defn.split()) < defn_cap:
          valid_defs.append(defn)
      if valid_defs:
        valid_defs.sort(key=len)
        defn = re.sub(r'[^\w\s]', '', valid_defs[0].lower()).strip()
        if word[0].isupper():
          defn = defn[0].upper() + defn[1:]
        output += defn + " "
        print(defn + " ", end="")
      else:
        output += word[0] + " "
        print(word[0] + " ", end="")
    else:
      output += word[0] + " "
      print(word[0] + " ", end="")
    sys.stdout.flush()

  return output[0:-1]

if __name__ == "__main__":
  mdef = 10
  if len(sys.argv) < 2:
    print("Please supply a filepath")
    sys.exit(1)
  elif len(sys.argv) > 2:
    mdef = int(sys.argv[2])
  with open(sys.argv[1], "r") as fp:
    replace_nouns(fp.read(), mdef)

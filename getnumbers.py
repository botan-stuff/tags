bookmarks_html = open(r"bookmarks.html", "r")  # replace bookmarks.html with file name or location
lines = bookmarks_html.readlines()
sanitized_links = []

for line in lines:
    if line.strip() == "dummy":
        print("ERROR: you did not provide a functional bookmarks.html file")
        raise RuntimeError("ERROR: you did not provide a functional bookmarks.html file")
    # get all urls in the file
    if "HREF" in line:
        working_line = line.split("\"")
        link = working_line[1]
        # filter for what we're looking for
        if "chrome://newtab" not in link and "nhentai.net" in link and "artist" not in link and "group" not in link and "search" not in link and "parody" not in link and "tag" not in link and "character" not in link and "page" not in link and "https://nhentai.net/" != link:
            sanitized_links.append(link)
            
categories = [] # separate links by domain name
for link in sanitized_links:
    working_link = link.split(":")
    working_link = working_link[1][2:]
    working_link = working_link.split("/")[0]
    if working_link not in categories:
        categories.append(working_link)
categorized_links = {}
for category in categories:
    categorized_links[category] = []
    
for link in sanitized_links:
    # remove irrelevant parts of the url
    working_link = link.split(":")
    working_link = working_link[1][2:]
    working_link = working_link.split("/")[0]
    if link not in categorized_links[working_link]: # avoids duplicates
        link = link.split("https://nhentai.net/g/")[1]
        link = link.split("/")[0]
        #appends only the id
        categorized_links[working_link].append(link)
numbers = categorized_links["nhentai.net"]
numbers = list(dict.fromkeys(numbers))
results = open(r"numbers.txt", "w")
for i in numbers:
    results.write(f"{i}\n")
bookmarks_html.close()
results.close()

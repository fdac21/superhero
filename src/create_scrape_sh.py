"""
Create sh download file to grab all the files for each superhero
"""

import helper as h

all_links = []
herolinks = [0] 
counter = 1
while len(herolinks) > 0:
    data = h.get_data("https://www.superherodb.com/characters/?page_nr={}".format(counter))
    herolinks = h.get_superheroes_links(data)
    all_links += herolinks
    counter += 1

DOWNLOAD_DIR = "./data/raw/"

file_content = ""
command = "wget {} -t 5 --limit-rate=20K --show-progress -O {}\n"

file_content += "#!/bin/sh\n\n\n"
file_content += "mkdir -p {}\n\n\n".format(DOWNLOAD_DIR)

filename_set = []

for link in all_links:

    filename = DOWNLOAD_DIR + link.split("/")[-3]

    # Download about
    filename_about = filename + "_about.html"
    file_content += command.format(link, filename_about)

    # Download history
    filename_history = filename + "_history.html"
    file_content += command.format(link + "history/", filename_history)

    # Download powers
    filename_powers = filename + "_powers.html"
    file_content += command.format(link + "powers/", filename_powers)

    file_content += "\n"

    filename_set.append(filename)

print("There are ", len(filename_set), " files.")
print("There are ", len(set(filename_set)), "unique files.")

with open("download.sh", "w") as file:
    file.write(file_content)
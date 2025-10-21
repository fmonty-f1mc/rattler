from os import walk

#gonna stash all the tpls in html list for easy access
filenames = next(walk("app/tpls"), (None, None,[]))[2]
html_files=[x.split(".")[0] for x in filenames if x != '__init__.py']

tpls={}

for i in html_files:
    with open(f"app/tpls/{i}.html", 'r', encoding='utf-8') as file:
    # Read the entire content of the file into a string
        tpls[i]=file.read()
    
#print(tpls)
import os
DOC_PATHS = [os.path.join(os.getcwd(), 'data', f) for f in os.listdir('data')] # list of docx files in data folder
print(DOC_PATHS)
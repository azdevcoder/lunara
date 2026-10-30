import glob
import re

classes = set()
for path in glob.glob("app/templates/**/*.html", recursive=True):
    text = open(path, encoding="utf-8").read()
    classes.update(re.findall(r'class="([^"]+)"', text))

tokens = set()
for value in classes:
    for token in value.split():
        if "{" not in token and "}" not in token:
            tokens.add(token)
print("\n".join(sorted(tokens)))

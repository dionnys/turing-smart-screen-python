import urllib.request
import re

html_content = urllib.request.urlopen('https://arcraiders.nexon.com/en-US/main').read().decode('utf-8')
pngs = re.findall(r'src="(.*?\.png)"', html_content, re.IGNORECASE)
jpegs = re.findall(r'src="(.*?\.jpg)"', html_content, re.IGNORECASE)
svgs = re.findall(r'src="(.*?\.svg)"', html_content, re.IGNORECASE)

print("SVGs found:")
for svg in svgs: print(svg)
print("PNGs found:")
for png in pngs: print(png)


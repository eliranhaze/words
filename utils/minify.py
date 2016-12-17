import re

def minify_feed(content):
    content = re.sub('<content:encoded[\s\S]*?</content:encoded>', '', content)
    content = re.sub('<description[\s\S]*?</description>', '', content)
    return content

def minify_html2(content):
    content = re.sub('<footer[\s\S]*?</footer>', '', content)
    content = re.sub('<nav[\s\S]*?</nav>', '', content)
    content = re.sub('<script[\s\S]*?</script>', '', content)
    content = re.sub('<form[\s\S]*?</form>', '', content)
    content = re.sub('<style[\s\S]*?</style>', '', content)
    content = re.sub('<h[1-6][\s\S]*?</h[1-6]>', '', content)
    content = re.sub('<!--[\s\S]*?-->', '', content)
    content = re.sub('href=".*?"', '', content)
    content = re.sub('src=".*?"', '', content)
    content = ' '.join(content.split())
    return content

def minify_html(content):
    content = re.sub('<footer[\s\S]*?</footer>', '', content)
    content = re.sub('<nav[\s\S]*?</nav>', '', content)
    content = re.sub('<script[\s\S]*?</script>', '', content)
    content = re.sub('<form[\s\S]*?</form>', '', content)
    content = re.sub('<style[\s\S]*?</style>', '', content)
    content = re.sub('<h[1-6][\s\S]*?</h[1-6]>', '', content)
    content = re.sub('<!--[\s\S]*?-->', '', content)
    content = re.sub('href=".*?"', '', content)
    content = re.sub('src=".*?"', '', content)
    content = content.replace('  ','').replace('\n\n','\n')
    return content


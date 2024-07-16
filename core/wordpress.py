import codecs
import requests
import datetime
from base64 import b64encode
from requests.auth import HTTPBasicAuth

URI = "https://www.ashtarey.com/wp-json/wp/v2"
baseToken = "6rTz Q4Cd r7Xi xtqV jXiu Aij4"

baseToken2 = "mM9E iKMJ WMDt x0oo owjI y0dq"
user = "ashtarey.com"
class BasicAuthToken(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        authstr = 'Basic ' + b64encode(('token:' + self.token).encode('utf-8')).decode('utf-8')
        r.headers['Authorization'] = authstr
        return r


def getToken():
    token = codecs.encode(baseToken,'base64').decode()
    print(token)
    return token



def uploadImage(imageID):
    imagePath = f"media/{imageID}.jpg"
    headers = {
        "Content Type": "image/jpg",
        "Content Disposition": "attachment filename=$image",
    }
    response = requests.post(URI+'/media',auth=HTTPBasicAuth(user,baseToken),headers=headers)

    if(response.status_code == 201):
        data = reaponse.json()
        imageLink = data["guid"]["rendered"]
        return imageLink
    else:
        return "Image was not uploaded"

def createPost(msgs):
    title = "عروض اليوم"
    templates = []
    currentDate = datetime.datetime.now()
    #File jsonMessages = File("assets/messages/msg.json") 
    print(title)
    for msg in msgs:
        date = msg['date'].strftime('%Y-%m-%d')
        if (date != currentDate):
            #continue
        #else:
            textLines = msg["message"].split("\n")
            link = textLines[-1]
            print(textLines)
            textLines = textLines[:-3]
            #input('continue ?\n>')
            text = "\n".join(textLines)
            imageUrl = uploadImage(int(msg["id"]))
            template = u'<p>{content}</p><br><br><br><br><p><a href="{website}" target="_blank" rel="noreferrer noopener">من هنا</a></p><br><br><br><br><figure class="wp-block-image size-large"><img fetchpriority="high" decoding="async" width="679" height="744" src="{img}" sizes="(max-width: 679px) 100vw, 679px" alt="No image for this offer"/><figcaption class="wp-element-caption">Image</figcaption></figure>'.format(content=text,website=link,img=imageUrl)
            templates.append(template)


    post = {
    "status": "draft",
    "type": "post",
    "title": title,
    "content": "".join(templates),
    "author":1,
    "format": "standard"
    }

    response = requests.post(URI+'/posts',auth=HTTPBasicAuth(user,baseToken), params=post)
    print(response.status_code)
    print(response.json())
    if(response.status_code == 201):
        print(response.json())
        return "Post was created successfully"
    else:
        return "There was an issue with the post"

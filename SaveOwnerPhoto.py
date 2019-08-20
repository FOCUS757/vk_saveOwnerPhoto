import os
import time
import random
import requests

import vk_api

from vk_api.utils import get_random_id
from urllib import urlretrieve

def captcha_handler(captcha):
    print("Waiting for captcha input")
    captcha_url = captcha.get_url()
    
    urlretrieve(captcha_url, "captcha.jpg")
    
    key = send_captcha(captcha_url)
    
    print(key)
    return captcha.try_again(key)

def send_captcha(captcha_url):
    token = "group token"
    
    vk_session = vk_api.VkApi(token = token)
    vk = vk_session.get_api()
    
    url = vk.photos.getMessagesUploadServer()['upload_url']
    
    request = requests.post(url, files={'photo': open("captcha.jpg", 'rb')}).json()
    
    photo = vk.photos.saveMessagesPhoto(server=request['server'],
                                        photo = request['photo'],
                                        hash = request['hash'])
    
    attachment = 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
    
    vk.messages.send(
        user_id="you profile id",
        attachment = attachment,
        random_id=get_random_id())
    
    os.remove("captcha.jpg")
    
    key = ''
    while (key == ''):
        messages = vk.messages.getDialogs()['items'][0]
        if 'attachments' not in messages['message'].keys():
            key = messages['message']['body']
    return key

def main():
    vk_session = vk_api.VkApi('+7999132****', '*********', captcha_handler=captcha_handler)
    vk_session.auth()
    
    vk = vk_session.get_api()
    
    images = os.listdir("images")
    
    url = vk.photos.getOwnerPhotoUploadServer()['upload_url']
    
    photo = []
    for image in images:
        request = requests.post(url, files={'photo': open('images/'+image, 'rb')}).json()
        photo.append(request['photo'])
    
    server = request['server'] 
    hash = request['hash']
    
    y = 0
    while(True):
        x = random.randint(0, len(photo)-1)
        while(x == y):
            x = random.randint(0, len(photo)-1)
        y = x
                   
        vk.photos.saveOwnerPhoto(server = server, hash = hash, photo = photo[x])
    
        posts = vk.wall.get()
        post_id = posts["items"][0]["id"]
        vk.wall.delete(post_id = post_id)
          
        photos = vk.photos.getAll()
        if (photos['count']>1):
            photo_id = photos["items"][1]["id"]
            vk.photos.delete(photo_id = photo_id)
            
        print("Successfully", x)
        time.sleep(60)
        
if __name__ == '__main__':
    main()

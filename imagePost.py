import sys, getopt
import json
import requests

def main(argv):
   page_id = ''
   page_token = ''
   image_url = ''
   caption = ''
   try:
      opts, args = getopt.getopt(argv,"hi:t:u:c:",["id=","token=","url=","caption="])
   except getopt.GetoptError:
      print('post.py -i <page_id> -t <Page_token> -u <image_url> -c [caption]')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('post.py -i <page_id> -t <Page_token> -u <image_url> -c [caption]')
         sys.exit()
      elif opt in ("-i", "--id"):
         page_id = arg
      elif opt in ("-t", "--token"):
         page_token = arg
      elif opt in ("-u", "--url"):
         image_url = arg
      elif opt in ("-c", "--caption"):
         caption = arg 

   if page_id == "" or page_token == "":
      print("Page id and Page access token are required")
      sys.exit(2)
   elif(image_url == ""):
         print("Image url is required")
         sys.exit(2)
   else:
         if(caption == ""):
            params = json.dumps({
               "url":image_url
               })
         else:
            params = json.dumps({
               "url":image_url, 
               "caption":caption
               })
   print(params)
   #post_url = "https://graph.facebook.com/{}/photos?access_token={}".format(page_id,page_token)
   #status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
   #print(status.json())

if __name__ == "__main__":
   main(sys.argv[1:])

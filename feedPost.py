import sys, getopt
import json
import requests

def main(argv):
   page_id = ''
   page_token = ''
   message = ''
   url = ''
   try:
      opts, args = getopt.getopt(argv,"hi:t:m:u:",["id=","token=","url=","caption="])
   except getopt.GetoptError:
      print('post.py -i <page_id> -t <Page_token> -m <message> -u [url]')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('post.py -i <page_id> -t <Page_token> -m <message> -u [url]')
         sys.exit()
      elif opt in ("-i", "--id"):
         page_id = arg
      elif opt in ("-t", "--token"):
         page_token = arg
      elif opt in ("-m", "--url"):
         message = arg
      elif opt in ("-u", "--caption"):
         url = arg 

   params = None 

   if page_id == "" or page_token == "":
      print("Page id and Page access token are required")
      sys.exit(2)
   elif message == "":
      print("Post text is required")
      sys.exit(2)
   else:
      if (url == ""):
         params = json.dumps({
                  "message":message
               }) 
      else:
         params = json.dumps({
                  "message":message, 
                  "url":url 
               })

   post_url = "https://graph.facebook.com/{}/feed?access_token={}".format(page_id,page_token)
   status = requests.post(post_url, headers={"Content-Type": "application/json"},data=params)
   print(status.json())


if __name__ == "__main__":
   main(sys.argv[1:])



from flask import Flask, jsonify, request
from celery import Celery
from google_play_scraper import app as play_detail
# from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://rabbitmq//'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'
app.config['MONGO_URI'] = 'mongodb://mongo:27017/playstore_db'

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database()
coll = db["app_details"]

coll.create_index("appId", unique=True)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# @celery.task
# def scrape_playstore(package_name):
#     return app(package=package_name, lang='en', country='us')

@celery.task
def echo(time):
    print("i am celery", time)
    return True

@app.route('/api/apps')
def get_app_details():
    # Scrape the Play Store games page to get the package names
    # and enqueue the scraping tasks
    scrape_package_names.delay()
    # tasks = []
    # for package_name in package_names:
    #     tasks.append(scrape_playstore.delay(package_name))

    # # Fetch the results from the tasks and store them in a list
    # app_details = [task.get() for task in tasks]

    # Store the app details in a database (implementation not shown)
    # store_in_database(app_details)

    # return jsonify(app_details), 200
    # echo.delay(datetime.now())
    return "Stated fetching..."

@app.route("/get_details")
def get_one_app_detail():
    app_id = request.args.get("app_id")
    data = coll.find_one({"appId": app_id})
    if data == None:
        # return "None", 404
        return f"app_id = {app_id} Not Found", 404
    else:
        data["_id"] = str(data["_id"])
        return jsonify(data), 200


def souped(html_text):
    app_id_lists = []
    soup = BeautifulSoup(html_text, "html.parser")
    a1 = soup.findAll(class_="Si6A0c Gy4nib")
    for x in a1:
        url = x.get("href")
        if url != None:
            app_id = url.split("=")[1]
            # print(app_id)
            app_id_lists.append(app_id)
    return app_id_lists

def get_details(app_id_lists):
    count = 0
    for x in app_id_lists:
        if count == 2:
            return
        # This will fetch details from google play store using
        # google_play_scraper lib
        data = play_detail(x, lang="en", country="us")
        store_in_database(data)
        count += 1
        
        

def store_in_database(app_detail):
    # Implement database storage logic here
    print("from store in database", app_detail.get("appId"))
    appId = app_detail.get("appId")
    # print("app")
    count = coll.count_documents({"appId": appId})
    if count == 1:
        print("exists")
    else:
        coll.insert_one(app_detail)
        print("inserted", app_detail.get("appId"))



@celery.task
def scrape_package_names():
    # Implement scraping of package names from the Play Store games page
    # You can use libraries like BeautifulSoup or Scrapy for web scraping
    # Return a list of package names
    r = requests.get("https://play.google.com/store/games?hl=en&gl=US")
    if r.status_code == 200:
        app_id_lists = souped(r.text)
        get_details(app_id_lists)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

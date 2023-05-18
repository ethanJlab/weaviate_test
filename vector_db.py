import weaviate
from weaviate.embedded import EmbeddedOptions
import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
import openai
load_dotenv()

# these are the api endpoints to interact with the vectorDB

openai.api_key = os.getenv("OPENAIAPIKEY")

# use this to make requests using the requests library
baseURL = "http://localhost:8080"

# use this to make requests using the weviate SDK
client = weaviate.Client(baseURL)

mainClass = "Topic"

# schema used for DB
schema = {
    "classes": [{
    "class":"Topic",
    "properties":[
        {
            "dataType":["text"],
            "description":"The contents of the topic to be vectorized.",
            "name":"content"
        }
    ]
    }]
}

# define the backedend application to 
app = Flask(__name__)

# route to get all topics from the DB
@app.route('/vector/getAllTopics', methods=['GET'])

def getAllTopics():
    #get all request
    x = requests.get(baseURL + '/v1/objects?class=Topic&')
    return jsonify(x.json())

# route to get all of a spacific class
@app.route('/vector/getAllOfClass', methods=['POST'])

def getAllOfClass():
    #get all of a class
    className = request.json['className']
    x = requests.get(baseURL + '/v1/objects?class=' + className + '&')
    return jsonify(x.json())

@app.route('/vector/initializeDB', methods=['POST'])

def initializeDB():
    #initialize DB
    client.schema.create(schema)
    return "DB Initialized"

@app.route('/vector/getSchema', methods=['POST'])

def getSchema():
    #get schema
    return jsonify(client.schema.get())

@app.route('/vector/addTopic', methods=['POST'])

def addTopic():
    #add topic
    content = request.json['content']
    client.batch.add_data_object(
        data_object = {"content": content}, 
        class_name = "Topic"
    )
    result = client.batch.create_objects()
    return jsonify(result)

@app.route('/vector/deleteAll', methods=['POST'])

#does not work
def deleteAllTopics():
    # delete all topics
    x = requests.get(baseURL + '/v1/objects?class=Topic&')
    return jsonify(x.json())

@app.route('/vector/query', methods=['POST'])

def vectorQuery():
    queryContent = request.json['content']
    keywords = ""
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [{"role":"system", "content": queryContent + ". Based on this query, generate keywords in one line."}],
    )

    keywords = response["choices"][0].message.content
    print(keywords)
    ret = client.query.get("Topic", ["content"]).with_near_text({"concepts":[keywords]}).do()
    return ret





#client.schema.create(schema)

#client.batch.add_data_object(
#    data_object = {"contents": "Hello my name is Ethan and I am a computer scientist. I graduated from the university of central florida. I am 22 years of age.", "topic": "Student Information on Ethan"}, 
#    class_name = "Topic"
#)
#result = client.batch.create_objects()

#result = client.query\
#    .get("Topic",["contents"])\
#    .do()
#print(result)
#print(client.schema.get())

app.run(port =5050)
# video-based-learning
FLASK_APP=web.py flask run
http://127.0.0.1:5000/
Developed tutoring system based on web learning.



## Pre-configuration for Elasticsearch

Run following codes on kibana (http://localhost:5601) before storing docs

Apply `english` analyzer on `questions` index.

```
PUT questions
{
  "mappings": {
    "_doc": {
      "properties": {
        "question": {
          "type": "text",
          "analyzer": "english"
        }
      }
    }
  }
}
```
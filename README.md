# video-based-learning

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

### Using virtualenv

Installing venv
`python3 -m venv env`

Activate venv
`source env/bin/activate`

Deactivate venv
`deactivate`

### Running webapp

source env/bin/activate
python web.py

Visit http://127.0.0.1:5000/
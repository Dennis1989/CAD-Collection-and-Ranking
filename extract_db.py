import mephisto.abstractions.blueprints.ranking_task.db as db
from mongoengine import *
import json
import os

DATABBASE_URL = "mongodb://root:better_password@mongo:27017"
connect(host=DATABBASE_URL)

cad_pipeline = [
  {
    "$match": {"outputCad": {"$exists": True}}
  },
  {
    "$lookup": {
      "from": db.CAD._get_collection().name,
      "pipeline": [{
        "$lookup": {
          "from": db.Sentence._get_collection().name,
          "localField": "original",
          "foreignField": "_id",
          "as": "original"
        }
      }],
      "localField": "outputCad",
      "foreignField": "_id",
      "as": "outputCad"
    }
  },
]

ranking_pipeline = [
  {
    "$match": {"outputRanking": {"$exists": True}}
  },
  {
    "$lookup": {
      "from": db.Ranking._get_collection().name,
      "localField": "outputRanking",
      "foreignField": "_id",
      "as": "outputRanking"
    }
  },
]

rejected_pipeline = [
  {
    "$match": {"outputExplanation": {"$exists": True}}
  },
  {
    "$lookup": {
      "from": db.SkipExplanation._get_collection().name,
      "localField": "outputExplanation",
      "pipeline": [
        {
          "$lookup": {
            "from": db.Sentence._get_collection().name,
            "localField": "original",
            "foreignField": "_id",
            "as": "original"
          }
        }],
      "foreignField": "_id",
      "as": "outputExplanation"
    }
  },
]

unfinished_units = [
  {
    "$match": {"outputExplanation": {"$exists": False}}
  },
  {
    "$match": {"outputCad": {"$exists": False}}
  },
  {
    "$match": {"outputRanking": {"$exists": False}}
  },
]

# aggregate
cad_units        = list(db.Unit._get_collection().aggregate(cad_pipeline))
for u in cad_units:
  u['_id'] = str(u['_id'])
  u['startTime'] = u['startTime'].timestamp()
  u['endTime'] = u['endTime'].timestamp()
  # clean output cad
  u['outputCad'] = u['outputCad'][0]
  u['outputCad']['_id'] = str(u['outputCad']['_id'])
  # clean output cad sentence
  u['outputCad']['original'] = u['outputCad']['original'][0]
  u['outputCad']['original']['_id'] = str(u['outputCad']['original']['_id'])

ranking_units    = list(db.Unit._get_collection().aggregate(ranking_pipeline))
for u in ranking_units:
  u['_id'] = str(u['_id'])
  u['startTime'] = u['startTime'].timestamp()
  u['endTime'] = u['endTime'].timestamp()
  # clean ranking
  u['outputRanking'] = u['outputRanking'][0]
  u['outputRanking']['_id'] = str(u['outputRanking']['_id'])
  u['outputRanking']['cads'] = [ str(id) for id in u['outputRanking']['cads'] ]

rejected_units   = list(db.Unit._get_collection().aggregate(rejected_pipeline))
for u in rejected_units:
  u['_id'] = str(u['_id'])
  u['startTime'] = u['startTime'].timestamp()
  u['endTime'] = u['endTime'].timestamp()
  # clean feedback
  u['outputExplanation'] = u['outputExplanation'][0]
  u['outputExplanation']['_id'] = str(u['outputExplanation']['_id'])
  # clean original
  u['outputExplanation']['original'] = u['outputExplanation']['original'][0]
  u['outputExplanation']['original']['_id'] = str(u['outputExplanation']['original']['_id'])

unfinished_units = list(db.Unit._get_collection().aggregate(unfinished_units))
for u in unfinished_units:
  u['_id'] = str(u['_id'])
  u['startTime'] = u['startTime'].timestamp()

# write to files
dump_path = './dump'
with open(os.path.join(dump_path, 'cad_units.json'), 'w+') as f:
  f.write(json.dumps(cad_units))
with open(os.path.join(dump_path, 'ranking_units.json'), 'w+') as f:
  f.write(json.dumps(ranking_units))
with open(os.path.join(dump_path, 'unfinished_units.json'), 'w+') as f:
  f.write(json.dumps(unfinished_units))
with open(os.path.join(dump_path, 'rejected_units.json'), 'w+') as f:
  f.write(json.dumps(rejected_units))
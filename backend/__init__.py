from flask import Flask
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
from backend import config
import requests
import json
import numpy as np
app = Flask(__name__)
CORS(app) # required for Cross-origin Request Sharing
api = Api(app)

parser = reqparse.RequestParser()

class ActorList(Resource):

    def get(self):
        print("Call for: GET /actors")
        url = config.es_base_url['actors']+'/_search'
        query = {
            "query": {
                "match_all": {}
            },
            "size": 100
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        actors = []
        for hit in data['hits']['hits']:
            actor = hit['_source']
            actor['id'] = hit['_id']
            actors.append(actor)
        return actors

    def post(self):
        print("Call for: POST /actors")
        parser.add_argument('first_name')
        parser.add_argument('last_name')
        # parser.add_argument('abv')
        # parser.add_argument('description')
        # parser.add_argument('titles', action='append')
        actor = parser.parse_args()
        print(actor)
        url = config.es_base_url['actors']
        resp = requests.post(url, data=json.dumps(actor))
        data = resp.json()
        return data

api.add_resource(ActorList, config.api_base_url + '/actors')

class Actor(Resource):

    def get(self, actor_id):
        print("Call for: GET /actors/%s" % actor_id)
        url = config.es_base_url['actors']+'/'+actor_id
        resp = requests.get(url)
        data = resp.json()
        actor = data['_source']
        return actor

    def put(self, actor_id):
        """TODO: update functionality not implemented yet."""
        pass

    def delete(self, actor_id):
        print("Call for: DELETE /actors/%s" % actor_id)
        url = config.es_base_url['actors']+'/'+actor_id
        resp = requests.delete(url)
        data = resp.json()
        return data

class Title(Resource):
    def get(self, title_id):
        print("Call for: GET /titles/%s" % title_id)
        url = config.es_base_url['titles']+'/'+title_id
        resp = requests.get(url)
        data = resp.json()
        title = data['_source']
        return title

    def put(self, title_id):
        """TODO: update functionality not implemented yet."""
        pass

    def delete(self, title_id):
        print("Call for: DELETE /titles/%s" % title_id)
        url = config.es_base_url['titles']+'/'+title_id
        resp = requests.delete(url)
        data = resp.json()
        return data

class TitleList(Resource):

    def get(self):
        print("Call for /titles")
        url = config.es_base_url['titles']+'/_search'
        query = {
            "query": {
                "match_all": {}
            },
            "size": 100
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        titles = []
        for hit in data['hits']['hits']:
            title = hit['_source']
            title['id'] = hit['_id']
            titles.append(title)
        return titles

    def post(self):
        print("Call for: POST /actors")
        parser.add_argument('short_title')
        # parser.add_argument('abv')
        # parser.add_argument('description')
        # parser.add_argument('titles', action='append')
        title = parser.parse_args()
        print(title)
        url = config.es_base_url['titles']
        resp = requests.post(url, data=json.dumps(title))
        data = resp.json()
        return data

api.add_resource(TitleList, config.api_base_url+'/titles')
class L(list):
    """
    A subclass of list that can accept additional attributes.
    Should be able to be used just like a regular list.

    The problem:
    a = [1, 2, 4, 8]
    a.x = "Hey!" # AttributeError: 'list' object has no attribute 'x'

    The solution:
    a = L(1, 2, 4, 8)
    a.x = "Hey!"
    print a       # [1, 2, 4, 8]
    print a.x     # "Hey!"
    print len(a)  # 4

    You can also do these:
    a = L( 1, 2, 4, 8 , x="Hey!" )                 # [1, 2, 4, 8]
    a = L( 1, 2, 4, 8 )( x="Hey!" )                # [1, 2, 4, 8]
    a = L( [1, 2, 4, 8] , x="Hey!" )               # [1, 2, 4, 8]
    a = L( {1, 2, 4, 8} , x="Hey!" )               # [1, 2, 4, 8]
    a = L( [2 ** b for b in range(4)] , x="Hey!" ) # [1, 2, 4, 8]
    a = L( (2 ** b for b in range(4)) , x="Hey!" ) # [1, 2, 4, 8]
    a = L( 2 ** b for b in range(4) )( x="Hey!" )  # [1, 2, 4, 8]
    a = L( 2 )                                     # [2]
    """
    def __new__(self, *args, **kwargs):
        return super(L, self).__new__(self, args, kwargs)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            list.__init__(self, args[0])
        else:
            list.__init__(self, args)
        self.__dict__.update(kwargs)

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

class Search(Resource):

    def get(self):
        print("Call for GET /search")
        parser.add_argument('q')
        query_string = parser.parse_args()
        url = config.es_base_url['actors']+'/_search'
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query_string['q'],
                            "fields": ["first_name","last_name"],
                            "fuzziness": np.sqrt(len(query_string['q'])),
                            "analyzer": "autocomplete_search"}
                            },"field_value_factor": {
                                "field": "popularity",
                                "modifier": "log1p",
                                "factor": 1},
                                "boost_mode": "multiply", "max_boost": 1}
                                },
                    "size": 12
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        actors = L()
        actors.took = data["took"]
        for hit in data['hits']['hits']:
            actor = hit['_source']
            actor['ms'] = data["took"]
            actor['id'] = hit['_id']
            actors.append(actor)
        return actors

api.add_resource(Search, config.api_base_url+'/search')

class Search2(Resource):

    def get(self):
        print("Call for GET /search")
        parser.add_argument('q')
        query_string = parser.parse_args()
        url = config.es_base_url['titles']+'/_search'
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "multi_match": {
                            "query": query_string['q'],
                            "fields": ["short_title"],#,"rubric","keywords"],
                            "fuzziness": np.sqrt(len(query_string['q'])),
                            "analyzer": "autocomplete_search"}
                            },"field_value_factor": {
                                "field": "pop2",
                                "modifier": "log1p",
                                "factor": 10},
                                "boost_mode": "multiply", "max_boost": 10}
                                },
                    "size": 12
        }
        resp = requests.post(url, data=json.dumps(query))
        data = resp.json()
        actors = L()
        actors.took = data["took"]
        for hit in data['hits']['hits']:
            actor = hit['_source']
            actor['ms'] = data["took"]
            actor['id'] = hit['_id']
            actors.append(actor)
        return actors

api.add_resource(Search2, config.api_base_url+'/search2')

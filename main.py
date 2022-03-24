import datetime
import json
import os

import requests
from flask import Flask, render_template
from sta.client import Client

app = Flask(__name__)

DEBUG = False
ENDPOINTS = {'st2': 'https://st2.newmexicowaterdata.org/FROST-Server/v1.1',
             'nmenv': 'https://nmenv.newmexicowaterdata.org/FROST-Server/v1.1',
             'ose': 'https://ose.newmexicowaterdata.org/FROST-Server/v1.1'}


def get_count(url, tag):
    url = f'{url}/{tag}?$top=1&$count=True'
    resp = requests.get(url)
    if resp:
        return resp.json()['@iot.count']


def make_endpoint_stats(key):
    url = ENDPOINTS[key]

    return {tag: get_count(url, tag) for tag in ('Locations',
                                                 'Things',
                                                 'Datastreams',
                                                 'Observations')}


@app.route('/stats')
def stats():
    p = './stats.json'
    make_live_stats()

    def make_row(tag, name):
        counts = obj[tag]
        row = [f'<td>{name}</td>']
        row.extend([f'<td>{counts[t]}</td>' for t in ('Locations', 'Things', 'Datastreams', 'Observations')])

        return ''.join(row)

    with open(p, 'r') as rfile:
        obj = json.load(rfile)
        payload = {'st2': make_row('st2', 'ST2'),
                   'nmenv': make_row('nmenv', 'NMENV'),
                   'ose': make_row('ose', 'OSE'),
                   }

        return json.dumps(payload)


def make_live_stats(overwrite=False):
    p = './stats.json'
    if not os.path.isfile(p) or overwrite:
        obj = {key: make_endpoint_stats(key) for key in ('st2', 'nmenv', 'ose')}

        with open(p, 'w') as wfile:
            json.dump(obj, wfile)


@app.route('/assemble_locations')
def assemble_locations():
    _assemble_locations()


@app.route('/cr_assemble_locations')
def chron_assemble_locations():
    _assemble_locations(overwrite=True)


def _assemble_locations(keys=None, overwrite=False):
    if keys is None:
        keys = ('st2', 'nmenv', 'ose')

    for key in keys:
        client = Client(base_url=ENDPOINTS[key])
        if key == 'ose':
            cnt = 1
            # service = fsc.SensorThingsService(ENDPOINTS[key])
            # gen = service.locations().query().list()
            gen = client.locations()
            for cnt in range(5):
                p = f'./{key}_locations-{cnt:05n}.json'

                locations = []
                for i in range(50000):
                    try:
                        locations.append(next(gen))
                    except StopIteration:
                        break

                with open(p, 'w') as wfile:
                    json.dump(locations, wfile)

        else:
            p = f'./{key}_locations.json'
            if os.path.isfile(p) and not overwrite:
                continue

            locations = list(client.get_locations())
            with open(p, 'w') as wfile:
                json.dump(locations, wfile)


@app.route('/nmenvlocations')
def nmedlocations():
    return ajax_locations('nmenv',
                          options={'color': 'red', 'radius': 2}, )


@app.route('/st2locations')
def st2locations():
    return ajax_locations('st2', options={'color': 'green',
                                          'radius': 2},
                          fuzzy_options={'color': 'blue'})


@app.route('/oselocations')
def oselocations():
    markers = []
    fuzzy_markers = []
    for i in range(10):
        pp = f'./ose_locations-{i:05n}.json'
        # print(pp, os.path.isfile(pp))
        if os.path.isfile(pp):
            pay = locations_to_payload(pp)
            markers.extend(pay['markers'])
            fuzzy_markers.extend(pay['fuzzy_markers'])
            # with open(pp) as rfile:
            #     obj = json.load(rfile)
    payload = {'options': {'color': 'blue', 'radius': 1},
               'markers': markers,
               'fuzzy_markers': fuzzy_markers}
    return json.dumps(payload)


def ajax_locations(tag, options=None, fuzzy_options=None):
    _assemble_locations(keys=(tag,), overwrite=False)
    p = f'./{tag}_locations.json'
    payload = locations_to_payload(p)
    if options:
        payload['options'] = options
    if fuzzy_options:
        payload['fuzzy_options'] = fuzzy_options

    return json.dumps(payload)


def locations_to_payload(p):
    with open(p, 'r') as rfile:
        obj = json.load(rfile)
        markers = [r['location'] for r in obj if r['location']['type'] == 'Point']
        fuzzy_markers = [r['location'] for r in obj if r['location']['type'] != 'Point']
        return {'markers': markers,
                'fuzzy_markers': fuzzy_markers}


@app.route('/')
def root():
    return render_template('index.html')
    # markers=markers)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

# -*- coding: utf-8 -*-  

from flask import Flask, Blueprint
from flask_restful import reqparse, abort, Api, Resource,request
from flask_cors import *
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config.update(RESTFUL_JSON = dict(ensure_ascii=False))
CORS(app, supports_credentials=True)

api_v1_bp = Blueprint('api_v1', __name__)
kpi_v1_api = Api(api_v1_bp)

class JsonStore():
    def __init__(self, store_file):
        self.store_file = store_file
        self.mem_store = {}

    def load_json(self):
        with open(self.store_file, 'r') as f:
            self.mem_store = json.loads(f.read())

    def save_json(self):
        with open(self.store_file, 'w') as f:
            f.write(json.dumps(self.mem_store, ensure_ascii=False, separators = (',', ':')))

    def get_mem(self):
        return self.mem_store

class KPIDao():
    def __init__(self):
        self.filestore = JsonStore("./store")
        self._load_data()
        self.memstore = self.filestore.get_mem()
 
    def _load_data(self):
        return self.filestore.load_json()

    def _commit(self):
        self.filestore.save_json()

    def is_exists(self, kpi_id):
        if kpi_id not in self.memstore:
            return False
        return True

    def get_item(self, kpi_id):
        return self.memstore[kpi_id]

    def get_all(self):
        return self.memstore

    def put_item(self, kpi_id, kpi_item):        
        self.memstore[kpi_id] = kpi_item
        self._commit()

    def del_item(self, kpi_id):
        del self.memstore[kpi_id]
        self._commit()

class KPIDaoV2():
    def __init__(self):
        self.sys_names = ["mivs", "cdms"]
        self.filestores = {}

        for _sys_name in self.sys_names:
            _filestore = JsonStore("./"+_sys_name+"_storev2")
            self.filestores[_sys_name] = _filestore
            self._load_data(_sys_name)

        self.memstores = {}

        for _sys_name in self.sys_names:
            self.memstores[_sys_name] = self.filestores[_sys_name].get_mem()

    def _load_data(self, sys_name):
        return self.filestores[sys_name].load_json()

    def _commit(self, sys_name):
        try:
            self.filestores[sys_name].save_json()
        except:
            print("_commit error")

    def is_exists(self, sys_name, kpi_id):
        if sys_name not in self.memstores:
            return False
        else:
            if kpi_id not in self.memstores[sys_name]:
                return False
        return True

    def get_item(self, sys_name, kpi_id):
        return self.memstores[sys_name][kpi_id]

    def get_all(self, sys_name):
        return self.memstores[sys_name]

    def put_item(self, sys_name, kpi_id, kpi_item):
        self.memstores[sys_name][kpi_id] = kpi_item
        self._commit(sys_name)

    def del_item(self, sys_name, kpi_id):
        del self.memstores[sys_name][kpi_id]
        self._commit(sys_name)

app.config['kpi_dao'] = KPIDao()
app.config['kpi_dao_v2'] = KPIDaoV2()

class KPIV1(Resource):
    def __init__(self):
        self.dao = app.config['kpi_dao']

    def get(self, kpi_id):
        if not self.dao.is_exists(kpi_id):
            abort(404, message = "KPI {} doesn't exist".format(kpi_id))
        
        kpi_item = self.dao.get_item(kpi_id)
        return kpi_item, 200

    def post(self, kpi_id):
        return self.put(kpi_id)

    def put(self, kpi_id):
        payload = request.get_data()
        kpi_item = json.loads(payload)
        
        self.dao.put_item(kpi_id, kpi_item)
        return kpi_item, 200

    def delete(self, kpi_id):
        if not self.dao.is_exists(kpi_id):
            abort(404, message = "KPI {} doesn't exist".format(kpi_id))

        self.dao.del_item(kpi_id)
        return {'status': 1}, 200

class KPISV1(Resource):
    def __init__(self):
        self.dao = app.config['kpi_dao']

    def get(self):
        return self.dao.get_all()


class KPIV2(Resource):
    def __init__(self):
        self.dao = app.config['kpi_dao_v2']

    def _do_404(self, sys_name, kpi_id):
        if not self.dao.is_exists(sys_name, kpi_id):
            abort(404, message = "KPI {},{} doesn't exist".format(sys_name, kpi_id))

    def get(self, sys_name, kpi_id):
        self._do_404(sys_name, kpi_id)

        kpi_item = self.dao.get_item(sys_name, kpi_id)
        return kpi_item, 200

    def post(self, sys_name, kpi_id):
        return self.put(sys_name, kpi_id)

    def put(self, sys_name, kpi_id):
        payload = request.get_data()
        kpi_item = json.loads(payload)

        self.dao.put_item(sys_name, kpi_id, kpi_item)
        return kpi_item, 200

    def delete(self, sys_name, kpi_id):
        self._do_404(sys_name, kpi_id)

        self.dao.del_item(sys_name, kpi_id)
        return {'status': 1}, 200

class KPISV2(Resource):
    def __init__(self):
        self.dao = app.config['kpi_dao_v2']

    def get(self, sys_name):
        return self.dao.get_all(sys_name)


app.register_blueprint(api_v1_bp, url_prefix = '/service')
#kpi_v1_api.add_resource(KPISV1, '/kpi/kpis',endpoint='kpi_kpis' )
#kpi_v1_api.add_resource(KPISV1, '/mivs/kpis',endpoint='mivs_kpis')
#kpi_v1_api.add_resource(KPISV1, '/cdms/kpis',endpoint='cdms_kpis')
#kpi_v1_api.add_resource(KPIV1, '/kpi/<string:kpi_id>',endpoint='kpi_kpi_id')
#kpi_v1_api.add_resource(KPIV1, '/mivs/<string:kpi_id>',endpoint='mivs_kpi_id')
#kpi_v1_api.add_resource(KPIV1, '/cdms/<string:kpi_id>',endpoint='cdms_kpi_id')

kpi_v1_api.add_resource(KPISV2, '/<string:sys_name>/kpis', endpoint='sys_kpis')
kpi_v1_api.add_resource(KPIV2, '/<string:sys_name>/<string:kpi_id>', endpoint='sys_kpi_id')

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port = 3000)

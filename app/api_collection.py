from flask_restful import Resource
import system_utils.usage as sys_usage

class SystemInfo(Resource):
    def get(self):
        return sys_usage.collect_data()

class VDR_Status(Resource):
    def get(self):
        return {
                'Recordings': [],
                'Timer': [],
                'Status': 'Ready',
                }

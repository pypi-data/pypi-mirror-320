import re
import json
import requests
import datetime
import urllib.parse
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor


class GatewayApi():
    
    def __ErrorHandling(self, status_code):
        if status_code == 200:
            return
        if status_code == 400:
            raise Exception(f"Status Code: 400. Bad Request. Ensure the information you entered is correct")
        if status_code == 401:
            raise Exception(f"Status Code: 401. Unauthorized. " +
                            "You do not hold the correct role permissions to view the dataset requested")
        if status_code == 403:
            raise Exception(f"Status Code: 403. Forbidden. For security reasons, you have been timed out")
        if status_code == 500:
            return 

    def __stringifyTime(self, time):
        string_time = ( f"{time.year}-{time.month:02d}-{time.day:02d}T"
                        f"{time.hour:02d}:{time.minute:02d}:{time.second:02d}.000Z" )
        return string_time
    
    def __requestGet(self, search_term):
        if self.apiKey != None:
            headers = {'Content-type': 'application/json', 'x-api-key': self.apiKey}
            request = requests.get(search_term,headers=headers)
            self.__ErrorHandling(request.status_code)
        else:
            headers = {'Content-type': 'application/json'}
            request = requests.get(search_term,auth=HTTPBasicAuth(self.username,self.password), headers=headers)
            self.__ErrorHandling(request.status_code)
        return request
    
    def __requestPost(self, search_term, payload):
        if self.apiKey != None:
            headers = {'Content-type': 'application/json', 'x-api-key': self.apiKey}
            request = requests.post(search_term, data=json.dumps(payload), headers=headers)
            self.__ErrorHandling(request.status_code)
        else:   
            headers = {'Content-type': 'application/json'}
            request = requests.post(search_term, auth=HTTPBasicAuth(self.username,self.password), 
                                    data=json.dumps(payload), headers=headers)
            self.__ErrorHandling(request.status_code)
        return request
    
    def __requestPut(self, search_term, payload):
        if self.apiKey != None:
            headers = {'Content-type': 'application/json', 'x-api-key': self.apiKey}
            request = requests.put(search_term, data=json.dumps(payload), headers=headers)
            self.__ErrorHandling(request.status_code)
        else:   
            headers = {'Content-type': 'application/json'}
            request = requests.put(search_term, auth=HTTPBasicAuth(self.username,self.password), 
                                    data=json.dumps(payload), headers=headers)
            self.__ErrorHandling(request.status_code)
        return request
    
    def __init__(self, endpoint, username = None, password= None, apiKey = None):
        self.endpoint = endpoint
        self.apiKey = apiKey
        if self.apiKey == None:
            self.username = username
            self.password = password
            request = requests.post(self.endpoint + "/login", 
                                    data={'username': self.username, 'password': self.password})
            self.__ErrorHandling(request.status_code)
            
    def getApiKeys(self):
        search_term = f"{self.endpoint}/apiKeys"
        request = self.__requestGet(search_term)
        return request.json()
    
    def createApiKey(self, name, datasets= None, filesets=None):
        payload = {}
        if name:
            payload["name"] = name
        else:
            raise Exception("Name of API Key must not be Null")
        if datasets != None:
            try:
                parsed_datasets = [dict(zip(('datasetCategory', 'datasetId'), pair)) for pair in datasets]
                payload["datasets"] = parsed_datasets
            except:
                raise Exception("Datasets must be in list form with tuples for category and datasetID. " + 
                                "Ex. [('ousv4-service_manager','ousv4-service_manager_ownship'),('airtracks','airtracks')]")   
        else:
            payload["datasets"] = []                    
        if filesets != None:
            payload["filesetIds"] = filesets
        else:
            payload["filesetIds"] = []
        search_term = f"{self.endpoint}/apiKeys"
        request = self.__requestPost(search_term,payload)
        return request.json()
    
    def updateApiKey(self, name, datasets= None, filesets=None):
        payload = {}
        if name:
            payload["name"] = name
        else:
            raise Exception("Name of API Key must not be Null")
        if datasets != None:
            try:
                parsed_datasets = [dict(zip(('datasetCategory', 'datasetId'), pair)) for pair in datasets]
                payload["datasets"] = parsed_datasets
            except:
                raise Exception("Datasets must be in list form with tuples for category and datasetID. " + 
                                "Ex. [('ousv4-service_manager','ousv4-service_manager_ownship'),('airtracks','airtracks')]")   
        else:
            payload["datasets"] = []                    
        if filesets != None:
            payload["filesetIds"] = filesets
        else:
            payload["filesetIds"] = []
        search_term = f"{self.endpoint}/apiKeys"
        request = self.__requestPut(search_term,payload)
        return request.json()
    
    def deleteApiKey(self, name):
        search_term = f"{self.endpoint}/apiKeys/{name}"
        headers = {'Content-type': 'application/json'}
        apikey_list = []
        for api in self.getApiKeys():
            apikey_list.append(api['name'])
        if name not in apikey_list:
            raise Exception("API Key was not deleted. Please make sure API key exists and try again. " +
                            "If error persists please use our UI to delete your api key")
        request = requests.delete(search_term, auth=HTTPBasicAuth(self.username,self.password), headers=headers)
        return f"Api Key {{{name}}} has been Deleted"

    def listDataSets(self):
        search_term = f"{self.endpoint}/datasets"
        request = self.__requestGet(search_term)
        return request.json()
    
    def mapEnabledDataSets(self):
        search_term = f"{self.endpoint}/datasets"
        request = self.__requestGet(search_term)
        all_records = request.json()
        map_enabled_list = []
        for category in all_records:
            for dataset in category['datasets']:
                if dataset['supportsMapResults'] == True:
                    map_enabled_list.append(dataset)
        return map_enabled_list
        
    def describeDataSet(self, category, datasetID):
        search_term = f"{self.endpoint}/datasets/{category}/{datasetID}/describe"
        request = self.__requestGet(search_term)
        return request.json()
    
    def sampleDataSet(self, category, datasetID, limit=None):
        if limit == None:
            limit = 25
        search_term = f"{self.endpoint}/datasets/{category}/{datasetID}/sample?max={str(limit)}"
        request = self.__requestGet(search_term)    
        return request.json()
    
    def getDataSet(self, category, datasetID, count=True, paging=False, offset=None, limit=None, 
                   startTime=None, endTime=None, polygons=None, filters=None, columns=None):
        
        # Initialize request payload. Set the query limit and offset
        payload = {}
        if count == False and paging == False:
            query_type = 'search'
            payload["paging"] = None
        elif count == True and paging == False:
            query_type = "count"
        elif count == False and paging == True:
            if limit > 1000:
                raise Exception("Limit must be 1000 entries or less.")
            try:
                query_type = "search"
                payload["paging"] = {"offset":int(offset),"max":int(limit)}
            except:
                raise Exception("Integer values must be given for offset and limit when querying for Data.")
            
        # Check to see if Query Parms are set
        if polygons == None and (startTime == None and endTime == None) and filters == None:
            raise Exception("Must pass at least startTime and endtime, polygons or filters")

        # Handle Temporal Queries
        if (startTime == None and endTime == None):
            time_range = None
            payload["timeRange"] = time_range
        elif (startTime != None and endTime != None):
            try: 
                start = self.__stringifyTime(startTime)
                end = self.__stringifyTime(endTime)
                time_range = {"start": start, "end":end}
                payload["timeRange"] = time_range
            except:
                 raise Exception("Invalid Date format. Must be a DateTime Object")

        # Handle Geospacial Queries
        if (polygons == None):
            poly_string = None
            payload["geospatial"] = poly_string
        elif (polygons != None):
            try:
                poly_string = str(polygons[0][0]) + " "+ str(polygons[0][1]) 
                for coord in polygons[1:]:
                    poly_string = poly_string + "," + str(coord[0]) + " " + str(coord[1])
                poly_string = "(" + poly_string + ")"
                payload["geospatial"] = {}
                payload["geospatial"]["polygons"] = poly_string
                payload["geospatial"]["antimeridianPolygons"] = False 
            except:
                raise Exception("polygons must be in a list format of [(lon1,lat1),(lon2,lat2), ... , (lonN,latN)]")
        
        #Handle Query Filters
        if (filters == None):
            payload["filters"] = []
        elif (filters != None):
            try:
                payload["filters"] = []
                for f in filters:
                    f_temp = {"name":f[0],"value":f[1],"operator":f[2], "type":f[3]}
                    payload["filters"].append(f_temp)
            except:
                payload["filters"] = []
                for f in filters:
                    f_temp = {"name":f[0],"value":f[1],"operator":f[2]}
                    payload["filters"].append(f_temp)
        else:
            raise Exception(f'Filters must be in form [("name","search value", "operator","type")]. ' +
                            'Check to make sure all parameters are correct')
        if columns:
            if all(isinstance(elem,str) for elem in columns):                
                payload["columns"] = columns
            else:
                raise Exception('Columns must be a list of strings in format ["string1","string2",...]')
                           
        #Send Query
        search_term = f"{self.endpoint}/datasets/{category}/{datasetID}/{query_type}"
        request = self.__requestPost(search_term,payload)
        return request.json()
    
    def listFileSets(self, path = None, recursive = None):
        if path == None:
            search_term = f"{self.endpoint}/filesets"
        elif "/" in path:
            dir_list = path.split("/",1)
            search_term = f"{self.endpoint}/filesets/{dir_list[0]}/list?listPrefix={dir_list[1]}%2F"
        else:
            if recursive == True:
                search_term = f"{self.endpoint}/filesets/{path}/list?recursive=true"
            else:
                search_term = f"{self.endpoint}/filesets/{path}/list"
        request = self.__requestGet(search_term)
        return request.json()
    
    def getFileSets(self, filesetId, path):
        if type(path) == str:
            search_term = f"{self.endpoint}/filesets/{filesetId}/download?file={path}"
            with self.__requestGet(search_term) as request:
                filename = path.rsplit("/", 1)[-1]
                with open(filename, 'wb') as f:
                    for chunk in request.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Download Finished")
                
        elif type(path) == list:
            for each in path:
                search_term = f"{self.endpoint}/filesets/{filesetId}/download?file={each}"
                with self.__requestGet(search_term) as request:
                    filename = each.rsplit("/", 1)[-1]
                    with open(filename, 'wb') as f:
                        for chunk in request.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("Download Finished")
                        
    def getMultifile(self, filesetId, filelist):
        n_threads = 5
        with ThreadPoolExecutor(n_threads) as executor:
            try:
                _ = {executor.submit(self.getFileSets, filesetId, file) for file in filelist}
            except:
                self.getFileSets(filesetId, filelist)
@csrf_exempt
def tokenrequest(request):
    tokenissue = GetToken(request)
    #print tokenissue.token
    responses = tokenissue.check_data_json_post()
    #import pdb; pdb.set_trace()
    return HttpResponse(responses)




class GetToken:
    #token = ""
    def __init__(self,json_data_post):
        self.json_data_post = json_data_post
        print "calling the class"
    def check_data_json_post(self):
        """ Get the user input from HTTP response/
            Input data from HTTP response
            Check the json string
            call up the keystone version check function """
        try:
            self.json_data = json.loads(self.json_data_post.read())
            #print self.json_data
        except ValueError:
            self.resp = "Request body missing, No JSON object could be decoded"
            return HttpResponse(self.resp)
        try:
            self.tokenRequest = urllib2.Request(self.json_data['keystoneEP'])
        except KeyError:
            self.resp = "Invalid json-key string, expecting keystoneEP as json-key"
            return HttpResponse(self.resp)
        self.tokenRequest.add_header("Content-type", "application/json")
        return(self.check_os_version(self.json_data))

    def read_json_v2(self,file_name):
        """Reads the user credentials from the database
            Applies for keystone version 2 """

        print "calling read json"
        self.file_name = file_name
        print "calling read"
        with open(self.file_name) as self.jsonfile:
            self.data = json.loads(self.jsonfile.read())
        self.creds_data = {}
        self.creds_data['os_tenant_name'] =  self.data['auth']['tenantName']
        self.creds_data['os_name'] = self.data['auth']['passwordCredentials']['username']
        self.creds_data['os_password'] = self.data['auth']['passwordCredentials']['password']
        #print self.creds_data
        return(self.creds_data)


    def read_json_v3(self,file_name):
        """Reads the user credentials from the database
            Applies for keystone version 3 """

        self.file_name = file_name
        with open(self.file_name) as self.jsonfile:
            self.data = json.loads(self.jsonfile.read())
        #print data
        self.creds_data = {}
        self.creds_data['os_name'] = self.data['auth']['identity']['password']['user']['name']
        self.creds_data['os_domain'] =  self.data['auth']['identity']['password']['user']['domain']['id']
        self.creds_data['os_password'] =  self.data['auth']['identity']['password']['user']['password']
        self.creds_data['os_project_id'] = self.data['auth']['scope']['project']['id']
        return(self.creds_data)

    def check_os_version(self,json_data):
        """checks the openstack API version supplied by user.
            Read the appropirate credentials file
            Fire up the API request to keystone endpoint
            Generates the token """
        print "calling check os version"
        self.json_data = json_data
        if "v2" in self.json_data['keystoneEP']:
            #print "this is v2 version"
            self.os_creds_data = self.read_json_v2('/home/stack/iManage-Installer/iManage/app_deployment/jsons/v2.json')
            self.jsonPayload = json.dumps({'auth' : {'tenantName' : self.os_creds_data['os_tenant_name'], 'passwordCredentials' : {'username' : self.os_creds_data['os_name'], 'password' : self.os_creds_data['os_password']}}})
            #print self.jsonPayload
            try:
                self.request = urllib2.urlopen(self.tokenRequest, self.jsonPayload)
                self.json_data = json.loads(self.request.read())
                self.request.read()
                self.request.close()
                self.resp = json.dumps(self.json_data)
                #print self.resp
            except (ValueError,urllib2.URLError) as e:
                #self.resp = "Invalid url param"
                self.resp = e
                print self.resp
            print "reached"
            GetToken.token = self.resp
            self.decode_token_v2(self.resp)
            #self.get_endpoint_v2()
            return (self.decode_token_v2(self.resp))

        elif "v3" in self.json_data['keystoneEP']:
            self.os_creds_data = self.read_json_v3('/home/stack/iManage-Installer/iManage/app_deployment/jsons/file1-home.json')
            self.jsonPayload = json.dumps({"auth": {"identity": {"methods": ["password"],"password": {"user": {"name": self.os_creds_data['os_name'],"domain":
            {"id": self.os_creds_data['os_domain']},"password": self.os_creds_data['os_password']}}},"scope": {"project": {"id": self.os_creds_data['os_project_id']}}}})
        try:
            self.request = urllib2.urlopen(self.tokenRequest, self.jsonPayload)
            self.json_data = json.loads(self.request.read())
            self.request.read()
            self.request.close()
            self.resp = self.request.info()
            print self.resp
            self.token = self.resp.dict['x-subject-token']
            GetToken.token = self.token
            print "Openstack Token = "+self.token
            self.get_endpoint_v3_special()
            return HttpResponse(self.token)
        except urllib2.URLError as e:
            self.resp = e.reason
            return HttpResponse(self.resp)

        else:
            self.resp = "Invalid OS version"
            return HttpResponse(self.resp)

    def decode_token_v2(self,jsons):
        """ Decodes the V2 token from the token issue strings"""
        self.jsons = jsons
        self.data = json.loads(self.jsons)
        print "Openstack Token generated = "+self.data['access']['token']['id']
        return self.data['access']['token']['id']

    def get_endpoint_v2(self):
        """ Gets the endpoints for v2 version.
            Reads the authenticated token"""
        print"calling get endpoint"
        self.json_data = GetToken.token
        print self.json_data
        self.endpoint_data_dict = {}
        try:
            self.user_id = self.json_data['access']['user']['id']
        except TypeError as e:
            print "exception caught"
            self.get_endpoint_v3()
        print "#"*20
        print "Openstack User-Id = "+self.user_id
        for self.item in self.json_data['access']['serviceCatalog']:
            self.endpoint_data_dict[item['name']] = item['endpoints'][0]['adminURL']
        self.endpoint_data_json = json.dumps(endpoint_data_dict)
        return self.endpoint_data_json

    def get_endpoint_v3(self):
        self.json_data = GetToken.token
        json_data = json.loads(self.json_data)
        #print json_data
        #print json_data['access']['serviceCatalog']
        #import pdb;pdb.set_trace()
        self.endpoint_data_dict = {}
        for item in self.json_data['access']['serviceCatalog']:
        #for item in self.json_data['token']['catalog']:
            #self.endpoint_data_dict[item['type']] = item['endpoints'][2]['url']
            print item
        print "~~"*20
        print "Openstack User-ID = "+json_data['token']['roles'][0]['id']
        self.endpoint_data_json = json.dumps(self.endpoint_data_dict)
        return self.endpoint_data_json

    def get_endpoint_v3_special(self):
        #self.json_data = GetToken.token
        self.url = "http://192.168.72.130:35357/v3/endpoints"
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': GetToken.token}
        print self.url
        print self.headers
        print "#####"
        #print heatdata1
        self.response = requests.post(self.url, headers=self.headers)
        self.response = self.response.json()
        print self.response
        self.endpoint_data_dict = {}
        for item in self.json_data['access']['serviceCatalog']:
        #for item in self.json_data['token']['catalog']:
            #self.endpoint_data_dict[item['type']] = item['endpoints'][2]['url']
            print item
        print "~~"*20
        print "Openstack User-ID = "+json_data['token']['roles'][0]['id']
        self.endpoint_data_json = json.dumps(self.endpoint_data_dict)
        return self.endpoint_data_json






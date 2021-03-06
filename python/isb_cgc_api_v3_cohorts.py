# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

'''
Copyright 2018, Institute for Systems Biology.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

from argparse import ArgumentParser
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.file import Storage

import httplib2
import json
import os
import pprint
import sys

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# the CLIENT_ID for the ISB-CGC site
CLIENT_ID = '907668440978-0ol0griu70qkeb6k3gnn2vipfa5mgl60.apps.googleusercontent.com'
# The google-specified 'installed application' OAuth pattern
CLIENT_SECRET = 'To_WJH7-1V-TofhNGcEqmEYi'
# The google defined scope for authorization
EMAIL_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
# where a default credentials file will be stored for use by the endpoints
DEFAULT_STORAGE_FILE = os.path.join(os.path.expanduser("~"), '.isb_credentials')

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# validate the credentials of the current user against the ISB-CGC site

def get_credentials():
    oauth_flow_args = ['--noauth_local_webserver']
    storage = Storage(DEFAULT_STORAGE_FILE)
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, EMAIL_SCOPE)
        flow.auth_uri = flow.auth_uri.rstrip('/') + '?approval_prompt=force'
        credentials = tools.run_flow(flow, storage, tools.argparser.parse_args(oauth_flow_args))
    return credentials

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def get_authorized_service(api_tag):
    api = 'isb_cgc{}_api'.format(api_tag)
    version = 'v3'
    site = "https://api-dot-isb-cgc.appspot.com"
    discovery_url = '%s/_ah/api/discovery/v1/apis/%s/%s/rest' % (site, api, version)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    if credentials.access_token_expired or credentials.invalid:
        credentials.refresh(http)

    authorized_service = build(api, version, discoveryServiceUrl=discovery_url, http=http)

    return authorized_service

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# resource methods
# the following four APIs can be cross-program and are part of the isb_cgc_api endpoint

def get(service, cohort_id=None, body=None, name=None):
    """
    Usage: python isb_cgc_api_v3_cohorts.py -e get -c 24
    """
    data = service.cohorts().get(cohort_id=cohort_id).execute()
    print '\nresults from cohorts().get()'
    pprint.pprint(data)

def list(service, cohort_id=None, body=None, name=None):
    """
    Usage: python isb_cgc_api_v3_cohorts.py -e list
    """
    data = service.cohorts().list().execute()
    print '\nresults from cohorts().list()'
    pprint.pprint(data)
    
    return data

def delete(service, cohort_id=None, body=None, name=None):
    """
    Usage: python isb_cgc_api_v3_cohorts.py -e delete -c 24
    """
    data = service.cohorts().delete(cohort_id=cohort_id).execute()
    print '\nresults from cohorts().delete()'
    pprint.pprint(data)

def cloud_storage_file_paths(service, cohort_id, body=None, name=None):

    """
    Usage: python isb_cgc_api_v3_cohorts.py -e cloud_storage_file_paths -c 24
    """

    data = service.cohorts().cloud_storage_file_paths(cohort_id=cohort_id).execute()
    print '\nresults from cohorts().cloud_storage_file_paths()'
    pprint.pprint(data)
    
    return data

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# the following two APIs are specific to a program endpoint -- the examples
# here use the TCGA-specific endpoint, but are also available within the
# TARGET- and CCLE-specific APIs

def preview(service, cohort_id=None, body=None, name=None):
    """
    Usage: python isb_cgc_api_v3_cohorts.py -e preview -b '{"project_short_name": ["TCGA-BRCA", "TCGA-UCS"], "age_at_diagnosis_gte": 90}'
    """
    data = service.cohorts().preview(**body).execute()
    print '\nresults from cohorts().preview()'
    pprint.pprint(data['sample_count'])

def create(service, cohort_id=None, body=None, name=None):
    """
    Usage: python isb_cgc_api_v3_cohorts.py -e create -n mycohortname -b '{"project_short_name": ["TCGA-BRCA", "TCGA-UCS"], "age_at_diagnosis_gte": 90}'
    """
    data = service.cohorts().create(name=name, body=body).execute()
    print '\nresults from cohorts().create()'
    pprint.pprint(data)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def print_usage():
    print " "
    print " Usage: python %s --endpoint <endpoint_name> ... " % sys.argv[0]
    print " "
    print " Examples: "
    print "     python %s --endpoint list " % sys.argv[0]
    print "     python %s --endpoint get --cohort <cohort_id> " % sys.argv[0]
    print "     python %s --endpoint delete --cohort <cohort_id> " % sys.argv[0]
    print "     python %s --endpoint cloud_storage_file_paths --cohort <cohort_id> " % sys.argv[0]
    bodyString = '{"project_short_name": ["TCGA-BRCA", "TCGA-UCS"], "age_at_diagnosis_gte": 90}'
    ## print "     python %s --endpoint preview --body '%s' " % ( sys.argv[0], bodyString )
    ## print "     python %s --endpoint create --name myNewCohort --body '%s' " % ( sys.argv[0], bodyString )
    print " "

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def main():
    parser = ArgumentParser()
    parser.add_argument('--endpoint', '-e',
                        help='Name of cohorts endpoint to execute. '
                             'Options: get, list, preview, create, delete, cloud_storage_file_paths')
    parser.add_argument('--cohort_id', '-c',
                        help='Id of cohort to use in get, delete, or cloud_storage_file_paths')
    parser.add_argument('--body', '-b',
                        help='Payload to use in preview or create endpoints. Example: '
                             '{"project_short_name": ["TCGA-BRCA", "TCGA-UCS"], "age_at_diagnosis_gte": 90')
    parser.add_argument('--name', '-n',
                        help='The name of the cohort to create in the create endpoint.')
    try:
        args = parser.parse_args()
    except:
        print_usage()
        return

    if args.endpoint not in ['get', 'list', 'preview', 'create', 'delete', 'cloud_storage_file_paths']:
        print_usage()
        return

    if args.endpoint not in ['list', 'preview', 'create']:
        if ( args.cohort_id is None ):
            print " "
            print " an integer cohort identifier is required for this endpoint "
            print " "
            print_usage()
            return

    if args.endpoint in ['preview', 'create']:
        print " "
        print " Cohort preview and create functionality is not currently available from the ISB-CGC APIs. "
        print " "
        return
        if ( args.body is None ):
            print " "
            print " at least one filter must be specified using the 'body' argument "
            print " in order to %s a cohort " % args.endpoint
            print " "
            print_usage()
            return

    api_tag = '_tcga' if args.endpoint in ('preview', 'create') else '' 
    service = get_authorized_service(api_tag)
    cohort_id = args.cohort_id if args.cohort_id is None else int(args.cohort_id)
    body = json.loads(args.body) if args.body is not None else args.body

    globals()[args.endpoint](service, cohort_id=cohort_id, body=body, name=args.name)

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == '__main__':
    main()

# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

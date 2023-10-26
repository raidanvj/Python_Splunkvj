import splunklib.client as client
import json
import splunklib.results as results
from collections import OrderedDict

## This Function is used to connect to the Splunk Site with Application Name and sharing level of Saved search mentioned
def connect_to_splunk(app,sharing):
    # Below is the User autorization parameters for the connection
    username = 'admin'
    password = 'changeme'
    host = 'localhost'
    port = '8089'

    try:
        service = client.connect(username=username,password=password,host=host,port=port,owner=None,app=app,sharing=sharing)
        if service:
            print("Splunk service created successfully")
            # print(service)
    except Exception as e:
        print(e)
    return service



# def savedsearch_list(splunk_service):
#     try:
#         savedsearches= None
#
#         if splunk_service:
#             savedsearches = splunk_service.saved_searches
#             print(splunk_service.saved_searches)
#         print("-----------------------------------")
#     except Exception as e:
#         print(e)
#     return savedsearches

# def create_savedsearch(savedsearch_collection,name,search,payload={}):
#     try:
#         if savedsearch_collection:
#             mysearch = savedsearch_collection.create(name,search,**payload)
#             if mysearch:
#                 print("{} object created successfully".format(mysearch.name))
#                 print("-----------------------------------")
#     except Exception as e:
#         print(e)


def update_owner_list_savedsearch(new_owner,lookup_contents):
    print("\nupdate_owner_list_savedsearch is called")
    saved_searches_to_update = list(lookup_contents)  # Replace with your saved search names
    print(saved_searches_to_update)
    # Initialize a list to store the names of saved searches that were updated
    updated_saved_searches = []
    for saved_search_name in saved_searches_to_update:
        ss_app = saved_search_name.split("##")
        saved_search = ss_app[0]
        app1 = ss_app[1]
        # app specific connect
        splunk_service = connect_to_splunk(app = app1,sharing= "app")

        # Get the saved search
        saved_search_o = splunk_service.saved_searches[saved_search]
        print(saved_search)
        try:
            if saved_search_o:
                # Change the owner of the saved search
                owner_change = saved_search_o.acl_update(sharing="app", owner=new_owner)
                # saved_search.update(owner=new_owner)
                updated_saved_searches.append(saved_search)
                print(f"Updated owner of '{saved_search}' to '{new_owner}'")

        except Exception as e:
            print(f"Failed to update owner of '{saved_search}': {str(e)}")

#Can be used for individual Saved search Owner Update
# def owner_update(splunk_service,new_owner,s_name):
#     try:
#         print("till here")
#         if splunk_service:
#             print("till here")
#             saved_search = splunk_service.saved_searches[s_name]
#
#             print("till here")
#             print(saved_search.name)
#             owner_change = saved_search.acl_update(sharing="app", owner=new_owner)
#             if owner_change:
#                 print("The Owner has successfully been updated")
#                 print("-----------------------------------")
#     except Exception as e:
#         print(e)


''' This Section is used to get the list of the Alerts and Apps concatenated values 
    from the Lookup which containes the required set of alerts and reports.
    Further it returns a list of those values in required format
'''
def get_lookup_contents(lookup_name, splunk_service):

    try:
        # Perform a search to retrieve the lookup contents
        search_query = f"| inputlookup {lookup_name}"
        job = splunk_service.jobs.create(search_query)
        while not job.is_done():
            sleep(.2)
        rr = results.ResultsReader(job.results())
        lookup_contents = []
        for result in rr:
            if isinstance(result, results.Message):
                # Diagnostic messages may be returned in the results
                print(result.type+" : "+ result.message)
            elif isinstance(result, dict):
                # Normal events are returned as dicts
                print(result)
                lookup_contents.append(result)
        List_of_alerts = [item['new_title'] for item in lookup_contents]
        #print("Nothing")
        print(List_of_alerts)
        assert rr.is_preview == False
        return List_of_alerts
    except Exception as e:
        print(e)


def main():
    try:
        splunk_service = connect_to_splunk(app="search",sharing="app")
        if splunk_service:
            new_owner="hilda"
            #s_name="Sample_table"
            #owner_update(splunk_service,new_owner,s_name)
            lookup_name = "alert_list.csv"  ###The Lookup of the the Splunk Savedsearch list
            lookup_contents = get_lookup_contents(lookup_name, splunk_service)
            if lookup_contents:
                update_owner_list_savedsearch(new_owner,lookup_contents)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

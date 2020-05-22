import numpy as np 
import requests
import argparse

def delete_project(token, name):
    """
    Deletes a SonarQube-project at topfit2.informatik.uni-osnabrueck.de:9000
    """
    base_url = "http://topfit2.informatik.uos.de:9000/api/"
    delete_project = "projects/delete"

    params = {"project":name}

    response = requests.post(base_url+delete_project, auth=(token, ''), data=params)

    if response.status_code == 204 :
        print("Project ",name," was deleted.")
    else : 
        print("Failed with status: ", response.status_code)
        print(response.reason)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("token")
    parser.add_argument("name")
    args = parser.parse_args()
    delete_project(args.token, args.name)
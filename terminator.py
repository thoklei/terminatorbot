import requests
import argparse
import re

def main(sq_url, sq_token, gl_token, gl_project_id, gl_name):
    """
    Delete all SonarQube-projects at topfit2.informatik.uni-osnabrueck.de:9000 that correspond
    to non-existing MergeRequests of this gitlab-project

    sq_token = the sonarqube-access-token
    project_id = the id of the gitlab project
    gl_token = the GitLab-access-token
    """

    # URLs
    sq_base_url = sq_url+"api/"
    sq_delete_project = "projects/delete"
    sq_show_projects = "projects/search"

    gl_base_url = "https://gitko.informatik.uni-osnabrueck.de/api/v4/"
    gl_open_mrs = "projects/{}/merge_requests?state=opened".format(gl_project_id)


    # get currently active merge requests of this project
    mrs_response = requests.get(gl_base_url+gl_open_mrs, headers = {"PRIVATE-TOKEN":gl_token})
    mrs = [mr['iid'] for mr in mrs_response.json()]
    print("Active Merge Requests: ", mrs)

    # get currently existing SQ-projects for this gitlab project
    sqprojects_response = requests.post(sq_base_url+sq_show_projects, auth=(sq_token, ''))
    sq_projects = [project['key'] for project in sqprojects_response.json()['components']]
    print("Active SonarQube Projects: ", sq_projects)

    # only look at MR-projects of this gitlab-project - we always want to keep dev- and master-projects
    pattern = re.compile(gl_name+"-[0-9]+") 
    sq_projects = [ project for project in sq_projects if pattern.match(project) ]
    print("Active SonarQube Projects of our project: ",sq_projects)

    # remove all open Merge Requests from the list of SonarQube-projects,
    # keeping only a list of SQ-projects to be removed
    target_projects = []
    for project in sq_projects:
        for merge in mrs :
            if project.endswith("-"+str(merge)):
                break
        else : # never broke out of for-loop, python is cool
            target_projects.append(project)
    print("Active SonarQube Projects of dead MRs: ", target_projects)

    def delete_project(name) :
        params = {"project":name}
        response = requests.post(sq_base_url+sq_delete_project, auth=(sq_token, ''), data=params)

        if response.status_code == 204 :
            print("Project ",name," was deleted.")
        else : 
            print("Failed with status: ", response.status_code)
            print(response.reason)

    # deleting all target projects
    for project in target_projects:
        delete_project(project)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("sq_url")   # SonarQube-Host-URL (taken from local variable)
    parser.add_argument("sq_token") # SonarQube-Token (taken from GL project variable)
    parser.add_argument("gl_token") # Gitab authentification-Token (taken from GL Project Variable)
    parser.add_argument("gl_project_id") #ID of the gitlab project (taken form CI-env-variable)
    parser.add_argument("gl_name") #IID (= readable name) of the gitlab project (taken from CI-env-variable)
    args = parser.parse_args()

    main(args.sq_url, args.sq_token, args.gl_token, args.gl_project_id, args.gl_name)
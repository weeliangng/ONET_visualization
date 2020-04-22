import yaml
import requests
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go

from occupation_details import *


with open("config.yml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

userId = config["config"]["userid"]
api_key = "Bearer "+ config["config"]["api"]

# OccupationSkillsGapList
# OccupationSkillsMatchList
# CurrentOccupationTitle
# TargetOccupationTitle
# CurrentOccupationCode
# TargetOccupationCode
# CurrentOccupationWage
# TargetOccupationWage
# CurrentEducationTitle
# TargetEducationTitle
# CurrentExperienceTitle
# TargetExperienceTitle
# CurrentTrainingTitle
# TargetTrainingTitle
# CurrentLicenses
# TargetLicenses
# CurrentCertificates
# TargetCertificates
# LocationState

def remove_dash_dot(onetcode):
    return onetcode.replace(".","").replace("-","")
def remove_comma_plus_dollar(salary):
    return float(salary.replace(",","").replace("+","").replace("$",""))




def get_skillsgap_json(OnetCodeSource, OnetCodeTarget, userId, api_key):
    request_url = "https://api.careeronestop.org/v1/skillgap/{userId}/{OnetCodeSource}/{OnetCodeTarget}/United%20States/25".format(userId = userId, 
                                                                                                                                    OnetCodeSource = OnetCodeSource, 
                                                                                                                                    OnetCodeTarget= OnetCodeTarget )
    response  = requests.get(request_url, headers = {"Authorization": api_key})
    print(response.status_code)
    return response.json()

skills_gap = get_skillsgap_json(41303103, 41309901, userId, api_key)

def salary_graph(skills_gap):

    text = [skills_gap["CurrentOccupationWage"], skills_gap["TargetOccupationWage"]]
    x = ["Current", "Target"]
    y = list(map(remove_comma_plus_dollar, text))
    fig = go.Figure(data=[go.Bar(
            x=x, y=y,
            text=text,
            textposition='auto',
        )])

    return dcc.Graph(figure=fig)

def similarity_tab_details(skills_gap):
    similarity_list = skills_gap["OccupationSkillsMatchList"]
    details = []
    if similarity_list is None :
        details.append(html.P(html.Em("No data available")))
        return details

    for similarity in similarity_list:
        details.append(html.P(children = 
                                    [
                                    html.Strong(similarity["Title"]),
                                    html.Br(),
                                    similarity["Description"]
                                    ]))
    return details

def differences_tab_details(skills_gap):
    differences_list = skills_gap["OccupationSkillsGapList"]
    details = []
    if differences_list is None :
        details.append(html.P(html.Em("No data available")))
        return details

    if differences_list is None : return details
    for difference in differences_list:
        details.append(html.P(children = 
                                    [
                                    html.Strong(difference["Title"]),
                                    html.Br(),
                                    difference["Description"]
                                    ]))
    return details

def skillsgap_details_tabs(OnetCodeSource, OnetCodeTarget):
    OnetCodeSource = remove_dash_dot(OnetCodeSource)
    OnetCodeTarget = remove_dash_dot(OnetCodeTarget)

    skills_gap = get_skillsgap_json(OnetCodeSource, OnetCodeTarget, userId, api_key)
    
    print(skills_gap)

    tabs = dbc.Tabs([
                        dbc.Tab(label = "Salary",
                                children = [salary_graph(skills_gap)]
                            ),
                        dbc.Tab(label = "Similarity",
                                children = similarity_tab_details(skills_gap)
                                ),
                        dbc.Tab(label = "Gaps",
                                children = differences_tab_details(skills_gap)
                                ),
                        dbc.Tab(label = "Typical Level Of Training")



    ])

    return tabs

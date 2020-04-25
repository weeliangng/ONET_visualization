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
    if salary == "Not Available": return 1000
    else:
        return float(salary.replace(",","").replace("+","").replace("$",""))




def get_skillsgap_json(OnetCodeSource, OnetCodeTarget, userId, api_key):
    request_url = "https://api.careeronestop.org/v1/skillgap/{userId}/{OnetCodeSource}/{OnetCodeTarget}/United%20States/25".format(userId = userId, 
                                                                                                                                    OnetCodeSource = OnetCodeSource, 
                                                                                                                                    OnetCodeTarget= OnetCodeTarget )
    response  = requests.get(request_url, headers = {"Authorization": api_key})
    print(response.status_code)
    return response.json()


def salary_graph(skills_gap):

    text = [skills_gap["CurrentOccupationWage"], skills_gap["TargetOccupationWage"]]

    x = ["Current", "Target"]
    y = list(map(remove_comma_plus_dollar, text))
    fig = go.Figure(data=[go.Bar(
            x=x, y=y,
            text=text,
            textposition='auto',
        )])
    details = html.Div(children = [
                    html.Strong("Salary Data from the United States - in US Dollars"),
                    dcc.Graph(figure=fig)
                ])

    return details

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

def get_skills_knowledge_level(onetsoc_code, element_id):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_skills_knowledge_level_sql = """select data_value from (
                                                                    select  * from knowledge
                                                                    union
                                                                    select * from skills ) as skills_knowledge

                                                                    where skills_knowledge.scale_id = 'LV'
                                                                    and onetsoc_code = '{}'
                                                                    and element_id = '{}'
                                                                    ;""".format(onetsoc_code, element_id)
    c = conn.cursor()
    skills_knowledge_level = list()
    for row in c.execute(onetsoc_skills_knowledge_level_sql):
        #print(row)
        skills_knowledge_level.append(row[0])
    return skills_knowledge_level

def difference_graph(OnetCodeSource, OnetCodeTarget, element_id):
    source_level = float(get_skills_knowledge_level(OnetCodeSource, element_id)[0])
    target_level = float(get_skills_knowledge_level(OnetCodeTarget, element_id)[0])
    x = ["Current", "Target"]
    y = [source_level, target_level]
    fig = go.Figure(
                    data=[go.Bar(
                                x=x, y=y,
                                textposition='auto'
                                )
                                ])
    fig.update_layout(
        yaxis =dict(range=[0,7]),
        margin = dict(t=0,
                    b=5)
    )
    return dcc.Graph(figure=fig)

def differences_tab_details(skills_gap, OnetCodeSource, OnetCodeTarget):
    differences_list = skills_gap["OccupationSkillsGapList"]
    details = []
    if differences_list is None :
        details.append(html.P(html.Em("No data available")))
        return details

    for difference in differences_list:
        details.append(html.P(children = 
                                    [
                                    html.Strong(difference["Title"]),
                                    html.Br(),
                                    difference["Description"]
                                    ]
                                    ))
        details.append(difference_graph(OnetCodeSource, OnetCodeTarget, difference["SkillId"]))
    return details

def training_tab_details(skills_gap,  OnetCodeSource, OnetCodeTarget):
    details =[]
    details.append(html.P(children = 
                                [
                                html.Strong("Typical Education Title of {}".format(skills_gap["CurrentOccupationTitle"])),
                                html.Br(),
                                skills_gap["CurrentEducationTitle"],
                                html.Br(),
                                html.Strong("Typical Education Title of {}".format(skills_gap["TargetOccupationTitle"])),
                                html.Br(),
                                skills_gap["TargetEducationTitle"]
                                ]
                                ))
    return details

def skillsgap_details_tabs():

    
    tabs = html.Div([
            dbc.Tabs(id = "skillsgap_details_tabs",
                    children = [
                        dbc.Tab(label = "Salary",
                            ),
                        dbc.Tab(label = "Similarity",
                                ),
                        dbc.Tab(label = "Gaps",
                                ),
                        dbc.Tab(label = "Typical Level Of Training")

            ]),
            dbc.Spinner(html.Div(id = "skillsgap_details_content"))
    ]
    )

    return tabs

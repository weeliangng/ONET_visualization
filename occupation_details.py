import sqlite3
import dash_core_components as dcc
import dash_html_components as html
from network_logic import get_occupation_onetsocCode_dict
import dash_bootstrap_components as dbc

from network_logic import get_occupation_onetsocCode_list

def get_occupation_description(onetsoc_code):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_description_sql = "select * from occupation_data where onetsoc_code ='{}';".format(onetsoc_code)
    c = conn.cursor()

    for row in c.execute(onetsoc_occupation_description_sql):
        description = row[2]
    return description

def get_occupation_education(onetsoc_code):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_education_sql = """select category_description, data_value from education_training_experience
                                            inner join content_model_reference on education_training_experience.element_id = content_model_reference.element_id
                                            inner join scales_reference on education_training_experience.scale_id = scales_reference.scale_id
                                            inner join ete_categories on ete_categories.element_id = education_training_experience.element_id and ete_categories.category = education_training_experience.category
                                            where education_training_experience.scale_id = 'RL'
                                            and data_value>0 
                                            and onetsoc_code = '{}'
                                            order by data_value desc;""".format(onetsoc_code)
    c = conn.cursor()
    occupation_education = list()
    for row in c.execute(onetsoc_occupation_education_sql):
        #print(row)
        occupation_education.append(row)
    return occupation_education

def occupation_content(onetsoc_code):
    return html.Ul(children = [html.Li("{} - {} % of respondents".format(education[0],education[1]) ) for education in get_occupation_education(onetsoc_code)])

def get_occupation_tasks(onetsoc_code):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_tasks_sql = """select task, task_type from task_statements
                                        inner join task_ratings on task_statements.task_id = task_ratings.task_id
                                        inner join scales_reference on task_ratings.scale_id = scales_reference.scale_id
                                        where task_statements.onetsoc_code = '{}'
                                        and task_ratings.scale_id ='RT'
                                        order by data_value desc;""".format(onetsoc_code)
    c = conn.cursor()
    occupation_tasks = list()
    for row in c.execute(onetsoc_occupation_tasks_sql):
        #print(row)
        occupation_tasks.append(row)
    return occupation_tasks

def occupation_tasks_content(onetsoc_code):    
    return html.Ul(children = [html.Li(task[0] + " - "+task[1]) for task in get_occupation_tasks(onetsoc_code)])

def get_top5_work_activities(onetsoc_code):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_work_activities_sql = """select element_name, description from work_activities
                                        inner join content_model_reference on work_activities.element_id = content_model_reference.element_id
                                        where onetsoc_code = '{}'
                                        and scale_id = 'IM'
                                        order by data_value desc
                                        limit 5;""".format(onetsoc_code)
    c = conn.cursor()
    occupation_work_activities = list()
    for row in c.execute(onetsoc_work_activities_sql):
        #print(row)
        occupation_work_activities.append(row)
    return occupation_work_activities

def occupation_activities_content(onetsoc_code):    
    return html.Ul(children = [html.Li(activity[0] + " - " + activity[1]) for activity in get_top5_work_activities(onetsoc_code)])

def remove_dash_dot(onetcode):
    return onetcode.replace(".","").replace("-","")

def dropdown_occupations(exclude=[]):
    options = []
    for onet_occ in get_occupation_onetsocCode_list():
        for onet,occ in onet_occ.items():
            options.append({"label" : occ, "value": remove_dash_dot(onet)})
    return options

def default_sidebar():
    tabs = dbc.Tabs(id = "default_sidebar_tabs",
                    children = [
                    dbc.Tab(label = "Welcome", className = "mx-3",
                            children = [
                                
                                html.P(children = ["""This visualization was developed to help job seekers identify other occupations similar to their existing occupation.
                                Every occupation has 10 other occupations that have been identified to be closely related by ONET. The lower the relatedness ranking, the more closely
                                related the occupation is."""]),
                                html.H5(children = ["How to use"]),
                                dcc.Markdown("""
                                **To add an outward occupation graph:**
                                * Select the occupation in the dropdown
                                * Choose the relatedness filter range (lower the ranking, the more closely related)
                                  * Please use a lower distance when a larger relatedness filter range is set in order to reduce the number of occupations added
                                * Choose the distance from the selected occupation
                                  * Distance > 1 will further add other occupations that are not directly related to the selected occupation
                                  * Please use a smaller relatedness filter range when a larger distance is set in order to reduce the number of occupations added
                                
                                **To add occupations pointing to a selected occupation:**
                                * Select the occupation in the graph
                                * Select the relatedness filter range
                                  * Note that not all occupations have occupations within the selected relatedness range pointing towards it. In that case no occupation will be added.
                                * Click on "Add" Button
                                """),
                                html.Hr(),
                                html.Div(children=[
                                    html.P(style = {"text-align": "center"},
                                        children=[
                                            html.A(href="https://services.onetcenter.org/", 
                                                title="This site incorporates information from O*NET Web Services. Click to learn more.",
                                                children=[html.Img(src="https://www.onetcenter.org/image/link/onet-in-it.svg", 
                                                        style={"width": "130px", "height": "60px", "border": "none"}, 
                                                        alt="O*NET in-it"
                                                            )
                                                            ]
                                                )
                                            ]
                                            ),
                                    html.P(children=[
                                        "This site incorporates information from ",
                                        html.A(href="https://services.onetcenter.org/", children = ["O*NET Web Services"]),
                                        " by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). O*NET&reg; is a trademark of USDOL/ETA."
                                    ])
                                ]

                                )

                            ]
                        ),
                    dbc.Tab(label = "Gap Analysis", className = "mx-3",
                            children =[
                                html.Div(className = "mx-3",
                                        children = [
                                                    html.Label("Current Occupation"),
                                                    dcc.Dropdown(id="current_occupation_dropdown",
                                                                    options =dropdown_occupations()),
                                                    html.Label("Target Occupation"),
                                                    dcc.Dropdown(id="target_occupation_dropdown",
                                                                    options =dropdown_occupations()),
                                                    html.Hr(),
                                                    ]
                                        ),
                                html.Div(id = "gap_analysis_tabs")
                                        ]
                                    )
    ])
    return tabs

def occupation_details_tab(onetsoc_code):
    tabs = dbc.Tabs([
                    dbc.Tab(label = "About", className = "mx-3",
                            children = [
                                html.H5(get_occupation_onetsocCode_dict()[onetsoc_code]),
                                html.P(
                                    children = [get_occupation_description(onetsoc_code)]
                                ),
                                html.H5(children = ["Tasks"]),
                                occupation_tasks_content(onetsoc_code),
                                html.H5(children = ["Top 5 work activities"]),
                                occupation_activities_content(onetsoc_code)

                            ]
                        ),
                    dbc.Tab(label = "Qualification", className = "mx-3",
                            children = [
                                html.H5(children = ["Education"]),
                                occupation_content(onetsoc_code)

                            ]
                        ),
                    dbc.Tab(label="Jobs - coming soon", className = "mx-3", disabled=True
                        ),

                    
    ])
    return tabs

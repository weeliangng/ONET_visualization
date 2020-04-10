import sqlite3
import dash_core_components as dcc
import dash_html_components as html

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

def default_sidebar():
    tabs = dcc.Tabs([
                    dcc.Tab(label = "Welcome",
                            children = [
                                
                                html.P(children = ["""This visualization is developed to help job seekers identify other occupations similar to their existing occupation.
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
                                  * Note that some occupations do not have any occupations within the selected relatedness range pointing towards it. In that case no occupation will be added.
                                * Click on "Add" Button
                                """)

                            ]
                        ),
    ])
    return tabs

def occupation_details_tab(onetsoc_code):
    tabs = dcc.Tabs([
                    dcc.Tab(label = "About",
                            children = [
                                html.P(
                                    children = [get_occupation_description(onetsoc_code)]
                                ),
                                html.H5(children = ["Tasks"]),
                                occupation_tasks_content(onetsoc_code),
                                html.H5(children = ["Top 5 work activities"]),
                                occupation_activities_content(onetsoc_code)

                            ]
                        ),
                    dcc.Tab(label = "Qualification",
                            children = [
                                html.H5(children = ["Education"]),
                                occupation_content(onetsoc_code)

                            ]
                        ),
                    dcc.Tab(label = "Openings",
                            children = [


                            ]
                        ),
                    
    ])
    return tabs

import sqlite3

def get_occupation_description(onetsoc_code):
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_description_sql = "select * from occupation_data where onetsoc_code ='{}';".format(onetsoc_code)
    c = conn.cursor()

    for row in c.execute(onetsoc_occupation_description_sql):
        description = row[2]
    return description

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
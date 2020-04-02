import sqlite3

def get_occupation_onetsocCode_list():
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_sql = """select distinct career_changers_matrix.onetsoc_code, title as occupation from career_changers_matrix 
                            inner join occupation_data on career_changers_matrix.onetsoc_code = occupation_data.onetsoc_code;"""
    c = conn.cursor()
    data = []
    for row in c.execute(onetsoc_occupation_sql):
        data.append({
            row[0]: row[1]
        })
    conn.close()
    return data
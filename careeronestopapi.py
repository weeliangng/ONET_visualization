import yaml
import requests

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


def get_skillsgap_json(OnetCodeSource, OnetCodeTarget, userId, api_key):
    request_url = "https://api.careeronestop.org/v1/skillgap/{userId}/{OnetCodeSource}/{OnetCodeTarget}/United%20States/25".format(userId = userId, 
                                                                                                                                    OnetCodeSource = OnetCodeSource, 
                                                                                                                                    OnetCodeTarget= OnetCodeTarget )
    response  = requests.get(request_url, headers = {"Authorization": api_key})
    return response.json()

skills_gap = get_skillsgap_json(41303103, 41309901, userId, api_key)

for gap in skills_gap.keys():
    print(gap)


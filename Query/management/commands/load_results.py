import json
from django.core.management.base import BaseCommand
from Query.models import Meet, Project, Result  
from Query.views import update_result,download
json_dir = 'cache.json'

                    
def update_from_online():
    meet_data = json.loads(download("https://wx.bjsh98.com/mobile/query/getMeetInfo"))
    with open(json_dir) as f:
        cache = json.load(f)

    for meet_info in meet_data:
        mid = meet_info['mid']
        meet, _ = Meet.objects.get_or_create(
            mid=meet_info['mid'],
            defaults={'name': meet_info['meetname']}
        )

        if str(mid) not in cache:
            cache[str(mid)] = {}
        if meet_info not in cache["meetList"]:
            cache["meetList"].append(meet_info)                                
        try:
            cache[str(mid)]["matches"] = json.loads(download(f"https://wx.bjsh98.com/mobile/query/getAllSchedule?mid={meet_info['mid']}"))
        except json.decoder.JSONDecodeError:
            cache[str(mid)]["matches"] = []
        
        for match in cache[str(mid)]["matches"]:
            project, _ = Project.objects.get_or_create(
                contest=meet,
                name=match['projectname'],
                xingbie = ["男子", "女子", "混合"][match['xingbie']-1],
                zubie = match['zubie'],
                leixing = match['leixing']
            )
            try:
                results = json.loads(download(f"https://wx.bjsh98.com/mobile/query/getResultsById?type=all&mid={meet_info['mid']}&sid={match['sid']}"))
            except json.decoder.JSONDecodeError:
                results = {}
            cache[str(mid)][str(match["sid"])] = results
            if results:
                update_result(results, project)

    with open("cache.json", mode="w", encoding="utf-8", errors="ignore") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_from_local():         
    with open(json_dir) as f:
        data = json.load(f)
        # 创建或获取比赛实例
        for meet in data["meetList"]: 
            contest, created = Meet.objects.update_or_create(
                name = meet["meetname"],
                mid = meet["mid"]
            )
            mid = meet["mid"] 
            for match in data[str(mid)]["matches"]:
                project, _ = Project.objects.get_or_create(
                    contest=contest,
                    name=match['projectname'],
                    xingbie = ["男子", "女子", "混合"][match['xingbie']-1],
                    zubie = match['zubie'],
                    leixing = match['leixing'],                       
                    )  
                try:
                    results = data[str(mid)][str(match["sid"])]
                except:
                    pass
                if results:
                    update_result(results,project)

class Command(BaseCommand):
    help = 'Import competition data from JSON files and online(bjsh)'
    def handle(self, *args, **options):
        Meet.objects.all().delete()
        Project.objects.all().delete()
        Result.objects.all().delete()
        load_from_local()
        # update_from_online()

"""Server/build-side collection only. No credentials; fail closed on partial data."""
import concurrent.futures, datetime as dt, json, pathlib, subprocess, time
from urllib.parse import urlencode

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 'https://api.taskmarket.dev'
RANGES = ('7d','30d','90d','all')

def fetch(path, params):
    url = BASE + path + '?' + urlencode(params)
    for attempt in range(3):
        r = subprocess.run(['curl','--fail','--silent','--show-error','--max-time','45',url],capture_output=True,text=True)
        if r.returncode == 0:
            value = json.loads(r.stdout)
            if isinstance(value,dict) and ('error' in value or value.get('success') is False):
                raise ValueError(f'API error at {url}: {value}')
            return value, {'url':url,'fetchedAt':dt.datetime.now(dt.timezone.utc).isoformat()}
        time.sleep(attempt + 1)
    raise RuntimeError(f'Fetch failed: {url}: {r.stderr[:200]}')

def weekly(tasks):
    weeks = {}
    for t in tasks:
        date = dt.datetime.fromisoformat(t['createdAt'].replace('Z','+00:00')).astimezone(dt.timezone.utc).date()
        week = (date-dt.timedelta(days=date.weekday())).isoformat()
        row = weeks.setdefault(week, {'week':week,'tasks':0,'posters':{}})
        address = t['requester'].lower()
        row['tasks'] += 1
        row['posters'][address] = row['posters'].get(address,0)+1
    return [{'week':w,'tasks':r['tasks'],'posters':len(r['posters']),
             'largestPosterTasks':max(r['posters'].values()),
             'top5Tasks':sum(sorted(r['posters'].values(),reverse=True)[:5])}
            for w,r in sorted(weeks.items())]

def collect_chain(chain):
    records = {}
    sources = []
    jobs = [('stats','/api/market/stats',{}),('breakdowns','/api/stats/breakdowns',{}),
            ('feed','/api/stats/activity-feed',{'limit':40})]
    for period in RANGES:
        jobs += [(f'series_{period}','/api/stats/platform-time-series',{'range':period,'bucket':'day'}),
                 (f'heat_{period}','/api/stats/activity-heatmap',{'range':period,'dimension':'hourOfWeek'})]
    def job(spec):
        name,path,params=spec
        value,source=fetch(path,{'chainId':chain,**params})
        return name,value,source
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for name,value,source in pool.map(job,jobs):
            records[name]=value;sources.append(source)
    tasks=[];cursor=None;seen=set();page_count=0
    for _ in range(500):
        params={'chainId':chain,'sort':'newest','limit':100}
        if cursor: params['cursor']=cursor
        page,source=fetch('/api/tasks',params);sources.append(source);page_count+=1
        assert isinstance(page.get('tasks'),list), 'Missing tasks array'
        for t in page['tasks']:
            if t['id'] not in seen:
                seen.add(t['id']);tasks.append({k:t[k] for k in ('id','requester','createdAt','status','mode','reward')})
        if not page.get('hasMore'): break
        nxt=page.get('nextCursor')
        if not nxt or nxt==cursor: raise ValueError('Non-advancing cursor')
        cursor=nxt
    else: raise ValueError('Incomplete task pagination')
    records['tasks']=tasks;records['weekly']=weekly(tasks);records['taskPages']=page_count
    records['sources']=sources
    assert all(isinstance(records[f'series_{r}'],list) for r in RANGES)
    return records

def main():
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(collect_chain,(4217,8453)))
    result={'schema':1,'startedAt':started,'asOf':dt.datetime.now(dt.timezone.utc).isoformat(),
            'chains':dict(zip(('4217','8453'),results))}
    out=ROOT/'site/data.json';temp=out.with_suffix('.tmp')
    temp.write_text(json.dumps(result,separators=(',',':')));temp.replace(out)
    print(json.dumps({'asOf':result['asOf'],'bytes':out.stat().st_size,
                     'tasks':{c:len(v['tasks']) for c,v in result['chains'].items()}}))

if __name__=='__main__': main()

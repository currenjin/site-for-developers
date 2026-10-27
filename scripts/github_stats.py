"""Build-time GitHub Stars snapshot. Visitors never call the GitHub API."""
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
API='https://api.github.com/repos/currenjin/site-for-developers'

def compact_stars(count):
    if type(count) is not int or count<0:raise ValueError('Stars must be a nonnegative integer')
    if count<1000:return str(count)
    unit,divisor=('m',1000000) if count>=1000000 else ('k',1000)
    value=(Decimal(count)/Decimal(divisor)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
    return format(value,'f').rstrip('0').rstrip('.')+unit

def validate_payload(payload):
    count=payload.get('stargazers_count') if isinstance(payload,dict) else None
    compact_stars(count)
    return count

def read_snapshot(path):
    path=Path(path)
    if not path.exists():return None
    payload=json.loads(path.read_text(encoding='utf-8'))
    count=payload.get('stars') if isinstance(payload,dict) else None
    compact_stars(count)
    return count

def fetch_stars():
    headers={'Accept':'application/vnd.github+json','User-Agent':'SFD-site-build'}
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:headers['Authorization']='Bearer '+token
    with urlopen(Request(API,headers=headers),timeout=10) as response:
        return validate_payload(json.load(response))

def update_snapshot(path):
    try:
        count=fetch_stars();compact_stars(count)
    except (OSError,ValueError):
        print('GitHub Stars refresh unavailable; keeping the last verified snapshot.')
        return False
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'stars':count,'fetchedAt':datetime.now(timezone.utc).isoformat(timespec='seconds')},indent=2)+'\n',encoding='utf-8')
    print('GitHub Stars refreshed:',count)
    return True

if __name__=='__main__':update_snapshot(ROOT/'web/github.json')

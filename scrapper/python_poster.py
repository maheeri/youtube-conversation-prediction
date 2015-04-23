import requests
import json
cookie = '__utma=27069237.2003427691.1412866368.1423408486.1423872619.6; __utmz=27069237.1423408486.5.2.utmcsr=reddit.com|utmccn=(referral)|utmcmd=referral|utmcct=/r/videos/comments/2v4xan/lady_blamed_me_for_running_a_red_light_the_video/; LOGIN_INFO=f9e920220475b91a3e4592950cc3c311c0AAAAB7IjQiOiAiR0FJQSIsICI3IjogMCwgIjEiOiAxLCAiOCI6IDU4OTEwNzQ3OTQ4NSwgIjMiOiA3NjcxMTk5NDZ9; lTdoH.resume=S9WOm9COijg:566,itkl7cHcX_E:793,7nyRo7lJ564:168,F29jFlAlPBY:178; SID=DQAAANMBAABcgTt8FOSmiUdsrDA9hYEZ350l6OEshXqk3tdEo9y5sp0kFfhoJ-1HKDXfMNUJIhFCnSx2Ap5MdBwRX952krgv1NbJ4tx1Gd81gWCWjYR6yOf3qcE6iDXOO8QispvOKXeKibGaELJh2jNoSvcRiTZLigRNdHSkNZ_VeyNLOowhdyy93DWtOTGkt-8Bplq9PiQDh124KuP57_0ua3xEUK36z-INkpukd91vrVfWdTqEfPyUep-qeMw4XLpZnOkDhcBNH-6phpFKTWEiaTdP-uU1O06s5FUf4p9T0eK7JpZayYUi3BbX1L4NjjaEr9iqUCqSyRtKxBmczKgOiubmM5NubAyOQNCxv4XP4hA0djjsyQTHvL3CPI0T7Ut4f1LTuDEZC-qfRWZQ23isRhelbZEqS1M-tEZ849rZ2AFyovTSI_pVPxo07KVpy7sqxmZAraWw9LMzKvY5qhhB1X0j2rC4K-xxUQusnfC5Q4ugcjVmuA28kwLak2MmhvOR5iJBwXiQcK3JJB-AQ443SAMxQcMXQkkfU4nFyvT63BHYzKlKB4TYv7ueIn2XFJrVCEt791cKX2L_Q-OpNY7uf0aApzUTNLtyjOwOzSWDFqqJL-hti9To_Q_N5qZO8qs5DaMWxwk; HSID=AJ0QmLcdP3G8ArNwY; SSID=AZm19dh84UV1qTJGp; APISID=2fPvlTP5uQfpQ_pU/AWsHUGH330egdFcSr; SAPISID=Hk6iM0JikP7DA-rp/A-9tId5baAKeK13mD; YSC=X2rm8RnTuxo; enabledapps.uploader=0; VISITOR_INFO1_LIVE=0UnyREt63iA; PREF=f5=30&f1=50000000&fv=16.0.0&al=en'
headers = { "Content-Type": "application/x-www-form-urlencoded",
            "cookie": cookie
        }
payload = {'session_token': "QUFFLUhqbTJkdTVuME9BUW1STUUwQ3VldXZCbmt2SnlDUXxBQ3Jtc0ttdk5vNm0wbExaMXR6SEQ0cU9PNElJdWhBc295OWhvdlVYek04d0g4ejlFRmVfUXpHbURuM25LemtJYjNHUENrSlV2SXJEMVp2dWVCOGxJTWhGQVoxYWZSblJOZDlyOXBiY3dNTUwzRVpLMWpKMzBjMGR0M3h5d3hFMWNUdkJYODVkVFVTcGxMLUh5NVUwdlAxdVlFRHFEb3hfSXc"}
url = "https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=b96LpPlevNI"
data = 'session_token=QUFFLUhqbFg3RHYwZi05TE5sQ1F0U1JwRkpxME9vOXAwd3xBQ3Jtc0trbWNBWGxWSzVHS2NCNmZ6eXpGUjNnRDFCQ2Ixclp4TGNqQ0tKeE1UQ2kxNTllZDBsWEZlc0JvS1psZU4ydjBnWTkzNFh2YkhjSDdWbDMyejBYZWJaTWhfb1FmRHZ6RUNsaWZmUEJWa0tLeEJ2Y0FUUFo2ZWdIWjBwRnJPNk1GREVkeTg2WEgtUWFudlVWYThMV0hUVk16VFdjZUE%3D'
r = requests.post(url, headers=headers, data=data )
print(r.status_code, r.reason)
print(r.text[:300] + '...')
"""
import urllib.parse
import urllib.request

url = 'https://www.youtube.com/insight_ajax'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
values = {'' : 1,
          'v' : '0ne7ChIFlZg' }
headers = { 'User-Agent' : user_agent
            }

data  = urllib.parse.urlencode(values)
data = data.encode('utf-8')
req = urllib.request.Request(url, data, headers)
with urllib.request.urlopen(req) as response:
   the_page = response.read()
"""


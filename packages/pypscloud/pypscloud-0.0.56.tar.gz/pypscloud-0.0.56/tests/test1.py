import sys
import os
sys.path.append(os.path.abspath("/Users/lmarchand/PycharmProjects/pypscloud/"))

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

from pypscloud.pypscloud import *


def test_site(ps):
    mps = ps.get_all_mp_from_account(6)
    for mp in mps:
        accountId = mp['accountId']
        siteId = mp['locationId']
        site = ps.get_site(mp['locationId'])
        if site['locationName'] == 'PQube3 e Test wall':
            print(mp)
            print(site)
            new_site = site
            del new_site['locationId']
            del new_site['measurementPoints']
            new_site['locationName'] = 'PQube3 e Test wall 09'

            ps.set_site(accountId, siteId, new_site)


def test_all_mps_accounts(ps):
    df = ps.get_all_mps_from_all_accounts_as_df()
    print(df)


def test_tz():

    # current_timestamp = datetime.time()
    #current_datetime = datetime.now()
    #datetime
    #dt_from_ts = datetime(current_timestamp)

    s, e = ps_build_start_end_date_from_midnight(7, 'America/Los_Angeles')
    print(s)
    print(e)

    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/Los_Angeles')
    print(d)
    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/New_York')
    print(d)
    ss = ps_time_with_tz(s, 'America/Los_Angeles')
    print(ss)
    ee = ps_time_with_tz(e, 'America/Los_Angeles')
    print(ee)


def test_param(ps):
    p = ps.get_mp_parameters(15206)
    print(p)

    p = ps.get_maxLoadCurrentDemand(15206)
    print(p)



def test_fwu(ps):
    f = ps.firmware_set_version_to_device('3.10.6.24.02.01', [13817])
    print(f)
    accounts = ps.get_all_accounts()
    print(accounts)

    p = ps.get_mp(13817)
    print(p)

    s = ps.firmware_start([13817])
    print(s)


def test_account(ps):
    acc_edge_test_bench = 489
    test_acc = 138
    a2 = {}
    a = ps.get_account(test_acc)
    print(a)
    if a['useFirmwareAutomaticUpdates'] == False:
        if 'address' not in a:
            a2['address'] = {}
            a2['address']['country'] = ''
            a2['address']['state'] = ''
            a2['address']['city'] = ''
            a2['address']['street1'] = ''
            a2['address']['street2'] = ''
            a2['address']['zipCode'] = ''
        else:
            a2['address'] = a['address']
            del a2['address'] ['addressId']

        if a2['address']['country'] == None: a2['address']['country'] = ''
        if a2['address']['state'] == None: a2['address']['state'] = ''
        if a2['address']['city'] == None: a2['address']['city'] = ''
        if a2['address']['street1'] == None: a2['address']['street1'] = ''
        if a2['address']['street2'] == None: a2['address']['street2'] = ''
        if a2['address']['zipCode'] == None: a2['address']['zipCode'] = ''


        a2['useFirmwareAutomaticUpdates'] = True
        a2['isPartner'] = a['isPartner']
        a2['partnerAccountId'] = a['partnerAccountId']
        a2['name'] = a['name']
        a2['subscriptionExpiry'] = "2024-04-01T23:00:00.000Z"
        a2['subscriptionType'] = a['subscriptionType']

        info = ps.set_account(test_acc,a2)
        print(info)
    a2 = ps.get_account(test_acc)
    print(a2)


def test_firmware_search(ps):
    f = ps.firmware_search()
    print(f)


def test_get_all_mp_from_all_customers_of_this_partner(ps):
    print('test_get_all_mp_from_all_customers_from_this_partner')
    dominion = 252
    dominion_transmission = 642
    all_dom = [dominion, dominion_transmission]

    #mps = ps.get_all_mp_from_account(dominion, True)
    #print(mps)

    mps = ps.get_all_mp_from_accounts(all_dom, True) # true = include partners's own MP
    print(mps)



def test_changing_mp_name(ps):
    dominion = 252
    datacenters = 572
    #mps = ps.get_all_mp_from_account(dominion, True)
    #print(mps)
    accountId = 8869
    siteId = 11284
    mpId = 86355902

    mp = ps.get_mp(mpId)
    print(mp)

    site_mp = {
        "site": {
            "locationName": "move to",
            # "shortname": "move to",
            "address1": "1683-1, Prieur Est",
            "address2": "",
            "city": "Montréal",
            "state": "PQ",
            "zipCode": "H2C 1M5",
            "country": "Canada",
            "siteInformation": "",
            "latitude": 45.5667066,
            "longitude": -73.6578514
        },
        "measurementPoint": {
            "mpId": mp['mpId'],
            "measurementPointTypeId": 1
        },
        "parameters": None
    }

    code = ps.set_site_mp(accountId, siteId, mpId, site_mp)
    print(code)


def test_notification_groups(ps):
    ngs = ps.get_notification_groups()
    
    ng_recs = ngs['records'] 
    for ng_rec in ng_recs:
        ng_info = ps.get_notification_group(ng_rec['notificationGroupId'])
        print(ng_info)


def test_s3_download_date_range(ps):
    env = ps.get_env()
    p = env['awsprofile']
    s3 = PSS3(p)
    start = '2023-12-01T00:00:00.000Z'
    end = '2024-04-01T12:00:00.000Z'
    beg_date = dateutil.parser.isoparse(start)
    end_date = dateutil.parser.isoparse(end)

    device_event_dir = 'iot/pqube/P3019857/event'
    #os.makedirs(device_event_dir, exist_ok=True)
    count = s3.download_date_range(device_event_dir, beg_date, end_date)
    print(count)


def test_get_activigy_log(ps):
    act = 'navigation.'
    start = '2025-01-01T05:00:00.000Z'
    end =   '2025-01-14T12:00:00.000Z'
    res = ps.get_activity_log(act, start, end)
    print(res)


def test_mp_get(ps):
    mp = ps.get_mp(17427)
    print(mp)

def test_get(ps):
    response = ps.get('measurementPointFile/hfEmissionsFiles/21613?startDate=2024-05-01&endDate=2024-05-01')
    print(response)
    print(response.json())

    
def test_catchup(ps):
    request = {
                  "dateRangeStart": "2024-01-01T00:00:00.000Z",
                  "dateRangeEnd": "2024-07-08T00:00:00.000Z",
                  "calculateOnly": True,
                  "entireRange": False,
                  "startCatchup": False
                }

    cloud_unit_prod = 13817
    gaps = ps.catchup(request, cloud_unit_prod)
    print(gaps)


def test_device_file_request(ps):

    request = {
        "measurementPointId": 18634,
        "files": [
            "channels-P3021816.json"
        ]
    }
    r = ps.device_file_request(request)
    print(r)


def test_download_file(ps):
    env = ps.get_env()
    p = env['awsprofile']
    s3 = PSS3(p)
    request_file = 'batchfwu_cfg.json'
    r = s3.download_file(request_file)
    print(r)


def test_get_event_mp_alarm_evt_notes_status(ps):
    request = {
      "measurementPointId": 9240,
      "dateRangeStart": "2024-06-01T07:00:00.000Z",
      "dateRangeEnd": "2024-10-03T06:59:00.000Z",
      "natures": [
        "event",
        "status"
      ],
      "typeIds": [
        "s1"
      ],
      "includeRetired": False,
      "includeLabels": True,
      "sorting": [
        {
          "column": "triggeredWhen",
          "desc": True
        }
      ],
      "count": 20,
      "offset": 0
    }

    response = ps.get_event_mp_alarm_evt_notes_status(request)
    if (response != None):
        print(response)

    return response


def test_get_maintenance_history(ps):
    mpId = 20656
    resp = ps.get_maintenance_history(mpId)
    print(resp)


def test_post(ps):
    
    request = {
    "createdDateRangeStart": "2024-08-18T04:00:00.000Z",
        "createdDateRangeEnd": "2024-11-19T04:59:00.000Z",
        "offset": 0,
        "count": 20,
        "sorting": [],
        "filter": []
    }

    url = 'reportResults?measurementPointId=17586'
    
    response = ps.post(url, request)
    if response is not None:
        print(response)
    else:
        print('Error with Post')
    

def main():
    ps = PSCommon('production')
    ps.login()

    print(ps)
    print(ps.get_env())

    # test_get(ps)

    # test_s3_download_date_range(ps)

    # ps_post_cmd(13817,7)
    # ps_post_cmd(5124,6)

    # ps.device_file_request_by_mp(16667, ["channels-P3020805.json"])

    # test_site(ps)
    # test_all_mps_accounts(ps)
    # cd = ps.get_mp_channel_def(15206)
    # hb = ps.get_mp_heartbeat(20247, 2)
    # print(hb)
    # test_tz()
    # test_param(ps)
    # test_fwu(ps)

    # test_account(ps)
    # test_changing_mp_name(ps)
    # test_firmware_search(ps)
    # test_notification_groups(ps)
    test_get_activigy_log(ps)
    # test_mp_get(ps)
    # test_catchup(ps)
    # test_device_file_request(ps)
    # test_s3_download_date_range(ps)
    # test_download_file(ps)
    # test_get_event_mp_alarm_evt_notes_status(ps)
    # test_get_maintenance_history(ps)
    # test_post(ps)
    # test_get_all_mp_from_all_customers_of_this_partner(ps)

main()
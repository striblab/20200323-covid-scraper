import re
import datetime
import json
import math
import requests
from django.conf import settings

def slack_latest(text, channel):
    MAX_BLOCK_LENGTH = 3000

    endpoints = {
        '#covid-tracking': settings.SLACK_WEBHOOK_ENDPOINT_COVID_TRACKING,
        '#virus': settings.SLACK_WEBHOOK_ENDPOINT_VIRUS,
        '#robot-dojo': settings.SLACK_WEBHOOK_ENDPOINT_DOJO,
    }
    # endpoint = settings.SLACK_WEBHOOK_ENDPOINT
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    char_count = len(text)
    remaining_text = text
    if char_count <= MAX_BLOCK_LENGTH:
        block_texts = [text]
    else:
        block_texts = []
        n = 0
        how_many_times = math.ceil(char_count / MAX_BLOCK_LENGTH)
        while n < how_many_times:
            raw_substring = remaining_text[0:MAX_BLOCK_LENGTH]
            last_line_break_charnum = raw_substring.rfind('\n')
            clean_substring = remaining_text[0:last_line_break_charnum]
            block_texts.append(clean_substring.strip())
            remaining_text = remaining_text[last_line_break_charnum:]
            n+=1

        # Check for remainder
        if len(remaining_text.strip()) > 0:
            block_texts.append(remaining_text)


    blocks_formatted_list = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": b
        }
    } for b in block_texts]

    payload = {
        # 'text': text,
        'blocks': blocks_formatted_list
    }

    print(payload)
    r = requests.post(endpoints[channel], data=json.dumps(payload), headers=headers)

    if r.ok:
        print('Slack message appears to have fired succesfully.')
    else:
        print('Slack error...')
        print(r.status_code)
        print(r.text)

#### Things for reading cached HTML stored on S3 ####
def get_matching_s3_cached_html(bucket, prefix, s3):
    keys = []

    kwargs = {
        'Bucket': bucket,
        'Prefix': '{}/html/situation'.format(prefix)
    }
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            keys.append(obj['Key'])

        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return keys


def find_filename_date_matchs(matching_files, hour, slice='first'):
    ''' Get the first or last cached file from a given hour on this date. If hour is null, return the last record from that date'''
    if hour:
        file_regex = re.compile('(\d{4}-\d{2}-\d{2})_' + str(hour) + '\d{2}.html')
    else:
        file_regex = re.compile('(\d{4}-\d{2}-\d{2})_\d{4}.html')

    date_matches = [f for f in matching_files if re.search(file_regex, f)]
    date_matches.sort()

    date_matches_unique = {}
    for d in date_matches:
        parsed_date = re.search(file_regex, d)
        scrape_date = datetime.datetime.strptime(parsed_date.group(1), '%Y-%m-%d').date()
        if not hour:
            date_matches_unique[scrape_date] = d  # Keep going until you reach the last one
        elif slice == 'first':
            if scrape_date not in date_matches_unique.keys():
                date_matches_unique[scrape_date] = d
        elif slice == 'last':  # Keep overwriting until you get to the last one
            date_matches_unique[scrape_date] = d

    listified_dict = [{'scrape_date': k, 'key': v} for k, v in date_matches_unique.items()]

    return listified_dict


def get_s3_file_contents(key, bucket, s3):
    response = s3.get_object(Bucket=bucket, Key=key['key'])
    return response['Body'].read()

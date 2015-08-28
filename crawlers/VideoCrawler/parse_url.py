import json
import requests
import re
import time


def main():

    input_json_file = open("NewVideo.json", "r")
    json_tmp = json.load(input_json_file)
    input_json_file.close()

    count = 0
    stop = 0

    for item in json_tmp:

        count += 1

        if count % 14 == 0:
            print "Process %d%%" % (count/14)

        video_id = re.search("/v_show/id_(.+)\.html", item['video_url']).groups(1)[0]

        values = {
            'client_id': 'dd50335594101a48',
            'video_id': video_id
        }

        url = "https://openapi.youku.com/v2/videos/show_basic.json"

        result = requests.get(url, params=values)

        result_json = result.json()

        try:
            with open("output", "a") as output_file:
                output_file.write(result_json['duration'] + '\n')
        except KeyError:
            pass

if __name__ == "__main__":
    main()

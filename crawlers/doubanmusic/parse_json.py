import json

music_parse_result = []

already_has = set({})

def main():
    with open("Music.json", "r") as read_file:
        read_json = json.load(read_file)

        for one_list in read_json:

            if one_list["music_list_id"] not in already_has:
                already_has.add(one_list["music_list_id"])

                song_list = one_list["music_list"]
                for item in song_list:
                    music_parse_result.append(int(item["song_length"]))

    print len(music_parse_result)

    with open("Music.output", "w") as write_file:
        for item in music_parse_result:
            write_file.write(str(item)+"\n")


if __name__ == "__main__":
    main()
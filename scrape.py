import requests
import time
import json
import pathlib
import sqlite3
import csv

# This module contains scripts that call the REST API of speedrun.com
# to gather the necessary data.

def try_request(uri):

    # This function handles decoding failures that occasionally
    # occur during requests.

    response_dict = None
    attempts = 0
    while attempts < 3:
        try:
            json_raw = requests.get(uri).text
            response_dict = json.loads(json_raw)
            break
        except json.decoder.JSONDecodeError:
            attempts += 1
            time.sleep(5)
    return response_dict

def get_games_api():

    # This function retrieves game information and saves the
    # returned JSON to disk.

    batch = 200
    i = 34405
    game_dir = pathlib.Path("json/games")
    embed = "levels,categories,moderators,gametypes,platforms,regions,genres,engines,developers,publishers,variables"
    uri = f"https://www.speedrun.com/api/v1/games?embed={embed}&max={batch}&offset={i}"
    while True:
        print(f"{i}: requesting", end = "\r")
        response_dict = try_request(uri)
        game_list = response_dict["data"]
        for game_dict in game_list:
            game_id = game_dict["id"]
            with open(game_dir / f"{game_id}.json", "w") as target:
                json.dump(game_dict, target)
        (direction, uri) = list(response_dict["pagination"]["links"][-1].items())[-1]
        if direction == "prev":
            break
        i += batch
        time.sleep(2)
        
def get_runs_api():

    # This function retrieves run information for each of the games
    # retrieved using "get_games_api", and stores the returned JSON
    # in a SQLite database.

    conn = sqlite3.connect("speedruns.db")
    cursor = conn.cursor()
    batch = 200 
    game_paths = [path for path in pathlib.Path("json\games").iterdir()]
    game_paths.sort()
    for (j, path) in enumerate(game_paths, 1):
        i = 0
        game_id = path.stem
        while True:
            uri = f"https://www.speedrun.com/api/v1/runs?game={game_id}&max={batch}&offset={i}"
            print(f"{j}/{len(game_paths)}: {i} requesting")
            response_dict = try_request(uri)
            run_list = response_dict["data"]
            if not run_list:
                break
            for run_dict in run_list:
                run_id = run_dict["id"]
                json_raw = json.dumps(run_dict)
                cursor.execute("INSERT INTO runs_json (run_id, raw) VALUES (?, ?) ON CONFLICT (run_id) DO NOTHING;",
                                (run_id, json_raw))
            i += batch
            if i >= 10000:
                with open("run_over", "a") as target:
                    target.write(f"{game_id}\n")
                break
            time.sleep(1)
        conn.commit()

def get_users_api():

    # This function retrieves user information and stores the 
    # returned JSON in a SQLite database.

    conn = sqlite3.connect("speedruns.db")
    cursor = conn.cursor()
    batch = 200
    for char in "abcdefghijklmnopqrstuvwxyz0123456789_":
        i = 0
        while True:
            uri = f"https://www.speedrun.com/api/v1/users?name={char}&max={batch}&offset={i}"
            print(f"{char}-{i}: requesting")
            response_dict = try_request(uri)
            user_list = response_dict["data"]
            if not user_list:
                break
            for user_dict in user_list:
                user_id = user_dict["id"]
                json_string = json.dumps(user_dict)
                cursor.execute("INSERT INTO users_json (user_id, raw) VALUES (?, ?) ON CONFLICT (user_id) DO NOTHING;", 
                   (user_id, json_string))
            i += batch
            time.sleep(1)
        conn.commit()
    conn.close()

def get_platforms_api():

    # This function retrieves game information and saves the
    # returned JSON in a CSV file. 

    batch = 200
    i = 0
    platforms = []
    while True:
        uri = f"https://www.speedrun.com/api/v1/platforms?max={batch}&offset={i}"
        print(f"{i}: requesting")
        response_dict = try_request(uri)
        platform_list = response_dict["data"]
        if not platform_list:
            break
        for platform_dict in platform_list:
            platform_id = platform_dict["id"]
            json_string = json.dumps(platform_dict)
            platforms.append((platform_id, json_string))
        i += batch
        time.sleep(1)
    with open("platforms.csv", "w") as target:
        csv.writer(target).writerows(platforms)      

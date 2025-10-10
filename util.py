DDRAGON_BASE_URL = 'https://ddragon.leagueoflegends.com/cdn/'
DDRAGON_VERSION = '15.15.1'
RESPWAN_TIMER_ADJUSTMENT_MS = 0

async def get_summoner_name_by_puuid(connection, puuid):
    if puuid == '':
        return 'boot'
    summoner_response = await connection.request('GET', f'/lol-summoner/v2/summoners/puuid/{puuid}')
    summoner = await summoner_response.json()
    return summoner.get('gameName')

async def team_add_names(connection, team):
    new_team = []  # Initialize a new list to store the updated team

    for player in team:
        summoner_name = await get_summoner_name_by_puuid(connection, player['puuid'])
        player['gameName'] = summoner_name
        new_team.append(player)

    return new_team


def live_to_url(ent, type):
    # if type == 'summoner':
    #     name = summoners_lookup[id]
    #     url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/img/spell/{name}.png'
    #     return url
        
        
    if type == 'icon':
        name = ent
        url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/img/champion/{name}.png'
        return url
    
    
    if type == 'splash':
        skin = 0
        # if len(id) > 3:
        #     skin = id[-3:]
        #     id = id[:-3]
            
        # skin = str(int(skin))
        
        name = ent
        url = f'{DDRAGON_BASE_URL}img/champion/splash/{name}_{skin}.jpg'
        return url


    if type == 'loading':
        skin = 0
        # if len(id) > 3:
        #     skin = id[-3:]
        #     id = id[:-3]
            
        # skin = str(int(skin))
        
        name = ent
        url = f'{DDRAGON_BASE_URL}img/champion/loading/{name}_{skin}.jpg'
        return url
    

    if type == 'item':
        id = ent
        url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/img/item/{id}.png'
        return url
        
        
    if type == 'rune':
        pass


def live_players_to_url(players):
    url_players = []
    for player in players:
        championName = player.get('championName')
        player['championNameIcon'] = live_to_url(championName, 'icon')
        player['championNameSplash'] = live_to_url(championName, 'splash')
        player['championNameLoading'] = live_to_url(championName, 'loading')
        player['respawnTimer'] = player.get('respawnTimer') - RESPWAN_TIMER_ADJUSTMENT_MS / 1000
        url_items = []
        items = player.get('items')
        for item in items:
            itemID = item['itemID']
            item['itemIDIcon'] = live_to_url(itemID, 'item')
            
            url_items.append(item)
            
        player['items'] = url_items    
        url_players.append(player)

    return url_players


def post_teams_to_url(teams):
    url_teams = []
    for team in teams:
        players = team.get('players')
        url_players = []
        for player in players:
            championName = player.get('championName')
            player['championNameIcon'] = live_to_url(championName, 'icon')
            player['championNameSplash'] = live_to_url(championName, 'splash')
            player['championNameLoading'] = live_to_url(championName, 'loading')
            
            item_ids = player.get('items')
            url_items = []
            for itemID in item_ids:
                itemIDIcon = live_to_url(itemID, 'item')
                
                item = {
                    "itemID": itemID,
                    "itemIDIcon": itemIDIcon
                }
                
                url_items.append(item)

            # TODO urlitems
        
            player['patchedItems'] = url_items    
            url_players.append(player)
            
        team['players'] = url_players
        url_teams.append(team)



    return url_teams

def id_to_url(id, type):
    # champion icon, splashart?, skin splashart, summoner spells
    if id <= 0 or id == 18446744073709551615:
        return ''
    id = str(id)
    if type=='summoner':
        name = summoners_lookup[id]
        url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/img/spell/{name}.png'
        return url
        
        
    if type=='icon':
        name = champions_lookup[id]
        url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/img/champion/{name}.png'
        return url
    
    
    if type=='splash':
        skin = 0
        if len(id) > 3:
            skin = id[-3:]
            id = id[:-3]
            
        skin = str(int(skin))
        
        name = champions_lookup[id]
        url = f'{DDRAGON_BASE_URL}img/champion/splash/{name}_{skin}.jpg'
        return url


    if type=='loading':
        skin = 0
        if len(id) > 3:
            skin = id[-3:]
            id = id[:-3]
            
        skin = str(int(skin))
        
        name = champions_lookup[id]
        url = f'{DDRAGON_BASE_URL}img/champion/loading/{name}_{skin}.jpg'
        return url



import requests
import os

def download_json(url, folder, filename):
    try:
        # Make a GET request to fetch the raw JSON data
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Create the folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Define the full path to save the JSON file
        file_path = os.path.join(folder, filename)

        # Write the JSON data to a file
        with open(file_path, 'w') as json_file:
            json_file.write(response.text)

        return json_to_lookup(response.json()['data'], 'key')
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage:
# download_json('https://api.example.com/data', 'my_folder', 'data.json')
    
def startup_download():
    # Get the summoner data
    champion = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/champion.json'
    summoner = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/summoner.json'
    download_json(champion, '.', 'champion.json')
    download_json(summoner, '.', 'summoner.json')

def json_to_lookup(data, data_key):
    lookup_table = {}
    for item_key, item in data.items():
        key = item.get(data_key)
        if key:
            lookup_table[key] = item_key
    return lookup_table


# champion = https://ddragon.leagueoflegends.com/cdn/15.15.1/data/en_US/champion.json
# summoner = f'{DDRAGON_BASE_URL}{version}/data/en_US/summoner.json'
# https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aatrox_0.jpg
# https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Aatrox_0.jpg


def team_to_url(team):
    new_team = []
    for player in team:
        championId = player['championId']
        championPickIntent = player['championPickIntent']
        selectedSkinId = player['selectedSkinId']
        spell1Id = player['spell1Id']
        spell2Id = player['spell2Id']
        puuid = player['puuid']

        player['championIdIcon'] = id_to_url(championId, 'icon')
        player['championPickIntentIcon'] = id_to_url(championPickIntent, 'icon')
        
        player['championIdSplash'] = id_to_url(championId, 'splash')
        player['championPickIntentSplash'] = id_to_url(championPickIntent, 'splash')
        player['championIdSkinSplash'] = id_to_url(selectedSkinId, 'splash')

        player['championIdLoading'] = id_to_url(championId, 'loading')
        player['championPickIntentLoading'] = id_to_url(championPickIntent, 'loading')
        player['championIdSkinLoading'] = id_to_url(selectedSkinId, 'loading')

        player['summonerSpell1Icon'] = id_to_url(spell1Id, 'summoner')
        player['summonerSpell2Icon'] = id_to_url(spell2Id, 'summoner')
        new_team.append(player)

    return new_team


def bans_to_url(bans):
    ban_objects = []
    
    for ban in bans:
        ban_object = {}
        ban_object['championId'] = ban
        ban_object['championIdIcon'] = id_to_url(ban, 'icon')
        ban_object['championIdSplash'] = id_to_url(ban, 'splash')
        ban_object['championIdLoading'] = id_to_url(ban, 'loading')
        ban_objects.append(ban_object)

    return ban_objects


def get_all_champions(actions, teams):
    champions = []
    for action in actions:
        for sub_action in action:
            if sub_action.get('type') == 'pick' and sub_action.get('completed'):
                champion = sub_action.get('championId')
                if champion and champion > 0:
                    icon = id_to_url(champion, 'icon')
                    splash = id_to_url(champion, 'splash')
                    loading = id_to_url(champion, 'loading')
                    
                    for player in teams:
                        if player.get('championId') == champion:
                            cellId = player.get('cellId')
                            champion_obj = {
                                "cellId": cellId,
                                "championId": champion,
                                "championIdIcon": icon,
                                "championIdSplash": splash,
                                "championIdLoading": loading,
                            }

                            champions.append(champion_obj)

                            continue
            
        
    return champions

print()
def handle_bans(actions, myTeamSize):
    myTeamBans = []
    theirTeamBans = []
    numBans = 0
    for action in actions:
        
        for sub_action in action:
            print(sub_action['actorCellId'])
            if sub_action['type'] == 'ban' and sub_action['actorCellId'] < myTeamSize and sub_action['championId'] != 0:
                myTeamBans.append(sub_action['championId'])
                numBans += 1
            if sub_action['type'] == 'ban' and sub_action['actorCellId'] >= myTeamSize and sub_action['championId'] != 0:
                theirTeamBans.append(sub_action['championId'])
                numBans += 1
            
    myTeamBans = bans_to_url(myTeamBans)
    theirTeamBans = bans_to_url(theirTeamBans)
    
    bans = {
        "myTeamBans": myTeamBans,
        "numBans": numBans,
        "theirTeamBans": theirTeamBans
    }
    
    return bans
    
def fearless_unique(champions):
    seen = []
    unique = []
    for champion in champions:
        championId = champion.get('championId')
        if championId in seen:
            continue
        
        unique.append(champion)
        seen.append(championId)
        
    return unique


def fearless_remove_current(all_champs, current):
    fearless = []
    current_ids = []
    for champion in current:
        championId = champion.get("championId")
        current_ids.append(championId)
        
    for champion in all_champs:
        if champion.get('championId') in current_ids:
            continue
        
        fearless.append(champion)
        
    return fearless


def create_tk_data(teams, current_tk):
    tk_data = []
    for team in teams:
        players = team.get('players')
        for player in players:
            stats = player.get('stats')
            total_heal = stats.get('TOTAL_HEAL')
            total_heal_on_teammates = stats.get('TOTAL_HEAL_ON_TEAMMATES')
            total_damage_shielded_on_teammates = stats.get('TOTAL_DAMAGE_SHIELDED_ON_TEAMMATES')
            total_damage_self_mitigated = stats.get('TOTAL_DAMAGE_SELF_MITIGATED')
            
            puuid = player.get('puuid')
            riotIdGameName = player.get('roitIdGameName')
            riotIdTagLine = player.get('riotIdTagLine')
            if current_tk:
                for player_tk in current_tk:
                    puuid_tk = player_tk.get('puuid')
                    if puuid == puuid_tk:
                        total_heal += player_tk.get('TOTAL_HEAL')
                        total_heal_on_teammates += player_tk.get('TOTAL_HEAL_ON_TEAMMATES')
                        total_damage_shielded_on_teammates += player_tk.get('TOTAL_DAMAGE_SHIELDED_ON_TEAMMATES')
                        total_damage_self_mitigated += player_tk.get('TOTAL_DAMAGE_SELF_MITIGATED')
                
                
            tk = {
                "puuid": puuid,
                "riotIdGameName": riotIdGameName,
                "riotIdTagLine": riotIdTagLine,
                "total_heal": total_heal,
                "total_heal_on_teammates": total_heal_on_teammates,
                "total_damage_shielded_on_teammates": total_damage_shielded_on_teammates,
                "total_damage_self_mitigated": total_damage_self_mitigated
            }
            tk_data.append(tk)
            
    return tk_data


champions_url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/champion.json'
summoners_url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/summoner.json'
    
summoners_lookup = download_json(summoners_url, '.', 'summoner.json')
champions_lookup = download_json(champions_url, '.', 'champion.json')
puuid_lookup={}


# Getting Started
```bash
pip install -r requirements.txt
py main.py
```

Die Datei `test_client.html` kann ohne Abhängigkeiten im Browser geöffnet werden und beinhaltet eine Steuerung für Replays und Websocket und REST API Beispiele.

# Events

Events werden über Webosckets gepublished und haben folgendes Format:
```json
{
    "data": {...},
    "eventType": "UPDATE",
    "uri": "/lol-champ-select/v1/session",
    "_replay": {
        "is_replay": true,
        "replay_timestamp": "2025-08-14T14:16:40.865861",
        "original_timestamp": 1755172982008
    },
    "timestamp": "2025-08-14T14:16:40.975517"
}
```
- data sind die daten selbst, siehe unten
- eventType gibt an ob geupdatet, gelöscht... wird atm gibt es nur updates, heißt daten können einfach überschrieben werden.
- uri gibt den typ des events an (interne url)
- _replay (optional) gibt an ob es sich um ein replay handelt und ggf. timestamps dazu
- timestamp gibt den zeitpunkt des events an

## Pick Ban
Die relevantesten Punkte der Pick Ban Data:
```json
   {
        ...,
        "bans": {
            "myTeamBans": [
                {
                    "championId": 84,
                    "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Akali.png",
                    "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Akali_0.jpg",
                    "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Akali_0.jpg"
                },
                ...
            ],
            "numBans": 10,
            "theirTeamBans": [
                {
                    "championId": 22,
                    "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Ashe.png",
                    "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ashe_0.jpg",
                    "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Ashe_0.jpg"
                },
                ...
            ]
        },
        ...,
        "myTeam": [
            {
                "assignedPosition": "",
                "cellId": 0,
                "championId": 150,
                "championPickIntent": 0,
                "gameName": "KIT Matthew",
                "internalName": "",
                "isHumanoid": false,
                "nameVisibilityType": "",
                "obfuscatedPuuid": "",
                "obfuscatedSummonerId": 0,
                "pickMode": 0,
                "pickTurn": 0,
                "playerAlias": "",
                "playerType": "PLAYER",
                "puuid": "6d270db4-55b6-5848-ae1f-0b031c8c9d97",
                "selectedSkinId": 150000,
                "spell1Id": 6,
                "spell2Id": 4,
                "summonerId": 3809584301622336,
                "tagLine": "",
                "team": 1,
                "wardSkinId": -1,
                "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Gnar.png",
                "championPickIntentIcon": "",
                "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gnar_0.jpg",
                "championPickIntentSplash": "",
                "championIdSkinSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Gnar_0.jpg",
                "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Gnar_0.jpg",
                "championPickIntentLoading": "",
                "championIdSkinLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Gnar_0.jpg",
                "summonerSpell1Icon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/spell/SummonerHaste.png",
                "summonerSpell2Icon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/spell/SummonerFlash.png"
            },
            ...
        ],
        "theirTeam": [
            {
                "assignedPosition": "",
                "cellId": 5,
                "championId": 203,
                "championPickIntent": 0,
                "gameName": "UEB Milkshake",
                "internalName": "",
                "isHumanoid": false,
                "nameVisibilityType": "",
                "obfuscatedPuuid": "",
                "obfuscatedSummonerId": 0,
                "pickMode": 0,
                "pickTurn": 0,
                "playerAlias": "",
                "playerType": "PLAYER",
                "puuid": "18b72f40-0308-58e1-a694-000f62b57340",
                "selectedSkinId": 203000,
                "spell1Id": 21,
                "spell2Id": 3,
                "summonerId": 3809584303138112,
                "tagLine": "",
                "team": 2,
                "wardSkinId": -1,
                "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Kindred.png",
                "championPickIntentIcon": "",
                "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kindred_0.jpg",
                "championPickIntentSplash": "",
                "championIdSkinSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kindred_0.jpg",
                "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Kindred_0.jpg",
                "championPickIntentLoading": "",
                "championIdSkinLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Kindred_0.jpg",
                "summonerSpell1Icon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/spell/SummonerBarrier.png",
                "summonerSpell2Icon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/spell/SummonerExhaust.png"
            },
            ...
        ],
        "timer": {
            "adjustedTimeLeftInPhase": 2021,
            "internalNowInEpochMs": 1755180468516,
            "isInfinite": false,
            "phase": "FINALIZATION",
            "totalTimeInPhase": 62378
        },
        ...
   }

```

## Fearless
Enthält alle Champions, die vorher gepickt wurden. Wird in fearless.json gespeichert, kann gelöscht werden wenn ein neues BoX startet
```json
{
    ...,
    "fearless": [
        {
            "championId": 1,
            "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Annie.png",
            "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Annie_0.jpg",
            "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Annie_0.jpg"
        },
        {
            "championId": 53,
            "championIdIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Blitzcrank.png",
            "championIdSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Blitzcrank_0.jpg",
            "championIdLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Blitzcrank_0.jpg"
        },
        ...
    ]
}
```

## Examples
In `_recordtest.json` befindet sich der TR Testpickban.

## Issues
 - Skins und Summonerspells refreshen nicht die Session, werden also erst geändert sobald etwas anderes die Session refresht.
 - Ban Hovers werden nicht gezeigt.


# Live Client Data
Live Client Data wird von einer Rest API und dann alle x millisekunden über den websocket relay im selben Format wie die anderen Events gepublished. Folgende Daten sind verfügbar:
 - activePlayer: Beinhaltet Daten zum Spieler, der grade im Spectator ausgewählt ist. Not available in Replays? Aber in Live Spectator? Maybe auch nicht?
 - allPlayers: Beinhaltet Infos zu allen Spielern. Champion, Spielername, Items, Level, KDA, CS, Keystone Rune, Summoner Spell und noch ein paar andere Dinge. KEINE Ability Cooldowns
 - events: Beinhalte folgende Events: Champion Kill (inclusive assits), Turret Kill/Respawn, Inhib Kill/Respawn, AtakhanKill, Baron Kill, Multi Kill (ab 3 Kills?). KEIN!!! Dragon Kill. Gibt dazu keine Dokumentation, also evtl. mehr (Ace?, Soul?, Elder?, Herald?, Voidgrubs?)

 ## Ideen
 LED Wall/Licht:
 - Objectives: Baron, Atakhan, Soul Drake, Elder Drake auf LED Wall/Licht
 - Items: Legendary Item Buy auf LED Wall
 - Level: Level 6, 11, 16 auf LED Wall
 - Win

## Player
items und champions haben images. Runen und Summonerspells könnten das auch bekommen, if u want. Deathtimer können im relay über die `RESPWAN_TIMER_ADJUSTMENT_MS` Variable adjusted werden, um led wall delays zu kompensieren.
```json
{
    "championName": "Illaoi",
    "isBot": false,
    "isDead": true,
    "items": [
        {
        "canUse": false,
        "consumable": false,
        "count": 1,
        "displayName": "Iceborn Gauntlet",
        "itemID": 6662,
        "price": 800,
        "rawDescription": "GeneratedTip_Item_6662_Description",
        "rawDisplayName": "Item_6662_Name",
        "slot": 0,
        "itemIDIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/item/6662.png"
        },
        ...
    ],
    "level": 17,
    "position": "TOP",
    "rawChampionName": "game_character_displayname_Illaoi",
    "rawSkinName": "game_character_skin_displayname_Illaoi_0",
    "respawnTimer": 24.31493377685547,
    "riotId": "JustPaInKiLLer23#EUW",
    "riotIdGameName": "JustPaInKiLLer23",
    "riotIdTagLine": "EUW",
    "runes": {
        "keystone": {
        "displayName": "Conqueror",
        "id": 8010,
        "rawDescription": "perk_tooltip_Conqueror",
        "rawDisplayName": "perk_displayname_Conqueror"
        },
        "primaryRuneTree": {
        "displayName": "Precision",
        "id": 8000,
        "rawDescription": "perkstyle_tooltip_7201",
        "rawDisplayName": "perkstyle_displayname_7201"
        },
        "secondaryRuneTree": {
        "displayName": "Sorcery",
        "id": 8200,
        "rawDescription": "perkstyle_tooltip_7202",
        "rawDisplayName": "perkstyle_displayname_7202"
        }
    },
    "scores": {
        "assists": 6,
        "creepScore": 240,
        "deaths": 7,
        "kills": 7,
        "wardScore": 22.405691146850586
    },
    "screenPositionBottom": "340282346638528859811704183484516925440.0000000,340282346638528859811704183484516925440.0000000",
    "screenPositionCenter": "340282346638528859811704183484516925440.0000000,340282346638528859811704183484516925440.0000000",
    "skinID": 0,
    "skinName": "",
    "summonerName": "JustPaInKiLLer23#EUW",
    "summonerSpells": {
        "summonerSpellOne": {
        "displayName": "Flash",
        "rawDescription": "GeneratedTip_SummonerSpell_SummonerFlash_Description",
        "rawDisplayName": "GeneratedTip_SummonerSpell_SummonerFlash_DisplayName"
        },
        "summonerSpellTwo": {
        "displayName": "Unleashed Teleport",
        "rawDescription": "GeneratedTip_SummonerSpell_S12_SummonerTeleportUpgrade_Description",
        "rawDisplayName": "GeneratedTip_SummonerSpell_S12_SummonerTeleportUpgrade_DisplayName"
        }
    },
    "team": "ORDER",
    "championNameIcon": "https://ddragon.leagueoflegends.com/cdn/15.15.1/img/champion/Illaoi.png",
    "championNameSplash": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Illaoi_0.jpg",
    "championNameLoading": "https://ddragon.leagueoflegends.com/cdn/img/champion/loading/Illaoi_0.jpg"
}
```

## Event
 ```json
{
    "Assisters": [
    "Artayr",
    "Kulturbanause"
    ],
    "EventID": 55,
    "EventName": "ChampionKill",
    "EventTime": 1929.0242919921875,
    "KillerName": "Hunterzombie17",
    "VictimName": "Moerak"
}
 ```

# Postgame
See post-game.json. Items und Champions werden mit Image URLs versehen. Replayable via `_recordpostgame.json`
## Assets
- Stats: https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/statmods/ <br>
- Postgame: https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-postgame/global/default/<br>
- Runes: https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/
- Matchhistory: https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-match-history/global/default/
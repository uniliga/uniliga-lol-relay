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

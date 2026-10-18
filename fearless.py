import json
import os
import threading
import copy

import util

FEARLESS_FILE = 'fearless.json'
SESSION_URI = '/lol-champ-select/v1/session'

# Relay thread and API thread both touch fearless.json
_lock = threading.Lock()

# Last champ select event that was published, used to re-broadcast after manual edits
_last_session_event = None


def _read():
    if not os.path.exists(FEARLESS_FILE):
        return []
    with open(FEARLESS_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)


def _write(champions):
    with open(FEARLESS_FILE, 'w', encoding='utf-8') as file:
        json.dump(champions, file, indent=2, ensure_ascii=False)


def load():
    with _lock:
        return _read()


def merge_picks(current_picks):
    """Add the current draft's picks to fearless.json, return the list without the current picks"""
    with _lock:
        combined = util.fearless_unique(current_picks + _read())
        _write(combined)
    return util.fearless_remove_current(combined, current_picks)


def champion_entry(champion_id, cell_id=None):
    return {
        "cellId": cell_id,
        "championId": champion_id,
        "championIdIcon": util.id_to_url(champion_id, 'icon'),
        "championIdSplash": util.id_to_url(champion_id, 'splash'),
        "championIdLoading": util.id_to_url(champion_id, 'loading'),
    }


def add(champion_id):
    """Add a champion manually. Returns False if it is unknown or already in the list"""
    if str(champion_id) not in util.champions_lookup:
        raise KeyError(champion_id)
    with _lock:
        champions = _read()
        if any(c.get('championId') == champion_id for c in champions):
            return False
        champions.append(champion_entry(champion_id))
        _write(champions)
    return True


def remove(champion_id):
    with _lock:
        champions = _read()
        remaining = [c for c in champions if c.get('championId') != champion_id]
        _write(remaining)
    return len(remaining) != len(champions)


def reset():
    with _lock:
        _write([])


def all_champions():
    """All champions from the downloaded ddragon champion.json, sorted by name"""
    with open('champion.json', 'r', encoding='utf-8') as file:
        data = json.load(file)['data']
    champions = [
        {
            "championId": int(c['key']),
            "name": c['name'],
            "championIdIcon": util.id_to_url(int(c['key']), 'icon'),
        }
        for c in data.values()
    ]
    return sorted(champions, key=lambda c: c['name'])


def remember_event(event):
    """Called for every published event, keeps the last champ select session"""
    global _last_session_event
    if event.get('uri') == SESSION_URI:
        _last_session_event = event


def session_event_with_current_fearless():
    """Copy of the last champ select event with a recalculated fearless list, or None"""
    if _last_session_event is None:
        return None
    event = copy.deepcopy(_last_session_event)
    event.pop('timestamp', None)
    data = event.get('data', {})
    teams = (data.get('myTeam') or []) + (data.get('theirTeam') or [])
    current_picks = util.get_all_champions(data.get('actions') or [], teams)
    data['fearless'] = util.fearless_remove_current(load(), current_picks)
    return event

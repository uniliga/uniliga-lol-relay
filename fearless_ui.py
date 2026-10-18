# Producer UI for the fearless list, served at /fearless/ui.
# Kept as a Python module so PyInstaller bundles it without extra --add-data flags.

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fearless Steuerung</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #1e2328;
            color: #f0e6d2;
        }
        h1 { margin: 0; font-size: 24px; }
        h2 { margin: 0 0 12px; font-size: 18px; }
        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .container {
            background-color: #3c3c41;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        button {
            background-color: #c8aa6e;
            color: #1e2328;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background-color: #f0e6d2; }
        button.danger { background-color: #c0392b; color: #f0e6d2; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; }
        button.danger:hover { background-color: #e74c3c; }
        .count { color: #c8aa6e; font-weight: normal; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(84px, 1fr));
            gap: 10px;
        }
        .champ {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 6px;
            border-radius: 6px;
            background-color: #1e2328;
            border: 2px solid transparent;
            font-size: 12px;
            text-align: center;
            cursor: pointer;
        }
        .champ img { width: 64px; height: 64px; border-radius: 4px; display: block; }
        .board {
            display: grid;
            grid-template-columns: 70px repeat(5, minmax(0, 1fr));
            gap: 8px;
            align-items: stretch;
        }
        .board .role, .board .side {
            font-size: 13px;
            font-weight: bold;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .board .side.blue { color: #5aa0ff; }
        .board .side.red { color: #ff6b5b; }
        .slot {
            min-height: 92px;
            padding: 6px;
            border-radius: 6px;
            background-color: #1e2328;
            border: 2px solid #2b2f36;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-content: flex-start;
            cursor: pointer;
        }
        .slot.blue { border-color: #24456f; }
        .slot.red { border-color: #6b2620; }
        .slot.target { border-color: #c8aa6e; box-shadow: 0 0 0 2px #c8aa6e inset; }
        .slot.drop { background-color: #463714; }
        .slot .champ { padding: 2px; background: none; }
        .slot .champ img, .unassigned .champ img { width: 48px; height: 48px; }
        .unassigned {
            margin-top: 16px;
            padding: 10px;
            border: 2px dashed #c8aa6e;
            border-radius: 6px;
        }
        .unassigned p { margin: 0 0 8px; font-size: 13px; color: #c8aa6e; }
        .unassigned .list { display: flex; flex-wrap: wrap; gap: 6px; }
        .hint { font-size: 13px; color: #a09b8c; margin: 0 0 12px; }
        .target-label { color: #c8aa6e; }
        .champ[draggable=true] { cursor: grab; }
        .champ .remove {
            position: absolute;
            top: -4px;
            right: -4px;
            width: 20px;
            height: 20px;
            padding: 0;
            border-radius: 50%;
            background-color: #c0392b;
            color: #f0e6d2;
            font-size: 12px;
            line-height: 20px;
        }
        .champ .remove:hover { background-color: #e74c3c; }
        .result:hover { border-color: #c8aa6e; }
        .result.taken { opacity: 0.3; cursor: not-allowed; }
        .empty { grid-column: 1 / -1; color: #a09b8c; font-style: italic; }
        input[type=search] {
            width: 100%;
            padding: 10px 12px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #463714;
            background-color: #1e2328;
            color: #f0e6d2;
            margin-bottom: 12px;
        }
        #status {
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 14px;
            background-color: #463714;
        }
        #status.error { background-color: #c0392b; }
        #status.ok { background-color: #2e7d32; }
    </style>
</head>
<body>
    <header>
        <h1>Fearless</h1>
        <div id="status">Lade…</div>
    </header>

    <div class="container">
        <header>
            <h2>Gesperrte Champions <span class="count" id="count"></span></h2>
            <div class="actions">
                <button onclick="publishFearless()">Ans Overlay senden</button>
                <button class="danger" onclick="resetFearless()">Reset</button>
            </div>
        </header>
        <p class="hint">Aufbau wie im Overlay: Spalte = Rolle, Zeile = Team. Feld anklicken, um es als Ziel zum Hinzufügen zu wählen. Champions per Drag &amp; Drop in ein anderes Feld verschieben.</p>
        <div class="board" id="board"></div>
        <div class="unassigned" id="unassigned" hidden>
            <p>Ohne Zuordnung – im Overlay nicht sichtbar. In ein Feld ziehen, um sie zuzuordnen.</p>
            <div class="list" id="unassignedList"></div>
        </div>
    </div>

    <div class="container">
        <h2>Champion hinzufügen zu <span class="target-label" id="targetLabel"></span></h2>
        <input type="search" id="search" placeholder="Champion suchen… (Enter fügt den ersten Treffer hinzu)" autocomplete="off">
        <div class="grid" id="results"></div>
    </div>

    <script>
        const API = window.location.origin;
        let fearless = [];
        let champions = [];
        let targetCell = 0;
        let dragging = false;

        const ROLES = ['Top', 'Jgl', 'Mid', 'Bot', 'Supp'];

        // cellId = draft slot: 0-4 blue side, 5-9 red side, role = cellId % 5
        function slotName(cellId) {
            return `${cellId < 5 ? 'Blue' : 'Red'} ${ROLES[cellId % 5]}`;
        }

        function setStatus(text, kind = '') {
            const el = document.getElementById('status');
            el.textContent = text;
            el.className = kind;
        }

        function publishedText(published) {
            return published
                ? 'Gespeichert und ans Overlay gesendet'
                : 'Gespeichert – Overlay aktualisiert beim nächsten Champ Select Event';
        }

        async function request(method, path, body) {
            const options = { method, headers: {} };
            if (body) {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(body);
            }
            const response = await fetch(API + path, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || response.statusText);
            return data;
        }

        function nameFor(championId) {
            const champ = champions.find(c => c.championId === championId);
            return champ ? champ.name : String(championId);
        }

        function champTile(champ) {
            const el = document.createElement('div');
            el.className = 'champ';
            el.draggable = true;
            el.title = nameFor(champ.championId);
            el.innerHTML = `<img src="${champ.championIdIcon}" alt=""><button class="remove" title="Entfernen">✕</button>`;
            el.querySelector('.remove').onclick = event => {
                event.stopPropagation();
                removeChampion(champ.championId);
            };
            el.ondragstart = event => {
                dragging = true;
                event.dataTransfer.setData('text/plain', String(champ.championId));
            };
            el.ondragend = () => { dragging = false; };
            return el;
        }

        function slotElement(cellId) {
            const slot = document.createElement('div');
            slot.className = `slot ${cellId < 5 ? 'blue' : 'red'}${cellId === targetCell ? ' target' : ''}`;
            slot.title = `${slotName(cellId)} als Ziel wählen`;
            for (const champ of fearless.filter(c => c.cellId === cellId)) {
                slot.appendChild(champTile(champ));
            }
            slot.onclick = () => selectTarget(cellId);
            slot.ondragover = event => { event.preventDefault(); slot.classList.add('drop'); };
            slot.ondragleave = () => slot.classList.remove('drop');
            slot.ondrop = event => {
                event.preventDefault();
                slot.classList.remove('drop');
                dragging = false;
                moveChampion(Number(event.dataTransfer.getData('text/plain')), cellId);
            };
            return slot;
        }

        function renderFearless() {
            document.getElementById('count').textContent = `(${fearless.length})`;
            document.getElementById('targetLabel').textContent = slotName(targetCell);

            const board = document.getElementById('board');
            board.innerHTML = '<div></div>';
            for (const role of ROLES) {
                const el = document.createElement('div');
                el.className = 'role';
                el.textContent = role;
                board.appendChild(el);
            }
            for (const [side, offset] of [['blue', 0], ['red', 5]]) {
                const label = document.createElement('div');
                label.className = `side ${side}`;
                label.textContent = side;
                board.appendChild(label);
                for (let role = 0; role < 5; role++) {
                    board.appendChild(slotElement(offset + role));
                }
            }

            // Entries without a valid slot (old fearless.json) never show up in the overlay
            const unassigned = fearless.filter(c => typeof c.cellId !== 'number' || c.cellId < 0 || c.cellId > 9);
            const list = document.getElementById('unassignedList');
            list.innerHTML = '';
            unassigned.forEach(champ => list.appendChild(champTile(champ)));
            document.getElementById('unassigned').hidden = unassigned.length === 0;
        }

        function selectTarget(cellId) {
            targetCell = cellId;
            renderFearless();
            renderResults();
            document.getElementById('search').focus();
        }

        function searchMatches() {
            const query = document.getElementById('search').value.trim().toLowerCase();
            if (!query) return [];
            return champions.filter(c => c.name.toLowerCase().includes(query));
        }

        function renderResults() {
            const grid = document.getElementById('results');
            grid.innerHTML = '';
            const takenIds = new Set(fearless.map(c => c.championId));
            for (const champ of searchMatches()) {
                const taken = takenIds.has(champ.championId);
                const el = document.createElement('div');
                el.className = `champ result${taken ? ' taken' : ''}`;
                el.title = taken ? 'Bereits gesperrt' : `${champ.name} zu ${slotName(targetCell)} hinzufügen`;
                el.innerHTML = `<img src="${champ.championIdIcon}" alt=""><span></span>`;
                el.querySelector('span').textContent = champ.name;
                if (!taken) el.onclick = () => addChampion(champ.championId);
                grid.appendChild(el);
            }
        }

        function apply(data) {
            fearless = data.fearless;
            renderFearless();
            renderResults();
        }

        async function refresh() {
            // Re-rendering mid drag would cancel it
            if (dragging) return;
            try {
                apply(await request('GET', '/fearless'));
                if (document.getElementById('status').className === 'error') setStatus('Verbunden');
            } catch (e) {
                setStatus(`Keine Verbindung zur API: ${e.message}`, 'error');
            }
        }

        async function addChampion(championId) {
            try {
                const data = await request('POST', '/fearless', { championId, cellId: targetCell });
                apply(data);
                setStatus(`${nameFor(championId)} zu ${slotName(targetCell)} hinzugefügt. ${publishedText(data.published)}`, 'ok');
                const search = document.getElementById('search');
                search.value = '';
                search.focus();
                renderResults();
            } catch (e) {
                setStatus(`Fehler: ${e.message}`, 'error');
            }
        }

        async function removeChampion(championId) {
            try {
                const data = await request('DELETE', `/fearless/${championId}`);
                apply(data);
                setStatus(`${nameFor(championId)} entfernt. ${publishedText(data.published)}`, 'ok');
            } catch (e) {
                setStatus(`Fehler: ${e.message}`, 'error');
            }
        }

        async function moveChampion(championId, cellId) {
            if (fearless.some(c => c.championId === championId && c.cellId === cellId)) return;
            try {
                const data = await request('PATCH', `/fearless/${championId}`, { cellId });
                apply(data);
                setStatus(`${nameFor(championId)} nach ${slotName(cellId)} verschoben. ${publishedText(data.published)}`, 'ok');
            } catch (e) {
                setStatus(`Fehler: ${e.message}`, 'error');
            }
        }

        async function publishFearless() {
            try {
                const data = await request('POST', '/fearless/publish');
                apply(data);
                setStatus(data.manual
                    ? 'Ans Overlay gesendet (ohne Champ Select, leerer Draft)'
                    : 'Ans Overlay gesendet (letztes Champ Select Event)', 'ok');
            } catch (e) {
                setStatus(`Fehler: ${e.message}`, 'error');
            }
        }

        async function resetFearless() {
            if (!confirm('Reset?')) return;
            try {
                const data = await request('DELETE', '/fearless');
                apply(data);
                setStatus(`Fearless zurückgesetzt. ${publishedText(data.published)}`, 'ok');
            } catch (e) {
                setStatus(`Fehler: ${e.message}`, 'error');
            }
        }

        document.getElementById('search').addEventListener('input', renderResults);
        document.getElementById('search').addEventListener('keydown', event => {
            if (event.key !== 'Enter') return;
            const takenIds = new Set(fearless.map(c => c.championId));
            const first = searchMatches().find(c => !takenIds.has(c.championId));
            if (first) addChampion(first.championId);
        });

        async function init() {
            try {
                champions = (await request('GET', '/fearless/champions')).champions;
                setStatus('Verbunden');
            } catch (e) {
                setStatus(`Keine Verbindung zur API: ${e.message}`, 'error');
            }
            await refresh();
            // Picks from the client land in fearless.json automatically, keep the view in sync
            setInterval(refresh, 3000);
        }

        init();
    </script>
</body>
</html>
"""

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
        .champ.blue { border-color: #2f80ed; }
        .champ.red { border-color: #c0392b; }
        .champ.manual { border-color: #c8aa6e; border-style: dashed; }
        .champ .remove {
            position: absolute;
            top: 2px;
            right: 2px;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background-color: #c0392b;
            color: #f0e6d2;
            font-size: 14px;
            line-height: 22px;
        }
        .champ:hover .remove { background-color: #e74c3c; }
        .result:hover { border-color: #c8aa6e; }
        .result.taken { opacity: 0.3; cursor: not-allowed; }
        .legend { display: flex; gap: 16px; font-size: 12px; margin-top: 12px; flex-wrap: wrap; }
        .legend span::before {
            content: '';
            display: inline-block;
            width: 10px;
            height: 10px;
            margin-right: 6px;
            border: 2px solid;
            border-radius: 2px;
            vertical-align: -1px;
        }
        .legend .l-blue::before { border-color: #2f80ed; }
        .legend .l-red::before { border-color: #c0392b; }
        .legend .l-manual::before { border-color: #c8aa6e; border-style: dashed; }
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
        <h1>Fearless Steuerung</h1>
        <div id="status">Lade…</div>
    </header>

    <div class="container">
        <header>
            <h2>Gesperrte Champions <span class="count" id="count"></span></h2>
            <button class="danger" onclick="resetFearless()">Neue Serie / Reset</button>
        </header>
        <div class="grid" id="fearless"></div>
        <div class="legend">
            <span class="l-blue">Blue Side Pick</span>
            <span class="l-red">Red Side Pick</span>
            <span class="l-manual">Manuell hinzugefügt</span>
        </div>
    </div>

    <div class="container">
        <h2>Champion hinzufügen</h2>
        <input type="search" id="search" placeholder="Champion suchen… (Enter fügt den ersten Treffer hinzu)" autocomplete="off">
        <div class="grid" id="results"></div>
    </div>

    <script>
        const API = window.location.origin;
        let fearless = [];
        let champions = [];

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

        function sideClass(cellId) {
            if (cellId === null || cellId === undefined) return 'manual';
            return cellId < 5 ? 'blue' : 'red';
        }

        function renderFearless() {
            const grid = document.getElementById('fearless');
            document.getElementById('count').textContent = `(${fearless.length})`;
            grid.innerHTML = '';
            if (fearless.length === 0) {
                grid.innerHTML = '<div class="empty">Noch keine Champions gesperrt.</div>';
                return;
            }
            for (const champ of fearless) {
                const el = document.createElement('div');
                el.className = `champ ${sideClass(champ.cellId)}`;
                el.title = `${nameFor(champ.championId)} entfernen`;
                el.innerHTML = `<img src="${champ.championIdIcon}" alt=""><span></span><div class="remove">✕</div>`;
                el.querySelector('span').textContent = nameFor(champ.championId);
                el.onclick = () => removeChampion(champ.championId);
                grid.appendChild(el);
            }
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
                el.title = taken ? 'Bereits gesperrt' : `${champ.name} hinzufügen`;
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
            try {
                apply(await request('GET', '/fearless'));
                if (document.getElementById('status').className === 'error') setStatus('Verbunden');
            } catch (e) {
                setStatus(`Keine Verbindung zur API: ${e.message}`, 'error');
            }
        }

        async function addChampion(championId) {
            try {
                const data = await request('POST', '/fearless', { championId });
                apply(data);
                setStatus(`${nameFor(championId)} hinzugefügt. ${publishedText(data.published)}`, 'ok');
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

        async function resetFearless() {
            if (!confirm('Alle gesperrten Champions löschen und eine neue Serie starten?')) return;
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

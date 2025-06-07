const statusEl = document.getElementById('status');
const logEl = document.getElementById('log');
const matchBtn = document.getElementById('matchBtn');

const params = new URLSearchParams(window.location.search);
const playerId = params.get('player_id') || Math.random().toString(36).slice(2);

function addLog(msg) {
  const li = document.createElement('li');
  li.textContent = msg;
  logEl.appendChild(li);
}

const ws = new WebSocket(`ws://${window.location.host}/ws/${playerId}`);
ws.onopen = () => statusEl.textContent = 'Connected';
ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    if (data.event === 'matched') {
      statusEl.textContent = `Matched with ${data.opponent}`;
    } else if (data.event === 'message') {
      addLog(`${data.from}: ${data.data}`);
    }
  } catch (e) {
    console.error(e);
  }
};
ws.onclose = () => statusEl.textContent = 'Disconnected';

matchBtn.addEventListener('click', () => {
  fetch('/matchmake', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId })
  })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'waiting') {
        statusEl.textContent = 'Waiting for opponent...';
      } else if (data.status === 'matched') {
        statusEl.textContent = `Matched with ${data.opponent}`;
      }
    })
    .catch(err => console.error(err));
});

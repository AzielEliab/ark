/* ARK UI. No CDN. No telemetry. Never logs the phrase. */
(function () {
  const phraseEl = document.getElementById("phrase");
  const levelEl = document.getElementById("level");
  const statusEl = document.getElementById("status");
  const entriesEl = document.getElementById("entries");
  const sweepOut = document.getElementById("sweep-out");

  function setStatus(text, cls) {
    statusEl.className = "band " + (cls || "idle");
    statusEl.textContent = text;
  }

  async function refreshList() {
    const resp = await fetch("/api/list");
    if (resp.status === 401) {
      entriesEl.innerHTML = "";
      return;
    }
    const payload = await resp.json();
    entriesEl.innerHTML = "";
    const rows = payload.entries || [];
    if (!rows.length) {
      const li = document.createElement("li");
      li.textContent = "(empty vault — wrong phrase also looks like this)";
      entriesEl.appendChild(li);
      return;
    }
    rows.forEach(function (row) {
      const li = document.createElement("li");
      const left = document.createElement("span");
      const code = document.createElement("span");
      code.className = "code";
      code.textContent = row.id.slice(0, 8);
      left.appendChild(code);
      left.appendChild(document.createTextNode(row.name));
      const a = document.createElement("a");
      a.href = "/api/get?id=" + encodeURIComponent(row.id);
      a.textContent = "download";
      li.appendChild(left);
      li.appendChild(a);
      entriesEl.appendChild(li);
    });
  }

  document.getElementById("unlock-form").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    const phrase = phraseEl.value;
    const level = levelEl.value;
    phraseEl.value = "";
    const resp = await fetch("/api/unlock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phrase: phrase, level: level }),
    });
    const payload = await resp.json();
    if (!resp.ok) {
      setStatus(payload.error || "Unlock/decrypt failed.", "fail");
      return;
    }
    setStatus("Opened vault " + payload.vault + "…  (" + payload.level + "). Wrong phrase = different empty vault.", "open");
    await refreshList();
  });

  document.getElementById("lock").addEventListener("click", async function () {
    await fetch("/api/lock", { method: "POST" });
    entriesEl.innerHTML = "";
    setStatus("Locked. Keys zeroized.", "idle");
  });

  document.getElementById("upload").addEventListener("change", async function (ev) {
    const file = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file, file.name);
    const resp = await fetch("/api/put", { method: "POST", body: body });
    const payload = await resp.json();
    if (!resp.ok) {
      setStatus(payload.error || "ARK blocked file (Mode E)", "fail");
      return;
    }
    setStatus("Encrypted " + payload.name, "open");
    await refreshList();
  });

  document.getElementById("sweep").addEventListener("change", async function (ev) {
    const file = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file, file.name);
    const resp = await fetch("/api/sweep", { method: "POST", body: body });
    const payload = await resp.json();
    if (payload.flagged) {
      sweepOut.textContent = "Mode E flagged: " + (payload.findings || []).map(function (f) { return f.detail; }).join("; ");
    } else {
      sweepOut.textContent = "Mode E clean. Payload was not stored.";
    }
  });
})();

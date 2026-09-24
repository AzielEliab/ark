/* ARK UI. No CDN. No telemetry. Never logs the phrase. */
(function () {
  const phraseEl = document.getElementById("phrase");
  const levelEl = document.getElementById("level");
  const statusEl = document.getElementById("status");
  const entriesEl = document.getElementById("entries");
  const emptyEl = document.getElementById("empty");
  const sweepOut = document.getElementById("sweep-out");
  const gateEl = document.getElementById("gate");
  const filesEl = document.getElementById("files");

  function setStatus(text, cls) {
    statusEl.className = "status " + (cls || "idle");
    statusEl.textContent = text;
  }

  function showVault(open) {
    gateEl.hidden = open;
    filesEl.hidden = !open;
  }

  async function readJson(resp) {
    try {
      return await resp.json();
    } catch (err) {
      return {};
    }
  }

  async function refreshList() {
    const resp = await fetch("/api/list");
    if (resp.status === 401) {
      entriesEl.innerHTML = "";
      emptyEl.hidden = false;
      showVault(false);
      setStatus("Locked", "idle");
      return;
    }
    const payload = await readJson(resp);
    entriesEl.innerHTML = "";
    const rows = payload.entries || [];
    emptyEl.hidden = rows.length > 0;
    rows.forEach(function (row) {
      const li = document.createElement("li");
      const name = document.createElement("span");
      name.className = "name";
      name.textContent = row.name || "Untitled";
      const link = document.createElement("a");
      link.href = "/api/get?id=" + encodeURIComponent(row.id);
      link.textContent = "Download";
      li.appendChild(name);
      li.appendChild(link);
      entriesEl.appendChild(li);
    });
  }

  document.getElementById("unlock-form").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    const phrase = phraseEl.value;
    const level = levelEl.value;
    phraseEl.value = "";
    if (!phrase) {
      setStatus("A phrase is required. Type one, then choose Open vault.", "fail");
      return;
    }
    setStatus("Opening…", "idle");
    try {
      const resp = await fetch("/api/unlock", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phrase: phrase, level: level }),
      });
      const payload = await readJson(resp);
      if (!resp.ok) {
        setStatus((payload.error || "Unlock/decrypt failed.") + " Try the phrase again.", "fail");
        return;
      }
      setStatus("Vault open", "open");
      showVault(true);
      await refreshList();
    } catch (err) {
      setStatus("Could not reach the vault on this computer. Run ark ui, then try again.", "fail");
    }
  });

  document.getElementById("lock").addEventListener("click", async function () {
    try {
      await fetch("/api/lock", { method: "POST" });
    } catch (err) {
      setStatus("Could not reach the vault on this computer. Run ark ui, then try again.", "fail");
      return;
    }
    entriesEl.innerHTML = "";
    emptyEl.hidden = false;
    showVault(false);
    const advanced = document.getElementById("advanced");
    if (advanced) advanced.open = false;
    setStatus("Locked", "idle");
    phraseEl.focus();
  });

  document.getElementById("add-file").addEventListener("click", function () {
    document.getElementById("upload").click();
  });

  document.getElementById("upload").addEventListener("change", async function (ev) {
    const file = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file, file.name);
    try {
      const resp = await fetch("/api/put", { method: "POST", body: body });
      const payload = await readJson(resp);
      if (resp.status === 401) {
        setStatus("Open the vault first, then add a file.", "fail");
        showVault(false);
        return;
      }
      if (!resp.ok) {
        setStatus(payload.error || "This file was not stored.", "fail");
        return;
      }
      setStatus("Stored " + (payload.name || "file"), "open");
      await refreshList();
    } catch (err) {
      setStatus("Could not reach the vault on this computer. Run ark ui, then try again.", "fail");
    }
  });

  document.getElementById("check-file").addEventListener("click", function () {
    document.getElementById("sweep").click();
  });

  document.getElementById("sweep").addEventListener("change", async function (ev) {
    const file = ev.target.files && ev.target.files[0];
    ev.target.value = "";
    if (!file) return;
    const body = new FormData();
    body.append("file", file, file.name);
    try {
      const resp = await fetch("/api/sweep", { method: "POST", body: body });
      const payload = await readJson(resp);
      if (payload.flagged) {
        const details = (payload.findings || []).map(function (item) { return item.detail; }).join("; ");
        sweepOut.textContent = "Blocked. This file was not stored." + (details ? " " + details : "");
      } else {
        sweepOut.textContent = "Clean. Nothing was stored.";
      }
    } catch (err) {
      sweepOut.textContent = "Could not check that file. Run ark ui, then try again.";
    }
  });

  const file = document.getElementById("aziel-import-json");
  const imp = document.getElementById("aziel-import-json-btn");
  const exp = document.getElementById("aziel-export-json-btn");
  const jsonStatus = document.getElementById("aziel-json-status");

  function say(message) {
    if (jsonStatus) jsonStatus.textContent = message;
  }

  function collect() {
    const data = { product: document.title || "", exported_at: new Date().toISOString(), author: "Aziel Eliab" };
    document.querySelectorAll("input, select, textarea").forEach(function (el) {
      if (!el.id || el.type === "file" || el.type === "password") return;
      data[el.id] = el.type === "checkbox" ? el.checked : el.value;
    });
    if (window.__azielLastJson && typeof window.__azielLastJson === "object") {
      data.last = window.__azielLastJson;
    }
    return data;
  }

  function apply(obj) {
    if (!obj || typeof obj !== "object") return;
    window.__azielLastJson = obj;
    Object.keys(obj).forEach(function (key) {
      if (key === "last" || key === "product" || key === "exported_at" || key === "author") return;
      const el = document.getElementById(key);
      if (!el || el.type === "file" || el.type === "password") return;
      if (el.type === "checkbox") el.checked = !!obj[key];
      else if ("value" in el) el.value = obj[key];
    });
  }

  if (file && imp && exp) {
    imp.addEventListener("click", function () { file.click(); });
    file.addEventListener("change", function () {
      const chosen = file.files && file.files[0];
      if (!chosen) return;
      const reader = new FileReader();
      reader.onload = function () {
        try {
          apply(JSON.parse(String(reader.result || "{}")));
          say("Imported " + chosen.name);
        } catch (err) {
          say("That file is not JSON. Choose a .json file saved from Export JSON.");
        }
      };
      reader.readAsText(chosen);
    });
    exp.addEventListener("click", function () {
      const blob = new Blob([JSON.stringify(collect(), null, 2)], { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "session.json";
      link.click();
      setTimeout(function () { URL.revokeObjectURL(link.href); }, 800);
      say("Exported JSON");
    });
  }
})();

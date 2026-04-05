(function () {
  const repoEl = document.getElementById("repo");
  const tokenEl = document.getElementById("token");
  const branchEl = document.getElementById("branch");
  const inputEl = document.getElementById("selectedJson");
  const outputEl = document.getElementById("outputJson");
  const cfgStatus = document.getElementById("cfgStatus");
  const runStatus = document.getElementById("runStatus");

  function setStatus(el, cls, text) {
    el.className = cls;
    el.textContent = text;
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function toSession(items) {
    return {
      session_id: crypto.randomUUID(),
      created_at: nowIso(),
      processed: false,
      items: items.map((item) => ({
        id: item.id,
        filename: item.filename || `photo_${item.id}.jpg`,
        description: item.description || null,
        baseUrl: item.baseUrl || null,
        creationTime: item.creationTime || null,
        status: "selected",
        processed_at: null,
      })),
    };
  }

  function parseInput() {
    let parsed;
    try {
      parsed = JSON.parse(inputEl.value || "[]");
    } catch (err) {
      throw new Error(`Invalid JSON: ${err.message}`);
    }
    if (!Array.isArray(parsed)) {
      throw new Error("Input must be a JSON array of selected media items.");
    }
    const valid = parsed.filter((x) => x && typeof x.id === "string" && x.id.length > 0);
    if (!valid.length) {
      throw new Error("No valid selected items found (expected objects with string id).");
    }
    return valid;
  }

  function buildSelectedPhotosDoc() {
    const items = parseInput();
    return {
      schema_version: 1,
      last_updated: nowIso(),
      sessions: [toSession(items)],
    };
  }

  function cfgKey() {
    return "oio-picker-config";
  }

  document.getElementById("saveConfig").addEventListener("click", () => {
    localStorage.setItem(
      cfgKey(),
      JSON.stringify({ repo: repoEl.value.trim(), token: tokenEl.value.trim(), branch: branchEl.value.trim() || "main" })
    );
    setStatus(cfgStatus, "ok", "Config saved locally.");
  });

  document.getElementById("loadConfig").addEventListener("click", () => {
    const raw = localStorage.getItem(cfgKey());
    if (!raw) {
      setStatus(cfgStatus, "warn", "No saved config found.");
      return;
    }
    const cfg = JSON.parse(raw);
    repoEl.value = cfg.repo || "";
    tokenEl.value = cfg.token || "";
    branchEl.value = cfg.branch || "main";
    setStatus(cfgStatus, "ok", "Config loaded.");
  });

  document.getElementById("previewBtn").addEventListener("click", () => {
    try {
      const doc = buildSelectedPhotosDoc();
      outputEl.value = JSON.stringify(doc, null, 2);
      setStatus(runStatus, "ok", `Prepared ${doc.sessions[0].items.length} selected item(s).`);
    } catch (err) {
      setStatus(runStatus, "error", err.message);
    }
  });

  document.getElementById("downloadBtn").addEventListener("click", () => {
    try {
      const doc = buildSelectedPhotosDoc();
      outputEl.value = JSON.stringify(doc, null, 2);
      const blob = new Blob([`${JSON.stringify(doc, null, 2)}\n`], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "selected-photos.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus(runStatus, "ok", "Downloaded selected-photos.json.");
    } catch (err) {
      setStatus(runStatus, "error", err.message);
    }
  });

  document.getElementById("commitBtn").addEventListener("click", async () => {
    const repo = repoEl.value.trim();
    const token = tokenEl.value.trim();
    const branch = branchEl.value.trim() || "main";
    if (!repo || !token) {
      setStatus(runStatus, "error", "Repo and token are required for GitHub commit.");
      return;
    }

    try {
      const doc = buildSelectedPhotosDoc();
      outputEl.value = JSON.stringify(doc, null, 2);
      const [owner, repoName] = repo.split("/");
      if (!owner || !repoName) {
        throw new Error("Repo must be in owner/repo format.");
      }

      const path = "intake/selected-photos.json";
      const base = `https://api.github.com/repos/${owner}/${repoName}/contents/${path}`;
      const headers = {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      };

      const getResp = await fetch(`${base}?ref=${encodeURIComponent(branch)}`, { headers });
      let sha = undefined;
      if (getResp.status === 200) {
        const body = await getResp.json();
        sha = body.sha;
      } else if (getResp.status !== 404) {
        const text = await getResp.text();
        throw new Error(`GitHub read failed (${getResp.status}): ${text}`);
      }

      const commitBody = {
        message: "chore(intake): add picker-selected photos",
        content: btoa(unescape(encodeURIComponent(`${JSON.stringify(doc, null, 2)}\n`))),
        branch,
        sha,
      };

      const putResp = await fetch(base, { method: "PUT", headers, body: JSON.stringify(commitBody) });
      if (!putResp.ok) {
        const text = await putResp.text();
        throw new Error(`GitHub commit failed (${putResp.status}): ${text}`);
      }
      const result = await putResp.json();
      setStatus(runStatus, "ok", `Committed selected photos: ${result.commit.sha.slice(0, 7)} on ${branch}`);
    } catch (err) {
      setStatus(runStatus, "error", err.message);
    }
  });
})();

const getElement = id => document.getElementById(id);

const app = getElement("app");
const url = getElement("url");
const go = getElement("go");
const statusEl = getElement("status");
const result = getElement("result");
const preview = getElement("preview");
const filename = getElement("filename");
const download = getElement("download");
const install = getElement("install");

let audioURL = null;

async function convert() {
  const link = url.value.trim();

  if (!link) {
    statusEl.className = "err";
    statusEl.textContent = "Paste a link first.";
    return;
  }

  go.disabled = true;
  go.textContent = "Converting…";
  statusEl.className = "";
  statusEl.textContent = "";
  result.hidden = true;

  try {
    const res = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: link })
    });

    if (!res.ok) {
      throw new Error(
        (await res.json().catch(() => ({}))).error || "Conversion failed."
      );
    }

    const name = decodeURIComponent(
      res.headers.get("X-Filename") || "audio.mp3"
    );

    if (audioURL) URL.revokeObjectURL(audioURL);

    const blob = await res.blob();
    audioURL = URL.createObjectURL(blob);

    preview.src = audioURL;
    filename.textContent = name;
    download.href = audioURL;
    download.download = name;

    result.hidden = false;
    statusEl.textContent = "";
    url.value = "";

  } catch (e) {
    statusEl.className = "err";
    statusEl.textContent = e.message;
  } finally {
    go.disabled = false;
    go.textContent = "Convert";
  }
}

go.addEventListener("click", convert);

url.addEventListener("keydown", e => {
  if (e.key === "Enter") convert();
});

let prompt;

addEventListener("beforeinstallprompt", e => {
  e.preventDefault();
  prompt = e;
  install.hidden = false;
});

install.addEventListener("click", async () => {
  if (!prompt) return;
  await prompt.prompt();
  prompt = null;
  install.hidden = true;
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}
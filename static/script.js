


// === Выбор блока, ряда, магазина ===
function loadRows() {
  const block = document.getElementById("block").value;
  const rowSel = document.getElementById("row");
  const shopSel = document.getElementById("store");
  rowSel.innerHTML = `<option value="">Выберите ряд</option>`;
  shopSel.innerHTML = `<option value="">Выберите магазин</option>`;
  rowSel.disabled = true;
  shopSel.disabled = true;

  if (!block) return;

  fetch(`/get_rows/${encodeURIComponent(block)}`)
    .then(res => res.json())
    .then(data => {
      if (data.type === "shops") {
        shopSel.innerHTML = `<option value="">Выберите магазин</option>` +
          data.items.map(s => `<option value="${s}">${s}</option>`).join("");
        shopSel.disabled = false;
      } else {
        rowSel.innerHTML = `<option value="">Выберите ряд</option>` +
          data.items.map(r => `<option value="${r}">${r}</option>`).join("");
        rowSel.disabled = false;
      }
    });
}

function loadStores() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value;
  const shopSel = document.getElementById("store");

  shopSel.innerHTML = `<option value="">Выберите магазин</option>`;
  shopSel.disabled = true;

  if (!block || !row) return;

  fetch(`/get_stores/${encodeURIComponent(block)}/${encodeURIComponent(row)}`)
    .then(res => res.json())
    .then(data => {
      shopSel.innerHTML = `<option value="">Выберите магазин</option>` +
        data.items.map(s => `<option value="${s}">${s}</option>`).join("");
      shopSel.disabled = false;
    });
}

function getPath() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value || "None";
  const shop = document.getElementById("store").value;
  if (!block || !shop) return;
  fetch(`/get_path/${encodeURIComponent(block)}/${encodeURIComponent(row)}/${encodeURIComponent(shop)}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("pathResult").innerHTML = data.path
        ? `<b>${data.path}</b>`
        : `<span class='error'>${data.error}</span>`;
    });
}

// === 🔽 Кнопка "Скрыть блоки" ===
document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("toggle-btn");
  const container = document.querySelector(".container");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      container.classList.toggle("hidden-block");
      toggleBtn.textContent = container.classList.contains("hidden-block")
        ? "Показать блоки"
        : "Скрыть блоки";
    });
  }

  // === 🌍 Переключение языка ===
  const langSelect = document.getElementById("languageSelect");
  if (langSelect) {
    langSelect.addEventListener("change", () => {
      const lang = langSelect.value;
      window.location.href = `/set_language/${lang}`;
    });
  }
});

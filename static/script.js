// переключение языка
document.addEventListener("DOMContentLoaded", () => {
  const langSelect = document.getElementById("languageSelect");
  if (langSelect) {
    langSelect.addEventListener("change", () => {
      const lang = langSelect.value;
      window.location.href = "/set_language/" + lang;
    });
  }

  // toggle hide/show
  const btn = document.getElementById("toggle-btn");
  const container = document.getElementById("blocks-container");
  if (btn && container) {
    const hideText = btn.dataset.hide || "Скрыть блоки";
    const showText = btn.dataset.show || "Показать блоки";
    // начально: если контейнер видим, ставим hideText
    btn.textContent =
      window.getComputedStyle(container).display === "none"
        ? showText
        : hideText;

    btn.addEventListener("click", () => {
      if (
        container.style.display === "none" ||
        window.getComputedStyle(container).display === "none"
      ) {
        container.style.display = "block";
        btn.textContent = hideText;
      } else {
        container.style.display = "none";
        btn.textContent = showText;
      }
    });
  }
});

// загрузка рядов / магазинов
function loadRows() {
  const block = document.getElementById("block").value;
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");

  rowSelect.innerHTML = `<option value="">${
    gettext ? gettext("Выберите ряд") : "Выберите ряд"
  }</option>`;
  storeSelect.innerHTML = `<option value="">${
    gettext ? gettext("Выберите магазин") : "Выберите магазин"
  }</option>`;
  rowSelect.disabled = true;
  storeSelect.disabled = true;

  if (!block) return;

  fetch(`/get_rows/${encodeURIComponent(block)}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.type === "shops") {
        // сразу магазины
        storeSelect.innerHTML = `<option value="">${
          gettext ? gettext("Выберите магазин") : "Выберите магазин"
        }</option>`;
        data.items.forEach((shop) => {
          const opt = document.createElement("option");
          opt.value = shop;
          opt.textContent = shop;
          storeSelect.appendChild(opt);
        });
        storeSelect.disabled = false;
      } else {
        // ряды
        rowSelect.innerHTML = `<option value="">${
          gettext ? gettext("Выберите ряд") : "Выберите ряд"
        }</option>`;
        data.items.forEach((r) => {
          const opt = document.createElement("option");
          opt.value = r;
          opt.textContent = r;
          rowSelect.appendChild(opt);
        });
        rowSelect.disabled = false;
      }
    })
    .catch((err) => {
      console.error("loadRows error:", err);
    });
}

function loadStores() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value;
  const storeSelect = document.getElementById("store");

  storeSelect.innerHTML = `<option value="">${
    gettext ? gettext("Выберите магазин") : "Выберите магазин"
  }</option>`;
  storeSelect.disabled = true;

  if (!block) return;

  fetch(`/get_stores/${encodeURIComponent(block)}/${encodeURIComponent(row)}`)
    .then((res) => res.json())
    .then((data) => {
      storeSelect.innerHTML = `<option value="">${
        gettext ? gettext("Выберите магазин") : "Выберите магазин"
      }</option>`;
      (data.items || []).forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s;
        opt.textContent = s;
        storeSelect.appendChild(opt);
      });
      storeSelect.disabled = false;
    })
    .catch((err) => console.error("loadStores error:", err));
}

function getPath() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value || "None";
  const shop = document.getElementById("store").value;
  if (!block || !shop) return;

  fetch(
    `/get_path/${encodeURIComponent(block)}/${encodeURIComponent(
      row
    )}/${encodeURIComponent(shop)}`
  )
    .then((res) => res.json())
    .then((data) => {
      const pr = document.getElementById("pathResult");
      if (data.path) {
        pr.innerHTML = `<div class="path-box">${data.path}</div>`;
      } else if (data.error) {
        pr.innerHTML = `<div class="error">${data.error}</div>`;
      } else {
        pr.innerHTML = "";
      }
    })
    .catch((err) => console.error("getPath error:", err));
}

// helper для локализации placeholder если gettext не доступен на клиенте
function gettext(s) {
  return s;
}

// AJAX-поиск формы
function doSearch(e) {
  e.preventDefault();
  const kw = document.getElementById("keyword").value.trim();
  if (!kw) return false;
  fetch(`/search?keyword=${encodeURIComponent(kw)}`)
    .then((res) => res.json())
    .then((data) => {
      const out = document.getElementById("search-results");
      if (data.error) {
        out.innerHTML = `<div class="error">${data.error}</div>`;
        return;
      }
      const arr = data.results || [];
      if (!arr.length) {
        out.innerHTML = `<div class="error">${gettext(
          "Ничего не найдено"
        )}</div>`;
        return;
      }
      out.innerHTML = "<pre>" + arr.join("\n") + "</pre>";
    })
    .catch((err) => console.error("search error:", err));
  return false;
}

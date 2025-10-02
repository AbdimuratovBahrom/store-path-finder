// выбор языка
document
  .getElementById("languageSelect")
  .addEventListener("change", function () {
    const lang = this.value;
    window.location.href = "/set_language/" + lang;
  });

// скрыть / показать блоки

  function toggleBlocks() {
    const container = document.getElementById("blocks-container");
    const btn = document.getElementById("toggle-btn");

    const hideText = btn.getAttribute("data-hide");
    const showText = btn.getAttribute("data-show");

    if (container.style.display === "none") {
      container.style.display = "block";
      btn.textContent = hideText;
    } else {
      container.style.display = "none";
      btn.textContent = showText;
    }
  }


  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("toggle-btn");
    const container = document.getElementById("blocks-container");
    if (!btn || !container) return;

    // прочитаем переводы, подставленные Jinja в data-атрибуты
    const hideText = btn.dataset.hide || "Скрыть блоки";
    const showText = btn.dataset.show || "Показать блоки";

    // функция проверки видимости: смотрим класс или computed style
    function isHidden() {
      return (
        container.classList.contains("hidden") ||
        window.getComputedStyle(container).display === "none"
      );
    }

    // установим начальный текст кнопки по текущему состоянию контейнера
    btn.textContent = isHidden() ? showText : hideText;
    btn.setAttribute("aria-expanded", String(!isHidden()));

    // навесим слушатель клика (лучше, чем inline onclick)
    btn.addEventListener("click", function () {
      const nowHidden = container.classList.toggle("hidden");
      btn.textContent = nowHidden ? showText : hideText;
      btn.setAttribute("aria-expanded", String(!nowHidden));
    });
  });




// загрузка рядов или магазинов
function loadRows() {
  const block = document.getElementById("block").value;
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");

  rowSelect.innerHTML = "<option value=''>Выберите ряд</option>";
  storeSelect.innerHTML = "<option value=''>Выберите магазин</option>";
  rowSelect.disabled = true;
  storeSelect.disabled = true;

  if (!block) return;

  fetch(`/get_rows/${block}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.type === "shops") {
        data.items.forEach((shop) => {
          let opt = document.createElement("option");
          opt.value = shop;
          opt.textContent = shop;
          storeSelect.appendChild(opt);
        });
        storeSelect.disabled = false;
      } else {
        data.items.forEach((row) => {
          let opt = document.createElement("option");
          opt.value = row;
          opt.textContent = row;
          rowSelect.appendChild(opt);
        });
        rowSelect.disabled = false;
      }
    });
}

// загрузка магазинов
function loadStores() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value;
  const storeSelect = document.getElementById("store");

  storeSelect.innerHTML = "<option value=''>Выберите магазин</option>";
  storeSelect.disabled = true;

  if (!row) return;

  fetch(`/get_stores/${block}/${row}`)
    .then((res) => res.json())
    .then((data) => {
      data.items.forEach((shop) => {
        let opt = document.createElement("option");
        opt.value = shop;
        opt.textContent = shop;
        storeSelect.appendChild(opt);
      });
      storeSelect.disabled = false;
    });
}

// загрузка пути
function getPath() {
  const block = document.getElementById("block").value;
  const row = document.getElementById("row").value || "None";
  const shop = document.getElementById("store").value;

  if (!shop) return;

  fetch(`/get_path/${block}/${row}/${shop}`)
    .then((res) => res.json())
    .then((data) => {
      const pathResult = document.getElementById("pathResult");
      pathResult.innerHTML = data.path ? `<b>${data.path}</b>` : data.error;
    });
}


  
function loadRows() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");

  rowSelect.innerHTML = '<option value="">Выберите ряд</option>';
  storeSelect.innerHTML = '<option value="">Выберите магазин</option>';
  pathResult.innerHTML = "";
  rowSelect.disabled = true;
  storeSelect.disabled = true;

  const block = blockSelect.value;
  if (block) {
    fetch(`/get_rows?block=${encodeURIComponent(block)}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.rows && data.rows.length > 0) {
          data.rows.forEach((row) => {
            const option = document.createElement("option");
            option.value = row;
            option.textContent = row;
            rowSelect.appendChild(option);
          });
          rowSelect.disabled = false;
        } else {
          pathResult.innerHTML = '<p class="error">Ряды не найдены.</p>';
        }
      })
      .catch((error) => {
        pathResult.innerHTML =
          '<p class="error">Ошибка загрузки рядов: ' + error + "</p>";
      });
  }
}

function loadStores() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");

  storeSelect.innerHTML = '<option value="">Выберите магазин</option>';
  pathResult.innerHTML = "";
  storeSelect.disabled = true;

  const block = blockSelect.value;
  const row = rowSelect.value;
  if (block && row) {
    fetch(
      `/get_stores?block=${encodeURIComponent(block)}&row=${encodeURIComponent(
        row
      )}`
    )
      .then((response) => response.json())
      .then((data) => {
        if (data.stores && data.stores.length > 0) {
          data.stores.forEach((store) => {
            const option = document.createElement("option");
            option.value = store;
            option.textContent = store;
            storeSelect.appendChild(option);
          });
          storeSelect.disabled = false;
        } else {
          pathResult.innerHTML = '<p class="error">Магазины не найдены.</p>';
        }
      })
      .catch((error) => {
        pathResult.innerHTML =
          '<p class="error">Ошибка загрузки магазинов: ' + error + "</p>";
      });
  }
}

function getPath() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");

  const block = blockSelect.value;
  const row = rowSelect.value;
  const store = storeSelect.value;

  if (block && row && store) {
    fetch(
      `/get_path?block=${encodeURIComponent(block)}&row=${encodeURIComponent(
        row
      )}&store=${encodeURIComponent(store)}`
    )
      .then((response) => response.json())
      .then((data) => {
        if (data.path) {
          pathResult.innerHTML = `<p><strong>Путь:</strong> ${data.path}</p>`;
        } else {
          pathResult.innerHTML = '<p class="error">Путь не найден.</p>';
        }
      })
      .catch((error) => {
        pathResult.innerHTML =
          '<p class="error">Ошибка получения пути: ' + error + "</p>";
      });
  } else {
    pathResult.innerHTML = '<p class="error">Выберите блок, ряд и магазин.</p>';
  }
}

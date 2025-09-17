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

// static/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Список фоновых изображений
    const backgrounds = [
      "/static/images/abu-saxiy1.webp", // Замените на ваши изображения
      "/static/images/abu-saxiy2.webp", // Замените на ваши изображения
      "/static/images/abu-saxiy3.webp", // Замените на ваши изображения
      "/static/images/abu-saxiy4.webp", // Замените на ваши изображения
      "/static/images/abu-saxiy5.webp",
      "/static/images/abu-saxiy6.webp",
      "/static/images/abu-saxiy7.webp",
      "/static/images/abu-saxiy8.webp",
      "/static/images/abu-saxiy9.webp",
      "/static/images/abu-saxiy10.webp",
      "/static/images/abu-saxiy11.webp",
      "/static/images/abu-saxiy12.webp",
      "/static/images/abu-saxiy13.webp",
      "/static/images/abu-saxiy14.webp",
      "/static/images/abu-saxiy15.webp",
      "/static/images/abu-saxiy16.webp",
      "/static/images/abu-saxiy17.webp",
      "/static/images/abu-saxiy18.webp",
      "/static/images/abu-saxiy19.webp",
      "/static/images/abu-saxiy20.webp",
      "/static/images/abu-saxiy21.webp",
      "/static/images/abu-saxiy22.webp",
      "/static/images/abu-saxiy23.webp",
      "/static/images/abu-saxiy24.webp",
      "/static/images/abu-saxiy25.webp",
      "/static/images/abu-saxiy26.jpg",
      "/static/images/abu-saxiy27.jpg",
      "/static/images/abu-saxiy28.jpg",
      

    ];

    let currentIndex = 0;
    const backgroundElement = document.body; // Или document.querySelector('.background-container');

    // Функция для смены фона
    function changeBackground() {
        backgroundElement.style.backgroundImage = `url('${backgrounds[currentIndex]}')`;
        currentIndex = (currentIndex + 1) % backgrounds.length; // Циклический переход
    }

    // Начальная установка фона
    changeBackground();

    // Смена фона каждые 8 секунд
    setInterval(changeBackground, 8000);
});
function changeLanguage(lang) {
  fetch(`/set_language/${lang}`).then(() => {
    window.location.reload();
  });
}



function updateFlag(lang) {
  const select = document.getElementById("languageSelect");
  let flag = "/static/images/ru.webp";
  if (lang === "uz_Latn") flag = "/static/images/uz_latn.webp";
  if (lang === "uz_Cyrl") flag = "/static/images/uz_cyrl.webp";
  select.style.backgroundImage = `url('${flag}')`;
  select.style.backgroundRepeat = "no-repeat";
  select.style.backgroundPosition = "8px center";
  select.style.backgroundSize = "24px 16px";
  select.style.paddingLeft = "40px";
}

// Вызывайте при загрузке и при смене языка:
document.addEventListener("DOMContentLoaded", function () {
  updateFlag(document.getElementById("languageSelect").value);
  document
    .getElementById("languageSelect")
    .addEventListener("change", function () {
      updateFlag(this.value);
    });
});



function loadRows() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");

  rowSelect.innerHTML = `<option value="">${rowSelect.dataset.selectRow}</option>`;
  rowSelect.disabled = true;
  storeSelect.innerHTML = `<option value="">${storeSelect.dataset.selectStore}</option>`;
  storeSelect.disabled = true;
  pathResult.innerHTML = "";

  const block = blockSelect.value;
  if (block) {
    fetch(`/get_rows/${encodeURIComponent(block)}`)
      .then((response) => response.json())
      .then((rows) => {
        if (rows.length > 0) {
          rowSelect.disabled = false;
          rows.forEach((row) => {
            rowSelect.innerHTML += `<option value="${row}">${row}</option>`;
          });
        } else {
          pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorRows}</div>`;
        }
      })
      .catch((error) => {
        console.error("Error fetching rows:", error);
        pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorRows}</div>`;
      });
  }
}

function loadStores() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");

  storeSelect.innerHTML = `<option value="">${storeSelect.dataset.selectStore}</option>`;
  storeSelect.disabled = true;
  pathResult.innerHTML = "";

  const block = blockSelect.value;
  const row = rowSelect.value;
  if (block && row) {
    fetch(`/get_stores/${encodeURIComponent(block)}/${encodeURIComponent(row)}`)
      .then((response) => response.json())
      .then((stores) => {
        if (stores.length > 0) {
          storeSelect.disabled = false;
          stores.forEach((store) => {
            storeSelect.innerHTML += `<option value="${store}">${store}</option>`;
          });
        } else {
          pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorStores}</div>`;
        }
      })
      .catch((error) => {
        console.error("Error fetching stores:", error);
        pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorStores}</div>`;
      });
  }
}

// ...existing code...
function getPath() {
  const blockSelect = document.getElementById("block");
  const rowSelect = document.getElementById("row");
  const storeSelect = document.getElementById("store");
  const pathResult = document.getElementById("pathResult");
  const block = blockSelect.value;
  const row = rowSelect.value;
  const shopId = storeSelect.value;

  if (block && row && shopId) {
    fetch(
      `/get_path/${encodeURIComponent(block)}/${encodeURIComponent(
        row
      )}/${encodeURIComponent(shopId)}`
    )
      .then((response) => response.json())
      .then((data) => {
        if (data.path) {
          pathResult.innerHTML = data.path;
        } else {
          pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorPath}</div>`;
        }
      })
      .catch((error) => {
        console.error("Error fetching path:", error);
        pathResult.innerHTML = `<div class="error">${pathResult.dataset.errorPath}</div>`;
      });
  }
}
// ...existing code...

// Смена изображений
let imageIndex = 1;
const images = [
  "/static/images/abu-saxiy1.webp",
  "/static/images/abu-saxiy2.webp",
  "/static/images/abu-saxiy3.webp",
];
setInterval(() => {
  document.body.style.backgroundImage = `url(${images[imageIndex]})`;
  imageIndex = (imageIndex + 1) % images.length;
}, 5000);

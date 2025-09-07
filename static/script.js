 
        function loadRows() {
            const blockSelect = document.getElementById('block');
            const rowSelect = document.getElementById('row');
            const storeSelect = document.getElementById('store');
            const pathResult = document.getElementById('pathResult');

            rowSelect.innerHTML = '<option value="">Выберите ряд</option>';
            storeSelect.innerHTML = '<option value="">Выберите магазин</option>';
            rowSelect.disabled = true;
            storeSelect.disabled = true;
            pathResult.textContent = '';

            const block = blockSelect.value;
            if (block) {
                console.log(`Fetching rows for block: ${block}`);
                fetch(`/get_rows?block=${encodeURIComponent(block)}`)
                    .then(response => response.json())
                    .then(rows => {
                        console.log(`Rows received: ${rows}`);
                        rows.forEach(row => {
                            const option = document.createElement('option');
                            option.value = row;
                            option.textContent = row;
                            rowSelect.appendChild(option);
                        });
                        rowSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching rows:', error);
                        pathResult.textContent = 'Ошибка при загрузке рядов';
                        pathResult.className = 'error';
                    });
            }
        }

        function loadStores() {
            const blockSelect = document.getElementById('block');
            const rowSelect = document.getElementById('row');
            const storeSelect = document.getElementById('store');
            const pathResult = document.getElementById('pathResult');

            storeSelect.innerHTML = '<option value="">Выберите магазин</option>';
            storeSelect.disabled = true;
            pathResult.textContent = '';

            const block = blockSelect.value;
            const row = rowSelect.value;
            if (block && row) {
                console.log(`Fetching stores for block: ${block}, row: ${row}`);
                fetch(`/get_stores?block=${encodeURIComponent(block)}&row=${encodeURIComponent(row)}`)
                    .then(response => response.json())
                    .then(stores => {
                        console.log(`Stores received: ${stores}`);
                        stores.forEach(store => {
                            const option = document.createElement('option');
                            option.value = store;
                            option.textContent = store;
                            storeSelect.appendChild(option);
                        });
                        storeSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching stores:', error);
                        pathResult.textContent = 'Ошибка при загрузке магазинов';
                        pathResult.className = 'error';
                    });
            }
        }

        function getPath() {
            const blockSelect = document.getElementById('block');
            const rowSelect = document.getElementById('row');
            const storeSelect = document.getElementById('store');
            const pathResult = document.getElementById('pathResult');

            const block = blockSelect.value;
            const row = rowSelect.value;
            const store = storeSelect.value;

            if (!block || !row || !store) {
                pathResult.textContent = 'Пожалуйста, выберите блок, ряд и магазин';
                pathResult.className = 'error';
                console.error('Missing block, row, or store:', { block, row, store });
                return;
            }

            console.log(`Sending POST request for path: block=${block}, row=${row}, store=${store}`);
            fetch('/get_path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `block=${encodeURIComponent(block)}&row=${encodeURIComponent(row)}&store=${encodeURIComponent(store)}`
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Path response:', data);
                    pathResult.className = '';
                    if (data.error) {
                        pathResult.textContent = data.error;
                        pathResult.className = 'error';
                    } else {
                        pathResult.textContent = data.path;
                    }
                })
                .catch(error => {
                    console.error('Error fetching path:', error);
                    pathResult.textContent = 'Ошибка при получении пути';
                    pathResult.className = 'error';
                });
        }
    
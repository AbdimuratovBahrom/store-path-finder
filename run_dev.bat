@echo off
echo ================================
echo 🚀 DEV START: Store Path Finder
echo ================================

:: Активируем виртуальное окружение
call myenv\Scripts\activate

:: Удаляем старую базу
if exist shops.db (
    del shops.db
    echo ✅ Старый shops.db удален
) else (
    echo ⚠️ База shops.db не найдена, создадим заново
)

:: Создаём новую базу
echo 🔄 Создание новой базы...
python init_db.py

:: Запуск Flask
echo 🚀 Запускаем Flask сервер...
python app.py

pause

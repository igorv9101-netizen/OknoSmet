[app]

# Название приложения (то, что будет видно на телефоне)
title = ОкноСмет

# Имя пакета (только латиница, без пробелов и заглавных букв)
package.name = oknosmet

# Домен пакета
package.domain = org.oknosmet

# Исходный код
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xml

# Версия приложения
version = 1.0.0

# Требования (только kivy)
requirements = python3,kivy

# Ориентация
orientation = portrait

# Полноэкранный режим (0 = нет)
fullscreen = 0

# Иконка приложения (положи файл icon.png рядом с main.py)
icon.filename = %(source.dir)s/icon.png

# Заставка при запуске (можно использовать ту же иконку)
presplash.filename = %(source.dir)s/icon.png

# Разрешения Android (нам ничего особенного не нужно)
android.permissions = 

# Минимальная и целевая версия Android
android.minapi = 24
android.api = 33
android.accept_sdk_license = True
android.ndk_api = 24

# Архитектуры (современные телефоны)
android.archs = arm64-v8a, armeabi-v7a

# Не оставлять отладочные символы
android.add_jars = 

# Отключаем ненужные сервисы
services = 

# Логирование
log_level = 2

# Не пропускать проверку
warn_on_root = 1

[buildozer]

# Логи
log_level = 2

# Не спрашивать подтверждения
warn_on_root = 1

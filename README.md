# Hundeführerschein (NRW) — Lernseite

Небольшая статическая страница для подготовки к Sachkundenachweis (NRW). Открывается прямо в браузере, без сервера.

## Онлайн-версия
- GitHub Pages: https://malaeu.github.io/Hundef-hrerschein/

## Локально
- Открой `index.html` в браузере.

## Содержимое
- `index.html` — основной файл
- `images/` — картинки вопросов

## Проверка ответов (PDF)
Скрипт сверяет ответы из `index.html` с официальной Lösungsschablone (NRW, gültig ab 01.01.2025).

Запуск:
```
/Users/emalam/Documents/GitHub/Alessia/.venv/bin/python scripts/verify_pdf_answers.py
```

Отчёт сохраняется в `reports/answers_report.csv`.

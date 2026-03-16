# Упрощенный API для системы межведомственного обмена  
## Описание проекта

Использованный стек:
- fastapi
- sqlite
- pydantic
- sqlalchemy

Проект задеплоен на Render и доступен по ссылке (вероятно нужно будет чуток подождать пока рендер разбудит систему):
```
    https://central-registry-api.onrender.com
```

Проект представляет из себя приложение эмулирующее работу Системы Б (указанной в ТЗ). Все документы
подписываются эмуляцией электронной цифровой подписи (ЭЦП) и хранятся в блокчейн подобной структуре.
Еденицей хранения в реестре является Транзакция (определена в src/api/models.py).
При старте проекта происходит создание первой базовой транзакции.

### Особенности реализации
Для обеспечения корректного и быстрого поиска поле транзакции transaction_time хранится в бд как datetime.
Для обеспечения вывода в ISO8601 в базовой схеме были использованы валидаторы, функции для перевода вынесены в src/utils, то же для обеспечения вывода decimal с round(2).
Также для корректного вывода json в PascalCase был использован alias в базовой схеме.

  
  <h2> Инструкцию по установке и запуску</h2>


Установка репозитория и сборка и запуск контейнера:

```
  git clone https://github.com/Selleihtr/central-registry-api.git
  cd central-registry-api

  docker-compose up --build
```
Запуск осуществляется на http://0.0.0.0:8000 

  ## Описание структуры проекта

Проект построен на принципах многослойной архитектуры.

Основные слои:
router.py      — обработка запросов
service.py     — бизнес-логика
models.py      — работа с БД
schemas/       — модели данных

При создании структуры руководствовался по данному репозиторию:
```
  https://github.com/zhanymkanov/fastapi-best-practices
```

Файловая стркутура проекта:
```
.
└── src
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   ├── constants.py
    │   ├── exceptions.py
    │   ├── models.py
    │   ├── router.py
    │   ├── schemas
    │   │   ├── __init__.py
    │   │   ├── messages.py
    │   │   ├── search_request.py
    │   │   ├── signed_api_data.py
    │   │   └── transactions.py
    │   ├── service.py
    │   └── utils.py
    ├── config.py
    ├── database.py
    ├── main.py
    ├── models.py
    ├── placeholder.py
    ├── requirements.txt
    ├── schemas.py
    └── utils.py
```


## Примеры curl-запросов для всех эндпоинтов

Для удобства декодирования

https://base64.ru/


/api/health
```
curl -X GET "https://central-registry-api.onrender.com/api/health"
```

/api/outgoing
```
curl -X POST "https://central-registry-api.onrender.com/api/outgoing" \
  -H "Content-Type: application/json" \
  -d '{"Data": "eyJTdGFydERhdGUiOiIyMDI0LTAxLTAxVDAwOjAwOjAwWiIsIkVuZERhdGUiOiIyMDI0LTEyLTMxVDIzOjU5OjU5WiIsIkxpbWl0IjoxMCwiT2Zmc2V0IjowfQ==", "SignerCert": "U1lTVEVNX0E=", "Sign": "dSlE6A3YIsKynKLEeHlfq8J1ITA/jccbcKzrUEbCarEw="}'
```

/api/incoming
```
curl -X 'POST' \
  'https://central-registry-api.onrender.com/api/incoming' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Data": "eyJUcmFuc2FjdGlvbnMiOlt7IlRyYW5zYWN0aW9uVHlwZSI6OSwiRGF0YSI6ImV5SlRaVzVrWlhKQ2NtRnVZMmdpT2lKVFdWTlVSVTFmUWlJc0lsSmxZMlZwZG1WeVFuSmhibU5vSWpvaVUxbFRWRVZOWDBFaUxDSkpibVp2VFdWemMyRm5aVlI1Y0dVaU9qSXdNU3dpVFdWemMyRm5aVlJwYldVaU9pSXlNREkwTFRBMUxUSXdWREV3T2pBd09qQXdXaUlzSWtOb1lXbHVSM1ZwWkNJNklrTklRVWxPTFRBd01TSXNJbEJ5WlhacGIzVnpWSEpoYm5OaFkzUnBiMjVJWVhOb0lqcHVkV3hzTENKTlpYUmhSR0YwWVNJNmJuVnNiQ3dpUkdGMFlTSTZJbVY1U2twaWJWcDJZMjB4YUdSSGJIWmliRkkxWTBkVmFVOXFTWGROVTNkcFUxYzFiV0l6U25SWldGSndZakkxVldWWVFteFZNMUo1WVZjMWJrbHFiMmt3U2t4U2FUbERNREJNUkZKb09VTjNTVTVEZWpCTVJGSm5Ua04zTUV3elVtZDBRelF3VEdkcFRFTktUMlJYTVdsYVdFbHBUMmxLUTFKNU1IbE5SRWt3VEZSQmQwMVRTWE5KYTJ4Nll6TldiRnBGVW1oa1IxVnBUMmxKZVUxRVNUQk1WRUV4VEZSSmQxWkVSWGRQYWtGM1QycEJkMWRwU1hOSmEyUXhXVmhLYUdKdVVuWmphVWsyU1hSRFpUQktOMUZ1YVVGdU1FdFVVWFZPUXprd1RFUlJkbVJIUWpCTU4xRnpkRU4zTUZrNFp6Qk1VRkZ6VGtkQk1FeEVVWFprUjBNd1RHcFNhbmxqYVV4RFNrTmFWelZzV20xc2FtRlhSbmxsVTBrMlNYUkRWREJNTjFKblpFZEVNRXhVVVhOT1IwRXdXVWhTWjNSRGVUQk1XRkYyWkVNNU1FdzNVWFJUUkZKbk9VZElNRmxFVVhSa1F6SXdURlJSZEdSRE9UQk1hbEYwVTBGdU1Fb3ZVWFowUXpjd1dWQlNhRGxEZHpCWlRGRjBaRU0zTUZsM2JrbHBkMmxWU0Vwd1ltMU9jR05IUm5OSmFtOXBNRW8zVVc1MFEyVkpRMlpSYkU1REt6Qk1kbEYwZEVNNU1FeHFVWFZwWTJsTVEwcFFXVzE0Y0ZveVJqQmhWemwxWTNsSk5sY3pjMmxXU0d4M1dsTkpOazFUZDJsVk0xSm9ZMjVTUlZsWVVteEphbTlwVFdwQmVVNURNSGRPYVRCM1RWWlJkMDFFYjNkTlJHOTNUVVp2YVV4RFNrWmliVkpGV1ZoU2JFbHFiMmxOYWtGNVRrTXdlRTFwTUhkTlZsRjNUVVJ2ZDAxRWIzZE5SbTlwVEVOS1Fsa3pVa1ZaV0ZKc1NXcHZhVTFxUVhsT1F6QjNUbE13ZUU1V1VYZE5SRzkzVFVSdmQwMUdiMmxNUTBwQ1dUTlNUMlJYTVdsYVdFbHBUMmxNVVc0NVEyZE1WRWwzVFdwUmRrMUVWWFpOVkZWMFRVUkJlRWxwZDJsV1IwWTBZM2xKTmxjemMybFVibFowV1cxV2VVbHFiM2hNUTBwUFdWY3hiRlpIUmpSSmFtOXBNRW8zVVhOa1IxQXdUR1pSYzA1SFF6Qk1XRkYxT1VkTk1GbElVbWQwUTNrd1REUm5NRXd2VVhacFJGRjFkRU1yTUV3elVtZDBSMEV3VEVSUmRYUkhRekJaVFdjMGIxTlhNRXB2ZEUxcVFYbE9RekIzVFZOSmMwbHJSblJpTTFaMVpFTkpOazVVUVhkTlJFRjFUVU4zYVZWSFZuVmlibXhDWWxjNU1XSnVVV2xQYWtGMVRVZ3djMlY1U2s5a1Z6RnBXbGhKYVU5cVNYTkphelZvWWxkV1ZWbFlaMmxQYVV4UmF6bERkekJaUkZGelRrTTVNRmxNVVhWT1F6VXdURE5SZG5SRE1VbE9ReXN3VEVoUmRHUkhRakJNTDFGMFpFZElNRXhZVVhaa1F6UXdURlZwVEVOS1FtSlhPVEZpYmxGcFQycEZNVTFFUVhkTWFrRnpTV3hDYkdKdE5UVlJWekYyWkZjMU1FbHFiekZOUkVGMVRVZ3haR1pXTUhOSmJFNHdXVmhLTUZKSFJqQmFVMGsyU1dwSmQwMXFVWFJOUkZsMFRVUkdWVTFFUVRaTlJFRTJUVVJDWVVscGQybFNWelZyVWtkR01GcFRTVFpKYWtsM1RXcFJkRTFVU1hSTlZGWlZUVVJCTmsxRVFUWk5SRUpoU1dsM2FWRXpWbmxqYlZaMVdUTnNSR0l5VW14SmFtOXBWbFpPUlVscGQybFJNMVo1WTIxV2RWa3piRTlaVnpGc1NXcHZhVEJLVkZGMmRFTTNNRXgyVVhOT1IwRkpUa05vTUV0cVVXdERTWE5KYTBaMFlqTldkV1JEU1RaT2FsVjNUVVJCZFUxRGQybFZiVll5WWpKMGFHUkhiSFppYTJ4MVdtMDRhVTlwVEZGclpFTXhNRXhtVVhaMFIwTXdUR1pTYVRsRGVUQk1NMUZ6VGtkUVNXbDNhVkV5ZUdoaFZ6RlRZVmRrYjJSR1VubFpWelY2V20xV2VVbHFiMmt3U2pOUmRGTkVVWFJPUXlzd1RDOVNaemxIUWpCTWNsRnpUa014TUZsTVVtZGtSMUJKYVhkcFZVZEdOV0pYVm5Wa1JrSnNZMjFzZGxwRFNUWkphbFZuTUZsRVVYTk9RM2d3VERkU2FEbEROREJaVldjd1RGUlJkbVJETVRCTWEyY3dXVVZuTUV4NlVYWjBRemd3VEZoUmRtUkhRekJNUVdjd1RDOVJkblJETnpCWlVGSm9PVU14TUV3elVYVk9SMUJKVGtkRE1GbEVVWFJrUTNnd1REZFJjM1JEZHpCTU0xRjFUa2RRU1dsM2FWVXliRzVpYlZaNVZHMUdkRnBUU1RaSmRFTlpNRXhNVVhOT1F6a3dURGRSYzJsRVVXMU9RM2t3VEVSUmRsTkVVVzFPUTNrd1RFUlJkbVJES3pCTVRGRjFUa2RJU1dsM2FWRllWakJoUnpsNVlWaHdiRnBHUW5aak1td3dZVmM1ZFVscWIya3dTbEJSZEdSRE9UQk1XRkpuVGtOM01FeDJVbXBPUXprd1dYWlJkVk5FVVhST1F6UXdXVVJSZEdSRE5qQlpURkYyZEVkQlNXbDNhVkZ0Um5WaE1HUXhXVmhLYUdKdVVteGFWV2hvWXpKbmFVOXBTVEZTUkZwSFQwVlZlVkZVUmtSTk1FazFVbXBTUlU0d1ZUUlJWRXBFVGxWSmVGSkVUa2RPYTFVMFVWUnNSRTFyVVRCU2FscENUMFZKZUZGNlRrWk9WVmt6VVZSc1JVMXJTVEJSZWxwR1QwVlpkMUZVUldsbVVUMDlJbjA9IiwiSGFzaCI6IjE3MUE4NDkyRkM3RTlBRThBMEVGQzRGOERCQzZEMzMzNjFCNTI0MzgxRUNERUU4M0Q4NjA1QUQ3QkIwODY3RjIiLCJTaWduIjoib0NPMUtCeU02MGgzeVk4cGxqMGFNc0RaRG5DbDhYczc1MGt4a203cjJmMD0iLCJTaWduZXJDZXJ0IjoiVTFsVFZFVk5YMEU9IiwiVHJhbnNhY3Rpb25UaW1lIjoiMjAyNC0wMS0xNVQxMDozMDowMFoiLCJNZXRhRGF0YSI6bnVsbCwiVHJhbnNhY3Rpb25JbiI6bnVsbCwiVHJhbnNhY3Rpb25PdXQiOm51bGx9XSwiQ291bnQiOjF9",
  "Sign": "IAcd+ow4IbH+CVCO5RT5/7czDqcfhHLzeZxVQDP6sMA=",
  "SignerCert": "U1lTVEVNX0E="
}'
```

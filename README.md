# WYSIWYM

# FAQ

## Как запустить? 
Запустить веб-сервер `unicorn`.

```shell
# WYSIWYM/project !!!
uvicorn app.main:app --reload
```
 Далее перейти в браузере по URL: `http://127.0.0.1:8000`
 
## Админ-панель
Необходимо ввести в стандартное окно авторизации

```shell
login: admin
password: admin
```
## Как установить зависимости?
Активируйте виртуальное окружение и выполните:

```shell
pip install -r requirements.txt
```

## Как установить виртуальное окружение?
1. Создайте виртуальное окружение:
```shell
python -m venv myenv
```
2. Активируйте виртуальное окружение: 

&nbsp;&nbsp;&nbsp;&nbsp;На Windows:
```shell
myenv\Scripts\activate
```
&nbsp;&nbsp;&nbsp;&nbsp;На macOS и Linux:
```shell
source myenv/bin/activate
```

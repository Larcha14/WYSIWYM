from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from begin_to_import import AircraftModel

# Создаем экземпляр модели
model = AircraftModel()

# Определение входных данных для предсказания
class PredictionRequest(BaseModel):
    # Определим поля необходимые для предсказания (например, egt, n1a, n2a и другие)
    egt: float
    n1a: float
    n2a: float
    nf: float
    ff: float
    # Тут еще добавим разберемся с моментом если вдруг на новых данных будет что-то дропать но думаю тут итак норм будет

# Определение выходных данных для предсказания
class PredictionResponse(BaseModel):
    acnum: str
    predicted_value: float

# Создание экземпляра FastAPI
app = FastAPI()

# Определение маршрута для предсказания
@app.post("/predict/", response_model=PredictionResponse)
def predict_acnum(payload: PredictionRequest):
    try:
        # Получение предсказания для заданных данных
        input_data = pd.DataFrame([payload.dict()])
        df_cleaned = model.clear_data(input_data)
        scaled_input = model.scaler.transform(df_cleaned.drop('acnum', axis=1))
        prediction = model.models['VQ-BGU'].predict(scaled_input)

        # Формирование ответа
        result = PredictionResponse(acnum='VQ-BGU', predicted_value=prediction[0])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Запуск приложения FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

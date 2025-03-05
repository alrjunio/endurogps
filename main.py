from fastapi import FastAPI
from routers import router


app = FastAPI()



# Incluindo as rotas
app.include_router(router)



# Executar o aplicativo
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8080, log_level='info' , reload=True )
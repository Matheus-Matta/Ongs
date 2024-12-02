# Usando a imagem oficial do Python
FROM python:3.9

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de dependências para o contêiner
COPY requirements.txt /app/

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código para o contêiner
COPY . /app/

# Expor a porta que o Django vai rodar
EXPOSE 8000

# Comando de entrada: você vai usar o wait-for-it.sh para garantir que o banco esteja pronto antes de rodar os comandos Django
ENTRYPOINT ["./wait-for-it.sh", "db:5432", "--"]

# O comando de inicialização do Django (migrate, collectstatic e runserver)
CMD ["python", "manage.py", "migrate", "--noinput", "&&", "python", "manage.py", "collectstatic", "--noinput", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]

version: '3.1'
services :
  db:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: stylegen
      POSTGRES_PASSWORD: stylegen
      POSTGRES_DB: main
  admin:
    image: adminer
    restart: always
    depends_on: 
      - db
    ports:
      - 8080:8080
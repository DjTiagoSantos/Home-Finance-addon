ARG BUILD_FROM
FROM $BUILD_FROM

# Instalar dependências do sistema
RUN apk add --no-cache \
    python3 \
    py3-pip \
    sqlite \
    nginx \
    supervisor

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY run.sh .
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Tornar o script executável
RUN chmod +x run.sh

# Criar diretório de dados
RUN mkdir -p /data

# Expor porta
EXPOSE 8080

# Comando de inicialização
CMD ["./run.sh"]


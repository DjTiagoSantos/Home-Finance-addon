#!/usr/bin/with-contenv bashio

# Configurar variáveis de ambiente
export DATABASE_PATH=$(bashio::config 'database_path')
export LOG_LEVEL=$(bashio::config 'log_level')
export PORT=$(bashio::config 'port')

# Log de inicialização
bashio::log.info "Iniciando Home Finance Manager..."
bashio::log.info "Banco de dados: ${DATABASE_PATH}"
bashio::log.info "Nível de log: ${LOG_LEVEL}"
bashio::log.info "Porta: ${PORT}"

# Criar banco de dados se não existir
if [ ! -f "${DATABASE_PATH}" ]; then
    bashio::log.info "Criando banco de dados inicial..."
    python3 /app/app/init_db.py
fi

# Iniciar supervisor para gerenciar nginx e aplicação Flask
bashio::log.info "Iniciando serviços..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf


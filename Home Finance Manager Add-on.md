# Home Finance Manager Add-on

Um add-on completo para Home Assistant que oferece gestão financeira doméstica com interface web moderna e integração nativa com o ecossistema do Home Assistant.

## 🚀 Funcionalidades

### 💰 Gestão Financeira Completa
- **Controle de Receitas e Despesas**: Registro detalhado de transações com categorização
- **Múltiplas Contas**: Suporte para Conta Corrente, Poupança, Cartão de Crédito e Dinheiro
- **Categorização Inteligente**: Sistema de categorias personalizáveis para organização
- **Relatórios Visuais**: Dashboard interativo com gráficos e métricas em tempo real
- **Interface Responsiva**: Design moderno que funciona em desktop e mobile

### 🏠 Integração com Home Assistant
- **Sensores Automáticos**: Exposição de dados financeiros como sensores nativos
- **Serviços Personalizados**: Comandos para adicionar transações via automações
- **Notificações Inteligentes**: Alertas sobre gastos excessivos ou metas atingidas
- **Dashboard Integrado**: Visualização no painel principal do Home Assistant

## 📦 Instalação

### Pré-requisitos
- Home Assistant OS ou Supervised
- Mínimo 512MB RAM disponível
- 100MB espaço em disco

### Instalação Rápida

1. **Adicionar Repositório**
   - Vá em `Settings > Add-ons > Add-on Store`
   - Clique nos três pontos → "Repositories"
   - Adicione: `https://github.com/seu-usuario/home-finance-addon`

2. **Instalar Add-on**
   - Procure por "Home Finance Manager"
   - Clique em "Install"
   - Configure e inicie o add-on

3. **Acessar Interface**
   - Clique em "Open Web UI"
   - Ou acesse `http://homeassistant.local:8080`

## ⚙️ Configuração

### Configuração Básica
```yaml
database_path: "/data/finance.db"
log_level: "info"
port: 8080
```

### Primeira Configuração
1. Acesse a interface web
2. Configure suas contas bancárias
3. Personalize categorias de receitas/despesas
4. Comece a registrar transações

## 🔧 Uso

### Registrar Transações
- Clique em "Nova Transação" no dashboard
- Preencha descrição, valor, tipo e categoria
- A transação aparece imediatamente nos relatórios

### Visualizar Relatórios
- **Dashboard**: Visão geral com saldos e gráficos
- **Transações**: Lista completa com filtros
- **Relatórios**: Análises por categoria e período

### Integração Home Assistant

#### Sensores Disponíveis
- `sensor.finance_total_balance` - Saldo Total
- `sensor.finance_monthly_income` - Receitas do Mês  
- `sensor.finance_monthly_expenses` - Despesas do Mês
- `sensor.finance_monthly_net` - Saldo do Mês

#### Serviços
```yaml
# Adicionar despesa
service: finance_manager.add_expense
data:
  description: "Compra supermercado"
  amount: 150.50
  category: "Alimentação"

# Adicionar receita  
service: finance_manager.add_income
data:
  description: "Salário"
  amount: 3000.00
  category: "Salário"
```

## 📊 Exemplos de Automação

### Alerta de Gastos Altos
```yaml
automation:
  - alias: "Alerta Financeiro"
    trigger:
      platform: numeric_state
      entity_id: sensor.finance_monthly_expenses
      above: 2000
    action:
      service: notify.mobile_app
      data:
        title: "⚠️ Gastos Elevados"
        message: "Despesas ultrapassaram R$ 2.000!"
```

### Resumo Semanal
```yaml
automation:
  - alias: "Resumo Financeiro"
    trigger:
      platform: time_pattern
      weekday: 1
      hour: 9
    action:
      service: notify.telegram
      data:
        message: |
          📊 Resumo Semanal:
          💰 Saldo: R$ {{ states('sensor.finance_total_balance') }}
          📈 Receitas: R$ {{ states('sensor.finance_monthly_income') }}
          📉 Despesas: R$ {{ states('sensor.finance_monthly_expenses') }}
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
home-finance-addon/
├── app/                    # Aplicação Flask
│   ├── main.py            # API principal
│   ├── models.py          # Modelos de dados
│   └── home_assistant_integration.py
├── static/                # Arquivos estáticos
│   ├── css/style.css      # Estilos
│   └── js/app.js          # JavaScript
├── templates/             # Templates HTML
├── config.yaml           # Configuração do add-on
├── Dockerfile            # Container Docker
└── README.md             # Este arquivo
```

### Executar Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
export DATABASE_PATH="/tmp/finance.db"
export LOG_LEVEL="debug"
export PORT="5000"

# Inicializar banco
python app/init_db.py

# Executar aplicação
python app/main.py
```

### Executar Testes
```bash
python tests.py
```

## 📚 Documentação

- **[Manual Completo](MANUAL.md)** - Guia detalhado de instalação e uso
- **[Integração HA](INTEGRATION.md)** - Documentação dos sensores e serviços
- **[Changelog](CHANGELOG.md)** - Histórico de versões

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes se necessário
5. Submeta um pull request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/home-finance-addon/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/home-finance-addon/discussions)
- **Comunidade**: [Fórum Home Assistant](https://community.home-assistant.io/)

## 🎯 Roadmap

- [ ] Importação de extratos bancários (OFX/CSV)
- [ ] Orçamento com alertas automáticos
- [ ] Relatórios avançados com gráficos
- [ ] Integração Open Banking
- [ ] App mobile complementar
- [ ] Suporte a múltiplas moedas

---

**Desenvolvido com ❤️ para a comunidade Home Assistant**


# Manual de Instalação e Uso - Home Finance Manager

## Visão Geral

O Home Finance Manager é um add-on completo para Home Assistant que oferece gestão financeira doméstica com interface web intuitiva e integração nativa com o ecossistema do Home Assistant. Este manual fornece instruções detalhadas para instalação, configuração e uso do sistema.

## Funcionalidades Principais

### Gestão Financeira Completa
- **Controle de Receitas e Despesas**: Registro detalhado de todas as transações financeiras com categorização automática
- **Múltiplas Contas**: Suporte para diferentes tipos de contas (Corrente, Poupança, Cartão de Crédito, Dinheiro)
- **Categorização Inteligente**: Sistema de categorias personalizáveis para organização eficiente das transações
- **Relatórios Visuais**: Gráficos e dashboards interativos para análise financeira
- **Orçamento por Categoria**: Definição e acompanhamento de limites de gastos

### Integração com Home Assistant
- **Sensores Automáticos**: Exposição de dados financeiros como sensores nativos do Home Assistant
- **Serviços Personalizados**: Comandos para adicionar transações via automações ou comandos de voz
- **Notificações Inteligentes**: Alertas automáticos sobre gastos excessivos ou metas atingidas
- **Dashboard Integrado**: Visualização dos dados financeiros no painel principal do Home Assistant

## Pré-requisitos

### Requisitos do Sistema
- Home Assistant OS ou Home Assistant Supervised
- Mínimo 512MB de RAM disponível
- 100MB de espaço em disco
- Acesso à internet para instalação de dependências

### Versões Compatíveis
- Home Assistant Core 2023.1 ou superior
- Python 3.11 ou superior
- SQLite 3.x

## Instalação

### Método 1: Instalação via Repositório de Add-ons

1. **Adicionar Repositório**
   - Acesse o Home Assistant
   - Navegue para `Settings > Add-ons > Add-on Store`
   - Clique nos três pontos no canto superior direito
   - Selecione "Repositories"
   - Adicione a URL: `https://github.com/seu-usuario/home-finance-addon`

2. **Instalar o Add-on**
   - Procure por "Home Finance Manager" na loja de add-ons
   - Clique em "Install"
   - Aguarde a conclusão da instalação

### Método 2: Instalação Manual

1. **Preparar Diretório**
   ```bash
   cd /usr/share/hassio/addons/local
   git clone https://github.com/seu-usuario/home-finance-addon.git
   ```

2. **Reiniciar Supervisor**
   ```bash
   ha supervisor restart
   ```

3. **Instalar via Interface**
   - O add-on aparecerá na seção "Local add-ons"
   - Proceda com a instalação normal

## Configuração Inicial

### Configuração Básica

Após a instalação, configure o add-on através da interface:

```yaml
database_path: "/data/finance.db"
log_level: "info"
port: 8080
```

### Parâmetros de Configuração

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `database_path` | string | `/data/finance.db` | Caminho para o arquivo do banco de dados |
| `log_level` | list | `info` | Nível de log (debug, info, warning, error) |
| `port` | port | `8080` | Porta para a interface web |

### Primeira Execução

1. **Iniciar o Add-on**
   - Clique em "Start" na página do add-on
   - Aguarde a inicialização completa (pode levar alguns minutos)

2. **Verificar Logs**
   - Monitore os logs para confirmar inicialização bem-sucedida
   - Procure pela mensagem: "Integração com Home Assistant inicializada com sucesso!"

3. **Acessar Interface Web**
   - Clique em "Open Web UI" ou acesse `http://homeassistant.local:8080`
   - A interface deve carregar com dados padrão

## Configuração de Contas e Categorias

### Configuração de Contas

O sistema vem com contas padrão pré-configuradas, mas você pode personalizar conforme sua necessidade:

1. **Acessar Seção de Contas**
   - Na interface web, clique em "Contas" no menu lateral
   - Visualize as contas existentes

2. **Adicionar Nova Conta**
   - Clique em "Nova Conta"
   - Preencha os campos:
     - **Nome**: Nome identificador da conta
     - **Tipo**: Selecione entre Conta Corrente, Poupança, Cartão de Crédito ou Dinheiro
     - **Saldo Inicial**: Valor atual da conta

3. **Editar Contas Existentes**
   - Clique no ícone de edição na conta desejada
   - Modifique as informações necessárias
   - Salve as alterações

### Configuração de Categorias

O sistema inclui categorias padrão para receitas e despesas, organizadas por tipo:

#### Categorias de Despesas Padrão
- Alimentação
- Transporte
- Moradia
- Saúde
- Educação
- Lazer
- Vestuário
- Serviços
- Impostos
- Outros

#### Categorias de Receitas Padrão
- Salário
- Freelance
- Investimentos
- Vendas
- Presentes
- Outros

### Personalização de Categorias

1. **Adicionar Nova Categoria**
   - Acesse a seção "Categorias"
   - Selecione a aba "Despesas" ou "Receitas"
   - Clique em "Nova Categoria"
   - Configure:
     - **Nome**: Nome da categoria
     - **Tipo**: Receita ou Despesa
     - **Cor**: Cor para identificação visual
     - **Ícone**: Ícone FontAwesome (ex: fas fa-car)

2. **Personalizar Cores e Ícones**
   - Use cores distintas para facilitar identificação
   - Escolha ícones representativos da categoria
   - Mantenha consistência visual

## Uso Diário

### Registrando Transações

#### Adicionar Nova Transação

1. **Acesso Rápido**
   - Clique no botão "Nova Transação" no dashboard
   - Ou acesse a seção "Transações" e clique em "Adicionar"

2. **Preenchimento do Formulário**
   - **Descrição**: Descrição clara da transação
   - **Valor**: Valor em reais (use ponto para decimais)
   - **Tipo**: Selecione Receita ou Despesa
   - **Conta**: Escolha a conta de origem/destino
   - **Categoria**: Selecione a categoria apropriada
   - **Data**: Data da transação (padrão: hoje)
   - **Observações**: Informações adicionais (opcional)

3. **Confirmação**
   - Clique em "Salvar" para registrar
   - A transação aparecerá imediatamente no dashboard
   - O saldo da conta será atualizado automaticamente

#### Editar Transações

1. **Localizar Transação**
   - Use a seção "Transações" para visualizar todas as transações
   - Utilize filtros por conta, categoria ou tipo
   - Clique na transação desejada

2. **Modificar Dados**
   - Altere os campos necessários
   - Confirme as mudanças
   - O sistema recalculará automaticamente os saldos

#### Excluir Transações

1. **Seleção**
   - Localize a transação na lista
   - Clique no ícone de exclusão

2. **Confirmação**
   - Confirme a exclusão
   - O saldo da conta será ajustado automaticamente

### Visualização de Relatórios

#### Dashboard Principal

O dashboard oferece uma visão geral instantânea das finanças:

- **Saldo Total**: Soma de todas as contas ativas
- **Receitas do Mês**: Total de receitas do mês atual
- **Despesas do Mês**: Total de despesas do mês atual
- **Saldo do Mês**: Diferença entre receitas e despesas
- **Gráfico de Despesas**: Distribuição por categoria
- **Transações Recentes**: Últimas 5 transações

#### Filtros e Pesquisa

1. **Filtros Disponíveis**
   - Por conta específica
   - Por categoria
   - Por tipo (receita/despesa)
   - Por período de datas

2. **Aplicação de Filtros**
   - Selecione os filtros desejados
   - Os resultados são atualizados automaticamente
   - Combine múltiplos filtros para análises específicas

## Integração com Home Assistant

### Sensores Automáticos

O add-on expõe automaticamente os seguintes sensores:

#### Sensores Financeiros

| Sensor | Entity ID | Descrição |
|--------|-----------|-----------|
| Saldo Total | `sensor.finance_total_balance` | Soma de todos os saldos |
| Receitas do Mês | `sensor.finance_monthly_income` | Total de receitas mensais |
| Despesas do Mês | `sensor.finance_monthly_expenses` | Total de despesas mensais |
| Saldo do Mês | `sensor.finance_monthly_net` | Saldo líquido mensal |
| Transações do Mês | `sensor.finance_monthly_transactions` | Número de transações |
| Última Transação | `sensor.finance_last_transaction` | Detalhes da última transação |

### Serviços Personalizados

#### Adicionar Despesa via Serviço

```yaml
service: finance_manager.add_expense
data:
  description: "Compra no supermercado"
  amount: 150.50
  category: "Alimentação"
  account: "Conta Corrente"
```

#### Adicionar Receita via Serviço

```yaml
service: finance_manager.add_income
data:
  description: "Salário mensal"
  amount: 3000.00
  category: "Salário"
  account: "Conta Corrente"
```

### Automações Sugeridas

#### Alerta de Gastos Elevados

```yaml
automation:
  - alias: "Alerta Financeiro - Gastos Altos"
    trigger:
      - platform: state
        entity_id: sensor.finance_monthly_expenses
    condition:
      - condition: numeric_state
        entity_id: sensor.finance_monthly_expenses
        above: 2000
    action:
      - service: notify.mobile_app_seu_dispositivo
        data:
          title: "⚠️ Alerta Financeiro"
          message: "Despesas do mês ultrapassaram R$ 2.000!"
          data:
            priority: high
```

#### Resumo Financeiro Semanal

```yaml
automation:
  - alias: "Resumo Financeiro Semanal"
    trigger:
      - platform: time
        at: "09:00:00"
      - platform: time_pattern
        weekday: 1  # Segunda-feira
    action:
      - service: notify.telegram
        data:
          title: "📊 Resumo Financeiro Semanal"
          message: |
            💰 Saldo Total: R$ {{ states('sensor.finance_total_balance') }}
            📈 Receitas do Mês: R$ {{ states('sensor.finance_monthly_income') }}
            📉 Despesas do Mês: R$ {{ states('sensor.finance_monthly_expenses') }}
            💵 Saldo do Mês: R$ {{ states('sensor.finance_monthly_net') }}
```

#### Comando de Voz para Adicionar Despesas

```yaml
intent_script:
  AddExpenseIntent:
    speech:
      text: "Despesa de {{ amount }} reais em {{ category }} foi registrada"
    action:
      - service: finance_manager.add_expense
        data:
          description: "Despesa via comando de voz"
          amount: "{{ amount }}"
          category: "{{ category }}"
          account: "Conta Corrente"
```

### Dashboard Cards

#### Card de Resumo Financeiro

```yaml
type: entities
title: 💰 Resumo Financeiro
entities:
  - entity: sensor.finance_total_balance
    name: Saldo Total
    icon: mdi:wallet
  - entity: sensor.finance_monthly_income
    name: Receitas do Mês
    icon: mdi:trending-up
  - entity: sensor.finance_monthly_expenses
    name: Despesas do Mês
    icon: mdi:trending-down
  - entity: sensor.finance_monthly_net
    name: Saldo do Mês
    icon: mdi:chart-line
```

#### Card de Gráfico Histórico

```yaml
type: history-graph
title: 📈 Histórico Financeiro
entities:
  - sensor.finance_monthly_income
  - sensor.finance_monthly_expenses
hours_to_show: 720  # 30 dias
refresh_interval: 60
```

## Manutenção e Backup

### Backup dos Dados

#### Backup Automático

O banco de dados é armazenado em `/data/finance.db` dentro do container do add-on. Para backup automático:

1. **Configurar Backup do Home Assistant**
   - O backup padrão do Home Assistant inclui dados dos add-ons
   - Configure backups regulares nas configurações do sistema

2. **Backup Manual**
   ```bash
   # Copiar arquivo do banco
   docker cp addon_container:/data/finance.db ./backup_finance.db
   ```

#### Restauração de Backup

1. **Parar o Add-on**
   - Pare o add-on antes de restaurar

2. **Substituir Arquivo**
   ```bash
   # Restaurar arquivo do banco
   docker cp ./backup_finance.db addon_container:/data/finance.db
   ```

3. **Reiniciar Add-on**
   - Inicie o add-on novamente

### Atualizações

#### Atualização do Add-on

1. **Verificar Atualizações**
   - O Home Assistant notifica sobre atualizações disponíveis
   - Acesse a página do add-on para ver versões

2. **Processo de Atualização**
   - Clique em "Update" quando disponível
   - Aguarde a conclusão do processo
   - Verifique logs para confirmar sucesso

#### Migração de Dados

Para atualizações que requerem migração:

1. **Backup Preventivo**
   - Sempre faça backup antes de atualizar
   - Teste a restauração se necessário

2. **Verificação Pós-Atualização**
   - Confirme que todos os dados estão íntegros
   - Teste funcionalidades principais
   - Verifique integração com Home Assistant

### Monitoramento

#### Logs do Sistema

1. **Acessar Logs**
   - Na página do add-on, clique em "Log"
   - Use filtros por nível de severidade

2. **Logs Importantes**
   - Erros de conexão com banco de dados
   - Falhas na integração com Home Assistant
   - Problemas de autenticação

#### Métricas de Performance

1. **Uso de Recursos**
   - Monitore uso de CPU e memória
   - Verifique espaço em disco disponível

2. **Tempo de Resposta**
   - Interface web deve responder em < 2 segundos
   - APIs devem processar requisições rapidamente

## Solução de Problemas

### Problemas Comuns

#### Add-on Não Inicia

**Sintomas**: Add-on falha ao inicializar ou para inesperadamente

**Soluções**:
1. Verificar logs para mensagens de erro específicas
2. Confirmar que há espaço em disco suficiente
3. Reiniciar o Home Assistant Supervisor
4. Reinstalar o add-on se necessário

#### Interface Web Não Carrega

**Sintomas**: Página em branco ou erro 500

**Soluções**:
1. Verificar se o add-on está rodando
2. Confirmar porta configurada (padrão: 8080)
3. Limpar cache do navegador
4. Verificar logs para erros de template

#### Sensores Não Aparecem no Home Assistant

**Sintomas**: Sensores financeiros não são criados

**Soluções**:
1. Verificar conectividade entre add-on e Home Assistant
2. Reiniciar Home Assistant Core
3. Verificar logs de integração
4. Atualizar sensores manualmente via API

#### Dados Não Sincronizam

**Sintomas**: Transações não refletem nos sensores

**Soluções**:
1. Verificar se a integração está ativa
2. Forçar atualização via endpoint `/api/home-assistant/sensors/update`
3. Verificar logs de erro na integração
4. Reiniciar o add-on

### Diagnóstico Avançado

#### Verificação de Conectividade

```bash
# Testar API do add-on
curl http://localhost:8080/api/accounts

# Verificar banco de dados
sqlite3 /data/finance.db ".tables"
```

#### Debug de Integração

1. **Habilitar Debug**
   - Configure `log_level: debug` no add-on
   - Reinicie para aplicar mudanças

2. **Monitorar Logs**
   - Acompanhe logs em tempo real
   - Procure por mensagens de erro específicas

#### Teste de APIs

```bash
# Testar criação de transação
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Teste API",
    "amount": 10.00,
    "transaction_type": "expense",
    "transaction_date": "2025-06-13",
    "account_id": 1,
    "category_id": 1
  }'
```

## Suporte e Comunidade

### Recursos de Suporte

#### Documentação Oficial
- Manual completo no repositório GitHub
- Exemplos de configuração e automações
- FAQ com problemas comuns

#### Comunidade
- Fórum do Home Assistant
- Discord da comunidade
- Issues no GitHub para bugs e sugestões

### Contribuindo

#### Reportar Bugs
1. Verificar se o bug já foi reportado
2. Incluir logs relevantes
3. Descrever passos para reproduzir
4. Especificar versão do Home Assistant e add-on

#### Sugerir Melhorias
1. Abrir issue no GitHub
2. Descrever funcionalidade desejada
3. Explicar caso de uso
4. Considerar impacto em performance

#### Desenvolvimento
1. Fork do repositório
2. Criar branch para feature
3. Implementar mudanças
4. Submeter pull request

### Roadmap

#### Próximas Funcionalidades
- Importação de extratos bancários
- Relatórios avançados com gráficos
- Orçamento com alertas automáticos
- Integração com bancos via Open Banking
- App mobile complementar

#### Melhorias Planejadas
- Performance otimizada para grandes volumes
- Interface redesenhada
- Suporte a múltiplas moedas
- Backup automático na nuvem
- Análise preditiva de gastos

Este manual fornece uma base sólida para utilização completa do Home Finance Manager. Para dúvidas específicas ou problemas não cobertos, consulte a documentação online ou entre em contato com a comunidade de usuários.


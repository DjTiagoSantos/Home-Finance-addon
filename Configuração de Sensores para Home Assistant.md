# Configuração de Sensores para Home Assistant

## Sensores Disponíveis

O add-on Home Finance Manager expõe automaticamente os seguintes sensores no Home Assistant:

### 1. Sensor de Saldo Total
- **Entity ID**: `sensor.finance_total_balance`
- **Nome**: Saldo Total
- **Descrição**: Soma de todos os saldos das contas ativas
- **Unidade**: BRL (Real Brasileiro)
- **Ícone**: mdi:wallet

### 2. Sensor de Receitas do Mês
- **Entity ID**: `sensor.finance_monthly_income`
- **Nome**: Receitas do Mês
- **Descrição**: Total de receitas do mês atual
- **Unidade**: BRL (Real Brasileiro)
- **Ícone**: mdi:trending-up

### 3. Sensor de Despesas do Mês
- **Entity ID**: `sensor.finance_monthly_expenses`
- **Nome**: Despesas do Mês
- **Descrição**: Total de despesas do mês atual
- **Unidade**: BRL (Real Brasileiro)
- **Ícone**: mdi:trending-down

### 4. Sensor de Saldo do Mês
- **Entity ID**: `sensor.finance_monthly_net`
- **Nome**: Saldo do Mês
- **Descrição**: Diferença entre receitas e despesas do mês atual
- **Unidade**: BRL (Real Brasileiro)
- **Ícone**: mdi:chart-line

### 5. Sensor de Transações do Mês
- **Entity ID**: `sensor.finance_monthly_transactions`
- **Nome**: Transações do Mês
- **Descrição**: Número total de transações do mês atual
- **Ícone**: mdi:swap-horizontal

### 6. Sensor da Última Transação
- **Entity ID**: `sensor.finance_last_transaction`
- **Nome**: Última Transação
- **Descrição**: Informações da transação mais recente
- **Ícone**: mdi:receipt

## Serviços Disponíveis

### 1. Adicionar Despesa
- **Serviço**: `finance_manager.add_expense`
- **Descrição**: Adiciona uma nova despesa ao sistema
- **Parâmetros**:
  - `description`: Descrição da despesa (obrigatório)
  - `amount`: Valor da despesa (obrigatório)
  - `category`: Nome da categoria (obrigatório)
  - `account`: Nome da conta (opcional, padrão: "Conta Corrente")

**Exemplo de uso**:
```yaml
service: finance_manager.add_expense
data:
  description: "Compra no supermercado"
  amount: 150.50
  category: "Alimentação"
  account: "Conta Corrente"
```

### 2. Adicionar Receita
- **Serviço**: `finance_manager.add_income`
- **Descrição**: Adiciona uma nova receita ao sistema
- **Parâmetros**:
  - `description`: Descrição da receita (obrigatório)
  - `amount`: Valor da receita (obrigatório)
  - `category`: Nome da categoria (obrigatório)
  - `account`: Nome da conta (opcional, padrão: "Conta Corrente")

**Exemplo de uso**:
```yaml
service: finance_manager.add_income
data:
  description: "Salário mensal"
  amount: 3000.00
  category: "Salário"
  account: "Conta Corrente"
```

## Exemplos de Automações

### 1. Notificação de Gastos Altos
```yaml
automation:
  - alias: "Alerta de Gasto Alto"
    trigger:
      - platform: state
        entity_id: sensor.finance_monthly_expenses
    condition:
      - condition: numeric_state
        entity_id: sensor.finance_monthly_expenses
        above: 2000
    action:
      - service: notify.mobile_app
        data:
          title: "Alerta Financeiro"
          message: "Despesas do mês ultrapassaram R$ 2.000!"
```

### 2. Resumo Financeiro Diário
```yaml
automation:
  - alias: "Resumo Financeiro Diário"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.telegram
        data:
          title: "Resumo Financeiro"
          message: >
            Saldo Total: {{ states('sensor.finance_total_balance') }} BRL
            Receitas do Mês: {{ states('sensor.finance_monthly_income') }} BRL
            Despesas do Mês: {{ states('sensor.finance_monthly_expenses') }} BRL
            Saldo do Mês: {{ states('sensor.finance_monthly_net') }} BRL
```

### 3. Adicionar Despesa por Comando de Voz
```yaml
intent_script:
  AddExpense:
    speech:
      text: "Despesa de {{ amount }} reais em {{ category }} foi adicionada"
    action:
      - service: finance_manager.add_expense
        data:
          description: "Despesa via comando de voz"
          amount: "{{ amount }}"
          category: "{{ category }}"
```

## Dashboard Cards

### 1. Card de Resumo Financeiro
```yaml
type: entities
title: Resumo Financeiro
entities:
  - entity: sensor.finance_total_balance
    name: Saldo Total
  - entity: sensor.finance_monthly_income
    name: Receitas do Mês
  - entity: sensor.finance_monthly_expenses
    name: Despesas do Mês
  - entity: sensor.finance_monthly_net
    name: Saldo do Mês
```

### 2. Card de Gráfico de Despesas
```yaml
type: history-graph
title: Histórico de Despesas
entities:
  - sensor.finance_monthly_expenses
hours_to_show: 168
refresh_interval: 60
```

### 3. Card de Última Transação
```yaml
type: entity
entity: sensor.finance_last_transaction
attribute: amount
name: Última Transação
icon: mdi:receipt
```

## Configuração Avançada

### Personalização de Sensores
Os sensores podem ser personalizados através do arquivo `customize.yaml`:

```yaml
sensor.finance_total_balance:
  friendly_name: "Meu Saldo Total"
  icon: mdi:bank

sensor.finance_monthly_expenses:
  friendly_name: "Gastos do Mês"
  icon: mdi:credit-card
```

### Grupos de Sensores
```yaml
group:
  finance_sensors:
    name: "Sensores Financeiros"
    entities:
      - sensor.finance_total_balance
      - sensor.finance_monthly_income
      - sensor.finance_monthly_expenses
      - sensor.finance_monthly_net
```

## Solução de Problemas

### Sensores não aparecem
1. Verifique se o add-on está rodando corretamente
2. Reinicie o Home Assistant
3. Verifique os logs do add-on para erros

### Serviços não funcionam
1. Verifique se as categorias e contas existem no sistema
2. Confirme que os nomes estão corretos (case-sensitive)
3. Verifique os logs para mensagens de erro

### Dados não atualizam
1. Os sensores são atualizados automaticamente após cada transação
2. Use o serviço `finance_manager.update_sensors` para atualização manual
3. Verifique a conectividade entre o add-on e o Home Assistant


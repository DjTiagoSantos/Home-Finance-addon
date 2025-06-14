// Configuração da API
const API_BASE_URL = '/api';

// Estado da aplicação
let currentSection = 'dashboard';
let accounts = [];
let categories = [];
let transactions = [];
let currentPage = 1;
let totalPages = 1;

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await loadInitialData();
    showSection('dashboard');
    updateDashboard();
}

function setupEventListeners() {
    // Menu lateral
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.dataset.section;
            showSection(section);
        });
    });

    // Botões de adicionar
    document.getElementById('add-transaction-btn').addEventListener('click', () => openTransactionModal());
    document.getElementById('add-account-btn').addEventListener('click', () => openAccountModal());
    document.getElementById('add-category-btn').addEventListener('click', () => openCategoryModal());

    // Modais
    setupModalEvents();

    // Formulários
    setupFormEvents();

    // Filtros
    setupFilterEvents();

    // Tabs de categorias
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadCategories(this.dataset.type);
        });
    });

    // Data atual para transações
    document.getElementById('transaction-date').value = new Date().toISOString().split('T')[0];
}

function setupModalEvents() {
    // Fechar modais
    document.querySelectorAll('[data-modal]').forEach(btn => {
        btn.addEventListener('click', function() {
            closeModal(this.dataset.modal);
        });
    });

    // Fechar modal clicando fora
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
}

function setupFormEvents() {
    // Formulário de transação
    document.getElementById('transaction-form').addEventListener('submit', handleTransactionSubmit);
    
    // Formulário de conta
    document.getElementById('account-form').addEventListener('submit', handleAccountSubmit);
    
    // Formulário de categoria
    document.getElementById('category-form').addEventListener('submit', handleCategorySubmit);

    // Mudança de tipo de transação
    document.getElementById('transaction-type').addEventListener('change', function() {
        loadCategoriesForSelect(this.value);
    });
}

function setupFilterEvents() {
    const filters = ['account-filter', 'category-filter', 'type-filter'];
    filters.forEach(filterId => {
        document.getElementById(filterId).addEventListener('change', () => {
            currentPage = 1;
            loadTransactions();
        });
    });
}

// Navegação entre seções
function showSection(sectionName) {
    // Atualizar menu
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Atualizar conteúdo
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');

    // Atualizar título
    const titles = {
        dashboard: 'Dashboard',
        transactions: 'Transações',
        accounts: 'Contas',
        categories: 'Categorias',
        reports: 'Relatórios'
    };
    document.getElementById('page-title').textContent = titles[sectionName];

    currentSection = sectionName;

    // Carregar dados específicos da seção
    switch(sectionName) {
        case 'transactions':
            loadTransactions();
            break;
        case 'accounts':
            loadAccounts();
            break;
        case 'categories':
            loadCategories('expense');
            break;
    }
}

// Carregamento de dados
async function loadInitialData() {
    try {
        await Promise.all([
            loadAccounts(),
            loadCategories(),
            loadTransactions()
        ]);
        populateSelects();
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
        showError('Erro ao carregar dados da aplicação');
    }
}

async function loadAccounts() {
    try {
        const response = await fetch(`${API_BASE_URL}/accounts`);
        accounts = await response.json();
        
        if (currentSection === 'accounts') {
            renderAccounts();
        }
        
        return accounts;
    } catch (error) {
        console.error('Erro ao carregar contas:', error);
        showError('Erro ao carregar contas');
    }
}

async function loadCategories(type = null) {
    try {
        const url = type ? `${API_BASE_URL}/categories?type=${type}` : `${API_BASE_URL}/categories`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (type) {
            renderCategories(data);
        } else {
            categories = data;
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
        showError('Erro ao carregar categorias');
    }
}

async function loadTransactions() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 20
        });

        // Adicionar filtros
        const accountFilter = document.getElementById('account-filter').value;
        const categoryFilter = document.getElementById('category-filter').value;
        const typeFilter = document.getElementById('type-filter').value;

        if (accountFilter) params.append('account_id', accountFilter);
        if (categoryFilter) params.append('category_id', categoryFilter);
        if (typeFilter) params.append('type', typeFilter);

        const response = await fetch(`${API_BASE_URL}/transactions?${params}`);
        const data = await response.json();
        
        transactions = data.transactions;
        totalPages = data.pages;
        
        if (currentSection === 'transactions') {
            renderTransactions();
            renderPagination();
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao carregar transações:', error);
        showError('Erro ao carregar transações');
    }
}

async function loadSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/summary`);
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        showError('Erro ao carregar resumo financeiro');
    }
}

async function loadExpensesByCategory() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/expenses-by-category`);
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar despesas por categoria:', error);
        return [];
    }
}

// Renderização
function renderAccounts() {
    const container = document.getElementById('accounts-grid');
    
    if (accounts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-university"></i>
                <h3>Nenhuma conta encontrada</h3>
                <p>Adicione sua primeira conta para começar</p>
            </div>
        `;
        return;
    }

    container.innerHTML = accounts.map(account => `
        <div class="card account-card">
            <div class="account-header">
                <div>
                    <div class="account-type">${getAccountTypeName(account.account_type)}</div>
                    <div class="account-name">${account.name}</div>
                </div>
                <div class="account-actions">
                    <button class="btn btn-sm" onclick="editAccount(${account.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
            <div class="account-balance">
                ${formatCurrency(account.current_balance)}
            </div>
        </div>
    `).join('');
}

function renderCategories(categoriesData) {
    const container = document.getElementById('categories-grid');
    
    if (categoriesData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-tags"></i>
                <h3>Nenhuma categoria encontrada</h3>
                <p>Adicione categorias para organizar suas transações</p>
            </div>
        `;
        return;
    }

    container.innerHTML = categoriesData.map(category => `
        <div class="category-item" onclick="editCategory(${category.id})">
            <div class="category-icon" style="background-color: ${category.color}">
                <i class="${category.icon}"></i>
            </div>
            <div class="category-name">${category.name}</div>
        </div>
    `).join('');
}

function renderTransactions() {
    const container = document.getElementById('transactions-list');
    
    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exchange-alt"></i>
                <h3>Nenhuma transação encontrada</h3>
                <p>Adicione sua primeira transação</p>
            </div>
        `;
        return;
    }

    container.innerHTML = transactions.map(transaction => `
        <div class="transaction-item" onclick="editTransaction(${transaction.id})">
            <div class="transaction-info">
                <div class="transaction-icon" style="background-color: ${getCategoryColor(transaction.category_id)}">
                    <i class="${getCategoryIcon(transaction.category_id)}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${transaction.description}</h4>
                    <div class="transaction-meta">
                        ${transaction.category_name} • ${transaction.account_name}
                    </div>
                </div>
            </div>
            <div class="transaction-amount ${transaction.transaction_type}">
                <div class="amount">
                    ${transaction.transaction_type === 'income' ? '+' : '-'}${formatCurrency(Math.abs(transaction.amount))}
                </div>
                <div class="transaction-date">${formatDate(transaction.transaction_date)}</div>
            </div>
        </div>
    `).join('');
}

function renderPagination() {
    const container = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHTML = '';
    
    // Botão anterior
    paginationHTML += `
        <button ${currentPage === 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    // Números das páginas
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage || i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            paginationHTML += `
                <button class="${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            paginationHTML += '<span>...</span>';
        }
    }
    
    // Botão próximo
    paginationHTML += `
        <button ${currentPage === totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    container.innerHTML = paginationHTML;
}

// Dashboard
async function updateDashboard() {
    try {
        const summary = await loadSummary();
        
        if (summary) {
            document.getElementById('total-balance').textContent = formatCurrency(summary.total_balance);
            document.getElementById('monthly-income').textContent = formatCurrency(summary.monthly_income);
            document.getElementById('monthly-expenses').textContent = formatCurrency(summary.monthly_expenses);
            document.getElementById('monthly-net').textContent = formatCurrency(summary.monthly_net);
        }

        // Carregar gráfico de despesas
        const expensesData = await loadExpensesByCategory();
        renderExpensesChart(expensesData);

        // Carregar transações recentes
        await loadRecentTransactions();
        
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
    }
}

async function loadRecentTransactions() {
    try {
        const response = await fetch(`${API_BASE_URL}/transactions?per_page=5`);
        const data = await response.json();
        renderRecentTransactions(data.transactions);
    } catch (error) {
        console.error('Erro ao carregar transações recentes:', error);
    }
}

function renderRecentTransactions(recentTransactions) {
    const container = document.getElementById('recent-transactions-list');
    
    if (recentTransactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhuma transação recente</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recentTransactions.map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-icon" style="background-color: ${getCategoryColor(transaction.category_id)}">
                    <i class="${getCategoryIcon(transaction.category_id)}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${transaction.description}</h4>
                    <div class="transaction-meta">
                        ${transaction.category_name} • ${formatDate(transaction.transaction_date)}
                    </div>
                </div>
            </div>
            <div class="transaction-amount ${transaction.transaction_type}">
                <div class="amount">
                    ${transaction.transaction_type === 'income' ? '+' : '-'}${formatCurrency(Math.abs(transaction.amount))}
                </div>
            </div>
        </div>
    `).join('');
}

function renderExpensesChart(data) {
    const ctx = document.getElementById('expenses-chart').getContext('2d');
    
    if (window.expensesChart) {
        window.expensesChart.destroy();
    }

    if (data.length === 0) {
        ctx.canvas.style.display = 'none';
        return;
    }

    ctx.canvas.style.display = 'block';

    window.expensesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.amount),
                backgroundColor: data.map(item => item.color),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Modais
function openTransactionModal(transaction = null) {
    const modal = document.getElementById('transaction-modal');
    const form = document.getElementById('transaction-form');
    const title = document.getElementById('transaction-modal-title');
    
    if (transaction) {
        title.textContent = 'Editar Transação';
        populateTransactionForm(transaction);
    } else {
        title.textContent = 'Nova Transação';
        form.reset();
        document.getElementById('transaction-date').value = new Date().toISOString().split('T')[0];
        loadCategoriesForSelect('expense');
    }
    
    modal.classList.add('active');
}

function openAccountModal(account = null) {
    const modal = document.getElementById('account-modal');
    const form = document.getElementById('account-form');
    const title = document.getElementById('account-modal-title');
    
    if (account) {
        title.textContent = 'Editar Conta';
        populateAccountForm(account);
    } else {
        title.textContent = 'Nova Conta';
        form.reset();
    }
    
    modal.classList.add('active');
}

function openCategoryModal(category = null) {
    const modal = document.getElementById('category-modal');
    const form = document.getElementById('category-form');
    const title = document.getElementById('category-modal-title');
    
    if (category) {
        title.textContent = 'Editar Categoria';
        populateCategoryForm(category);
    } else {
        title.textContent = 'Nova Categoria';
        form.reset();
    }
    
    modal.classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Formulários
async function handleTransactionSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE_URL}/transactions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeModal('transaction-modal');
            await loadTransactions();
            await loadAccounts();
            updateDashboard();
            showSuccess('Transação salva com sucesso!');
        } else {
            throw new Error('Erro ao salvar transação');
        }
    } catch (error) {
        console.error('Erro ao salvar transação:', error);
        showError('Erro ao salvar transação');
    }
}

async function handleAccountSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE_URL}/accounts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeModal('account-modal');
            await loadAccounts();
            populateSelects();
            showSuccess('Conta salva com sucesso!');
        } else {
            throw new Error('Erro ao salvar conta');
        }
    } catch (error) {
        console.error('Erro ao salvar conta:', error);
        showError('Erro ao salvar conta');
    }
}

async function handleCategorySubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE_URL}/categories`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeModal('category-modal');
            await loadCategories();
            populateSelects();
            const activeTab = document.querySelector('.tab-btn.active').dataset.type;
            loadCategories(activeTab);
            showSuccess('Categoria salva com sucesso!');
        } else {
            throw new Error('Erro ao salvar categoria');
        }
    } catch (error) {
        console.error('Erro ao salvar categoria:', error);
        showError('Erro ao salvar categoria');
    }
}

// Utilitários
function populateSelects() {
    // Popular select de contas
    const accountSelects = ['transaction-account', 'account-filter'];
    accountSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        const currentValue = select.value;
        
        select.innerHTML = selectId.includes('filter') ? '<option value="">Todas as Contas</option>' : '';
        
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = account.name;
            select.appendChild(option);
        });
        
        select.value = currentValue;
    });

    // Popular select de categorias para filtro
    const categoryFilter = document.getElementById('category-filter');
    const currentCategoryValue = categoryFilter.value;
    
    categoryFilter.innerHTML = '<option value="">Todas as Categorias</option>';
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        categoryFilter.appendChild(option);
    });
    
    categoryFilter.value = currentCategoryValue;
}

function loadCategoriesForSelect(type) {
    const select = document.getElementById('transaction-category');
    select.innerHTML = '';
    
    const filteredCategories = categories.filter(cat => cat.category_type === type);
    
    filteredCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function changePage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        loadTransactions();
    }
}

// Funções auxiliares
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function getAccountTypeName(type) {
    const types = {
        checking: 'Conta Corrente',
        savings: 'Poupança',
        credit_card: 'Cartão de Crédito',
        cash: 'Dinheiro'
    };
    return types[type] || type;
}

function getCategoryColor(categoryId) {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.color : '#6c757d';
}

function getCategoryIcon(categoryId) {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.icon : 'fas fa-tag';
}

// Notificações
function showSuccess(message) {
    // Implementar sistema de notificações
    console.log('Sucesso:', message);
}

function showError(message) {
    // Implementar sistema de notificações
    console.error('Erro:', message);
}

// Funções de edição (placeholder)
function editTransaction(id) {
    console.log('Editar transação:', id);
}

function editAccount(id) {
    console.log('Editar conta:', id);
}

function editCategory(id) {
    console.log('Editar categoria:', id);
}


let currentUser = null;

document.getElementById('login-btn').addEventListener('click', login);
document.getElementById('transfer-btn').addEventListener('click', transferFunds);
document.getElementById('load-transactions-btn').addEventListener('click', loadTransactions);
document.getElementById('logout-btn').addEventListener('click', logout);

function login() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        currentUser = username;
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('account-section').style.display = 'block';
        document.getElementById('login-message').textContent = '';
        loadAccountDetails();
      } else {
        document.getElementById('login-message').textContent = data.message;
      }
    })
    .catch(() => {
      document.getElementById('login-message').textContent = 'Error contacting server.';
    });
}

function loadAccountDetails() {
  fetch(`/api/accounts/${currentUser}`)
    .then(res => res.json())
    .then(data => {
      if (!data.error) {
        document.getElementById('account-info').innerHTML = `
          <strong>Account Number:</strong> ${data.account_number} <br />
          <strong>Balance:</strong> ₹${data.balance.toFixed(2)} <br />
          <strong>Account Type:</strong> ${data.account_type}
        `;
      } else {
        document.getElementById('account-info').textContent = data.error;
      }
    });
}

function transferFunds() {
  const toUser = document.getElementById('transfer-to').value.trim();
  const amount = parseFloat(document.getElementById('transfer-amount').value);

  if (!toUser || isNaN(amount) || amount <= 0) {
    document.getElementById('transfer-message').textContent = 'Enter valid recipient and amount.';
    return;
  }

  fetch('/api/transfer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: currentUser, to: toUser, amount: amount })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById('transfer-message').style.color = 'green';
        document.getElementById('transfer-message').textContent = 'Transfer successful!';
        loadAccountDetails();
        loadTransactions();
      } else {
        document.getElementById('transfer-message').style.color = 'red';
        document.getElementById('transfer-message').textContent = data.error || 'Transfer failed.';
      }
    })
    .catch(() => {
      document.getElementById('transfer-message').style.color = 'red';
      document.getElementById('transfer-message').textContent = 'Error contacting server.';
    });
}

function loadTransactions() {
  fetch(`/api/transactions/${currentUser}`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('transaction-list');
      list.innerHTML = '';
      if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = '<li>No transactions found.</li>';
        return;
      }
      data.forEach(txn => {
        let desc = '';
        if (txn.type === 'debit') {
          desc = `Sent ₹${txn.amount} to ${txn.to}`;
        } else if (txn.type === 'credit') {
          desc = `Received ₹${txn.amount} from ${txn.from}`;
        }
        const li = document.createElement('li');
        li.textContent = desc;
        list.appendChild(li);
      });
    });
}

function logout() {
  currentUser = null;
  document.getElementById('account-section').style.display = 'none';
  document.getElementById('login-section').style.display = 'block';
  document.getElementById('login-message').textContent = '';
  document.getElementById('transfer-message').textContent = '';
  document.getElementById('transaction-list').innerHTML = '';
  document.getElementById('account-info').textContent = '';
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
  document.getElementById('transfer-to').value = '';
  document.getElementById('transfer-amount').value = '';
}

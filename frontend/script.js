let currentUser = '';

function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  fetch('http://127.0.0.1:5000/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      currentUser = username;
      document.getElementById('loginSection').style.display = 'none';
      document.getElementById('dashboard').style.display = 'block';
      document.getElementById('user').innerText = username;
      loadAccount();
      loadTransactions();
    } else {
      document.getElementById('loginMsg').innerText = data.message;
    }
  });
}

function loadAccount() {
  fetch(`http://127.0.0.1:5000/api/account/${currentUser}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById('accNo').innerText = data.account_no;
      document.getElementById('balance').innerText = data.balance;
    });
}

function transfer() {
  const to = document.getElementById('toUser').value;
  const amount = document.getElementById('amount').value;

  fetch('http://127.0.0.1:5000/api/transfer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({from: currentUser, to, amount})
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.getElementById('transferMsg').innerText = "Transfer successful!";
      loadAccount();
      loadTransactions();
    } else {
      document.getElementById('transferMsg').innerText = data.error;
    }
  });
}

function loadTransactions() {
  fetch(`http://127.0.0.1:5000/api/transactions/${currentUser}`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('txns');
      list.innerHTML = '';
      data.forEach(txn => {
        const li = document.createElement('li');
        li.innerText = `${txn.from} sent ₹${txn.amount} to ${txn.to}`;
        list.appendChild(li);
      });
    });
}

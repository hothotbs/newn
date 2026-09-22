
const hamburger = document.querySelector('.hamburger')
const sidebar = document.querySelector('.sidebar-wrapper')
const close = document.querySelector('.close-sidebar')



hamburger.addEventListener('click', () => {
  sidebar.classList.add('show')


})

close.addEventListener('click', () => {
  sidebar.classList.remove('show')


})



const showHistory = document.querySelector('.show-history')
const historyList = document.querySelector('.history_list-wrapper')
const historyHeadWrapper = document.querySelector('.history-head-wrapper')


if (window.location.pathname === "/users/withdrawal-history" || window.location.pathname === "/users/deposit-history") {
  historyList.classList.remove('hide-list')
}



historyHeadWrapper.addEventListener('click', () => {
  historyList.classList.toggle('hide-list')
  if (historyList.classList.contains('hide-list')) {
    showHistory.innerHTML = '<i class="bi bi-caret-right-fill"></i>'
  } else {
    showHistory.innerHTML = '<i class="bi bi-caret-down-fill"></i>'
  }
})


const walletAddress = document.querySelector('.wallet-address')
const copyText = document.querySelector('.copy-btn')

copyText.addEventListener('click', () => {
  const wallet_address = walletAddress.textContent
  navigator.clipboard.writeText(wallet_address).then(() => {
    copyText.disabled = true;
    copyText.textContent = 'copied!';
    setTimeout(() => {
      copyText.disabled = false;
      copyText.textContent = 'Copy';
    }, 3000)
  })
})




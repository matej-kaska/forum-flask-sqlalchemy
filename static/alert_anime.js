if (document.querySelector('.js-alert')) {
  document.querySelectorAll('.js-alert').forEach(function($el) {
    setTimeout(() => {
      $el.classList.remove('show');
    }, 2000);
  });
}
function showToast(msg){
  const el = document.getElementById("toast");
  if(!el) return;
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(()=> el.classList.remove("show"), 2200);
}

function openModal(title, html){
  const overlay = document.getElementById("modalOverlay");
  const titleEl = document.getElementById("modalTitle");
  const bodyEl = document.getElementById("modalBody");
  if(!overlay || !titleEl || !bodyEl) return;
  titleEl.textContent = title;
  bodyEl.innerHTML = html;
  overlay.classList.add("show");
  
  // Добавляем анимацию появления
  const modal = overlay.querySelector('.modal');
  if(modal) {
    modal.style.animation = 'none';
    modal.offsetHeight; // триггер reflow
    modal.style.animation = 'modalSlideUp 0.4s ease';
  }
}

function closeModal(){
  const overlay = document.getElementById("modalOverlay");
  if(overlay) {
    // Добавляем анимацию закрытия
    const modal = overlay.querySelector('.modal');
    if(modal) {
      modal.style.animation = 'modalSlideDown 0.3s ease';
      setTimeout(() => {
        overlay.classList.remove("show");
      }, 250);
    } else {
      overlay.classList.remove("show");
    }
  }
}

// Добавляем анимацию для модального окна при закрытии
const style = document.createElement('style');
style.textContent = `
  @keyframes modalSlideDown {
    from {
      opacity: 1;
      transform: translateY(0);
    }
    to {
      opacity: 0;
      transform: translateY(30px);
    }
  }
`;
document.head.appendChild(style);
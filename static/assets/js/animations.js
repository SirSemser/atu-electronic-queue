// Анимации и исправление языка
(function() {
    // Исправление для языка
    function fixLanguageButtons() {
        const langButtons = document.querySelectorAll('[data-lang-btn]');
        const currentLang = document.documentElement.lang || 'kk';
        
        langButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-lang-btn') === currentLang) {
                btn.classList.add('active');
            }
            
            // Добавляем обработчик, если его нет
            if (!btn.hasAttribute('data-handler')) {
                const originalOnClick = btn.onclick;
                btn.setAttribute('data-handler', 'true');
                
                btn.onclick = function(e) {
                    e.preventDefault();
                    const lang = this.getAttribute('data-lang-btn');
                    
                    if (window.I18N && window.I18N.setLang) {
                        window.I18N.setLang(lang);
                    }
                    
                    // Обновляем активный класс
                    langButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Показываем уведомление
                    showCustomToast('Тіл ауыстырылды', 'success');
                    
                    return false;
                };
            }
        });
    }
    
    // Свои уведомления
    function showCustomToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = message;
            toast.className = 'toast ' + type;
            toast.classList.add('show');
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }
    }
    
    // Принудительное применение CSS
    function forceCSS() {
        // Добавляем стили напрямую, если CSS не загрузился
        const style = document.createElement('style');
        style.textContent = `
            body { 
                background: #f8fafc !important;
                color: #0f172a !important;
                font-family: 'Inter', sans-serif !important;
            }
            .card {
                background: white !important;
                border-radius: 24px !important;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
                padding: 32px !important;
            }
            .btn {
                background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 14px 24px !important;
                color: white !important;
                font-weight: 600 !important;
                cursor: pointer !important;
            }
            .btn.secondary {
                background: white !important;
                color: #0f172a !important;
                border: 1px solid #e2e8f0 !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Запускаем после загрузки
    document.addEventListener('DOMContentLoaded', function() {
        fixLanguageButtons();
        forceCSS();
    });
    
    // Наблюдаем за изменениями в DOM
    const observer = new MutationObserver(function() {
        fixLanguageButtons();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
// Simple i18n helper for ATU
// Language stored in localStorage: kz | ru | en

const I18N = (() => {
  const SUPPORTED = ["kz", "ru", "en"];
  let dict = {};
  let lang = localStorage.getItem("atu_lang") || "kz";

  function setLang(newLang){
    if(!SUPPORTED.includes(newLang)) newLang = "kz";
    lang = newLang;
    localStorage.setItem("atu_lang", lang);
    load();
  }

  async function load(){
    try{
      // 1) base texts from json
      const res = await fetch(`/static/config/texts.${lang}.json`, { cache: "no-store" });
      dict = await res.json();

      // 2) override texts from DB config
      try{
        const r2 = await fetch(`/api/config/`, { cache: "no-store" });
        if(r2.ok){
          const cfg = await r2.json();
          const overrides = cfg?.ui?.[lang] || {};
          dict = { ...dict, ...overrides }; // overrides win
        }
      }catch(e){}

      render();
    }catch(e){
      console.error("i18n load error:", e);
    }
  }

  function t(key){
    return dict[key] ?? `⟦${key}⟧`;
  }

  function render(){
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.dataset.i18n;
      el.textContent = t(key);
    });

    document.querySelectorAll("[data-i18n-html]").forEach(el => {
      const key = el.dataset.i18nHtml;
      el.innerHTML = t(key);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.dataset.i18nPlaceholder;
      el.placeholder = t(key);
    });

    document.querySelectorAll("[data-i18n-title]").forEach(el => {
      const key = el.dataset.i18nTitle;
      el.title = t(key);
    });

    document.querySelectorAll("[data-lang-btn]").forEach(btn => {
      btn.classList.toggle("active", btn.getAttribute("data-lang-btn") === lang);
    });
  }

  function getLang(){
    return lang;
  }

  return { load, setLang, t, getLang };
})();

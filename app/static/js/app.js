/* Lunara — interações leves, sem dependências. */
(function () {
  "use strict";

  var root = document.documentElement;
  var isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  /* ------------------------------------------------------------------ */
  /* Onboarding em etapas                                                */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll("[data-onboarding]").forEach(function (form) {
    var steps = Array.prototype.slice.call(form.querySelectorAll("[data-step]"));
    if (!steps.length) return;

    var next = form.querySelector("[data-next]");
    var prev = form.querySelector("[data-prev]");
    var submit = form.querySelector("[data-submit]");
    var fill =
      form.querySelector("[data-progress]") ||
      document.querySelector("[data-progress]");
    var label =
      form.querySelector("[data-progress-label]") ||
      document.querySelector("[data-progress-label]");
    var current = 0;

    function fieldsOf(step) {
      return Array.prototype.slice
        .call(step.querySelectorAll("input, select, textarea"))
        .filter(function (field) {
          return !field.disabled && field.type !== "hidden";
        });
    }

    function validate(step) {
      var fields = fieldsOf(step);
      for (var i = 0; i < fields.length; i += 1) {
        if (!fields[i].checkValidity()) {
          fields[i].reportValidity();
          return false;
        }
      }
      return true;
    }

    function render() {
      steps.forEach(function (step, index) {
        step.hidden = index !== current;
      });
      if (prev) prev.hidden = current === 0;
      if (next) next.hidden = current === steps.length - 1;
      if (submit) submit.hidden = current !== steps.length - 1;
      if (fill) fill.style.width = ((current + 1) / steps.length) * 100 + "%";
      if (label) label.textContent = "Passo " + (current + 1) + " de " + steps.length;

      var field = fieldsOf(steps[current])[0];
      if (field) {
        window.setTimeout(function () {
          field.focus({ preventScroll: true });
        }, 80);
      }
    }

    if (next) {
      next.addEventListener("click", function () {
        if (!validate(steps[current])) return;
        current = Math.min(current + 1, steps.length - 1);
        render();
      });
    }

    if (prev) {
      prev.addEventListener("click", function () {
        current = Math.max(current - 1, 0);
        render();
      });
    }

    form.addEventListener("submit", function (event) {
      for (var i = 0; i < steps.length; i += 1) {
        if (!validate(steps[i])) {
          event.preventDefault();
          current = i;
          render();
          return;
        }
      }
    });

    form.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" || event.target.tagName === "TEXTAREA") return;
      if (current < steps.length - 1) {
        event.preventDefault();
        if (next) next.click();
      }
    });

    render();
  });

  /* ------------------------------------------------------------------ */
  /* Mostrar / esconder senha                                            */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll("[data-toggle-password]").forEach(function (button) {
    button.addEventListener("click", function () {
      var wrap = button.closest(".input-wrap") || button.parentElement;
      var input = wrap ? wrap.querySelector("input") : null;
      if (!input) return;
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-pressed", show ? "true" : "false");
      button.setAttribute("aria-label", show ? "Ocultar senha" : "Mostrar senha");
      button.classList.toggle("is-visible", show);
    });
  });

  /* ------------------------------------------------------------------ */
  /* Mensagens flash                                                     */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll("[data-dismiss]").forEach(function (button) {
    button.addEventListener("click", function () {
      var flash = button.closest(".flash");
      if (!flash) return;
      flash.classList.add("is-leaving");
      window.setTimeout(function () {
        flash.remove();
      }, 190);
    });
  });

  document.querySelectorAll(".flash-stack .flash").forEach(function (flash) {
    window.setTimeout(function () {
      if (!flash.isConnected) return;
      flash.classList.add("is-leaving");
      window.setTimeout(function () {
        flash.remove();
      }, 190);
    }, 8000);
  });

  /* ------------------------------------------------------------------ */
  /* Confirmação de ações destrutivas                                    */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var message = form.getAttribute("data-confirm") || "Tem certeza?";
      if (!window.confirm(message)) event.preventDefault();
    });
  });

  /* ------------------------------------------------------------------ */
  /* Instalação do PWA                                                   */
  /* ------------------------------------------------------------------ */
  var installButtons = Array.prototype.slice.call(
    document.querySelectorAll("[data-install]")
  );
  var deferredPrompt = null;

  function showInstall(visible) {
    installButtons.forEach(function (button) {
      button.hidden = !visible;
      button.classList.toggle("is-visible", visible);
    });
  }

  if (installButtons.length) {
    showInstall(false);

    window.addEventListener("beforeinstallprompt", function (event) {
      event.preventDefault();
      deferredPrompt = event;
      showInstall(true);
    });

    installButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          deferredPrompt.userChoice.then(function (choice) {
            if (choice.outcome === "accepted") showInstall(false);
            deferredPrompt = null;
          });
          return;
        }

        var ios = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
        window.alert(
          ios
            ? "No iPhone: toque em Compartilhar e escolha “Adicionar à Tela de Início”."
            : "No menu do navegador, escolha “Instalar app” ou “Adicionar à tela inicial”."
        );
      });
    });

    window.addEventListener("appinstalled", function () {
      deferredPrompt = null;
      showInstall(false);
    });

    if (isStandalone) showInstall(false);
  }

  /* ------------------------------------------------------------------ */
  /* Service worker                                                      */
  /* ------------------------------------------------------------------ */
  if (
    "serviceWorker" in navigator &&
    (window.location.protocol === "https:" ||
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1")
  ) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function (error) {
        console.warn("Lunara: service worker não registrado.", error);
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Lembretes locais                                                    */
  /* ------------------------------------------------------------------ */
  var body = document.body;
  var reminderTime = body.getAttribute("data-reminder-time");
  var remindersEnabled = body.getAttribute("data-reminders-enabled") === "true";

  if (reminderTime) window.localStorage.setItem("lunara:reminder-time", reminderTime);
  if (body.hasAttribute("data-reminders-enabled")) {
    window.localStorage.setItem("lunara:reminders", remindersEnabled ? "1" : "0");
  }

  function showReminder() {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    var today = new Date().toISOString().slice(0, 10);
    if (window.localStorage.getItem("lunara:reminder-shown") === today) return;
    window.localStorage.setItem("lunara:reminder-shown", today);

    try {
      new Notification("Lunara · seu momento", {
        body: "Como você está hoje? Um registro de 1 minuto já ajuda seu ciclo.",
        icon: "/static/icons/icon-192.png",
        badge: "/static/icons/icon-192.png",
        tag: "lunara-daily-reminder",
      });
    } catch (error) {
      /* Alguns navegadores só permitem notificações via service worker. */
    }
  }

  function maybeScheduleReminder() {
    if (window.localStorage.getItem("lunara:reminders") !== "1") return;
    if (!("Notification" in window) || Notification.permission !== "granted") return;

    var stored = window.localStorage.getItem("lunara:reminder-time") || "09:00";
    var parts = stored.split(":");
    var now = new Date();
    var target = new Date();
    target.setHours(parseInt(parts[0], 10) || 9, parseInt(parts[1], 10) || 0, 0, 0);

    var delay = target.getTime() - now.getTime();
    if (delay <= 0) {
      showReminder();
      return;
    }
    if (delay < 24 * 60 * 60 * 1000) window.setTimeout(showReminder, delay);
  }

  var reminderForm = document.querySelector('input[name="reminder_time"]');
  if (reminderForm) {
    var timeInput = reminderForm;
    var enabledInput = document.querySelector('input[name="notifications_enabled"]');

    timeInput.addEventListener("change", function () {
      window.localStorage.setItem("lunara:reminder-time", timeInput.value);
    });

    if (enabledInput) {
      enabledInput.addEventListener("change", function () {
        window.localStorage.setItem("lunara:reminders", enabledInput.checked ? "1" : "0");
        if (
          enabledInput.checked &&
          "Notification" in window &&
          Notification.permission === "default"
        ) {
          Notification.requestPermission();
        }
      });
    }
  }

  if (document.visibilityState === "visible") maybeScheduleReminder();
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") maybeScheduleReminder();
  });

  root.classList.add("js-ready");
})();

// 懒人性价比清单 · 前端交互 v3（零依赖）
// v3：滚动渐显（IntersectionObserver）/ 统计数字滚动 / 里程碑动效
(function () {
  var KEY = "htlb_done";
  var TOTAL = window.__TOTAL__ || 0;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(d) { localStorage.setItem(KEY, JSON.stringify(d)); }

  var MILES = [
    [1, "🥇 第一条做掉了，万事开头难——但你已经开了。"],
    [5, "🔥 连做 5 条，这个月你已经跑赢大多数只收藏不动手的人。"],
    [20, "⚡ 20 条！你已经是行动派了。"],
    [50, "🏆 50 条，人生项目经理就是你。"],
    [100, "👑 破百了。剩下的都是精挑细选的硬骨头。"],
    [677, "🌌 全书通关……请收下我们的膝盖，并去 GitHub 给作者点个星。"]
  ];

  // ---------- 滚动渐显 ----------
  function setupReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.06, rootMargin: "0px 0px -30px 0px" });
    els.forEach(function (el) { io.observe(el); });
  }

  // ---------- 统计数字滚动 ----------
  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var t0 = null, dur = 900;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function setupCountUp() {
    var els = document.querySelectorAll("[data-count]");
    if (!els.length) return;
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.textContent = el.getAttribute("data-count"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { countUp(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  // ---------- 打勾状态 ----------
  function refreshUI() {
    var d = load();
    var n = Object.keys(d).length;
    document.querySelectorAll("[data-ck]").forEach(function (btn) {
      var on = !!d[btn.getAttribute("data-ck")];
      btn.classList.toggle("on", on);
      btn.textContent = on ? "已做 ✓" : "打勾";
      var card = btn.closest(".card, .daily");
      if (card) card.classList.toggle("done", on);
    });
    ["doneCount", "doneCount2"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.textContent = n;
    });
    var b = document.getElementById("doneBar");
    if (b && TOTAL) b.style.width = (n / TOTAL * 100).toFixed(1) + "%";
    var m = document.getElementById("milestone");
    if (m) {
      var text = "";
      for (var i = MILES.length - 1; i >= 0; i--) {
        if (n >= MILES[i][0]) { text = MILES[i][1]; break; }
      }
      if (n === 0) text = "勾上第一条，这里会有反应。";
      if (m.textContent !== text) {
        m.textContent = text;
        m.style.animation = "none";
        void m.offsetWidth;
        m.style.animation = "mileIn .4s ease";
      }
    }
  }

  window.toggleDone = function (id, btn) {
    var d = load();
    if (d[id]) { delete d[id]; } else { d[id] = Date.now(); }
    save(d);
    refreshUI();
    if (window.applyFilters) window.applyFilters(true);
  };

  // ---------- 数据 ----------
  var DATA = null;
  function initData(cb) {
    if (DATA) return cb(DATA);
    fetch("/s/search.json").then(function (r) { return r.json(); }).then(function (j) {
      DATA = j;
      cb(DATA);
    }).catch(function () { cb([]); });
  }

  // ---------- 筛选 ----------
  function matchLv(lv, sel) {
    if (!sel) return true;
    if (sel === "A") return lv === "A";
    if (sel === "AB") return lv === "A" || lv === "B";
    return true;
  }

  window.applyFilters = function (keepPreset) {
    initData(function (DATA) {
      var q = (document.getElementById("fQian") || {}).value || "";
      var y = (document.getElementById("fYili") || {}).value || "";
      var s = (document.getElementById("fShouyi") || {}).value || "";
      var l = (document.getElementById("fLv") || {}).value || "";
      var kwEl = document.getElementById("fKw");
      var kw = ((kwEl || {}).value || "").trim().toLowerCase();
      var d = load();
      var box = document.getElementById("filterList");
      var cnt = document.getElementById("filterCount");
      if (!box) return;
      document.querySelectorAll(".preset").forEach(function (p) {
        var on = !!keepPreset && p.getAttribute("data-p") === [q, y, s, l].join("|");
        p.classList.toggle("on", on);
      });
      if (!q && !y && !s && !l && !kw) {
        box.innerHTML = "";
        cnt.innerHTML = "点上面的套餐一键开筛，或自己组合条件";
        return;
      }
      var out = DATA.filter(function (e) {
        if (q && e.tags["钱"] !== q) return false;
        if (y && e.tags["毅力"] !== y) return false;
        if (s && e.tags["收益"] !== s) return false;
        if (!matchLv(e.lv, l)) return false;
        if (kw && (e.t + " " + e.h).toLowerCase().indexOf(kw) < 0) return false;
        return true;
      });
      var w = { "A": 0, "B": 1, "C": 2, "": 3 };
      out.sort(function (a, b) { return (w[a.lv] || 9) - (w[b.lv] || 9); });
      cnt.innerHTML = "筛出 <b>" + out.length + "</b> 条，其中你已做 " +
        out.filter(function (e) { return d[e.id]; }).length + " 条";
      var html = out.slice(0, 80).map(function (e) {
        var chips = "";
        for (var k in e.tags) {
          var v = e.tags[k];
          var cls = (v === "0" || v === "否" || v === "大") ? "g" :
            (v === "少" || v === "些" || v === "中") ? "b" : "m";
          chips += '<span class="chip ' + cls + '">' + k + "=" + v + "</span> ";
        }
        chips += '<span class="chip ' + (e.lv === "A" ? "g" : e.lv === "B" ? "b" : "o") + '">证据 ' + e.lv + "</span>";
        return '<div class="card' + (d[e.id] ? " done" : "") + '" data-eid="' + e.id + '">' +
          '<span class="chk"><button data-ck="' + e.id + '" onclick="toggleDone(\'' + e.id + '\',this)">打勾</button></span>' +
          '<div class="t"><a href="/e/' + e.id + '.html">' + e.t + "</a></div>" +
          '<div class="human">' + e.h + "…</div>" +
          '<div class="chips">' + chips + "</div></div>";
      }).join("");
      if (out.length > 80) html += '<div class="empty">只显示前 80 条，加个条件更精准</div>';
      if (!out.length) html = '<div class="empty">没有同时满足这些条件的条目，放宽一点试试</div>';
      box.innerHTML = html;
      refreshUI();
    });
  };

  // ---------- 每日一条：换一条 ----------
  function chipHtml(e) {
    var chips = "";
    for (var k in e.tags) {
      var v = e.tags[k];
      var cls = (v === "0" || v === "否" || v === "大") ? "g" :
        (v === "少" || v === "些" || v === "中") ? "b" : "m";
      chips += '<span class="chip ' + cls + '">' + k + "=" + v + "</span> ";
    }
    chips += '<span class="chip ' + (e.lv === "A" ? "g" : e.lv === "B" ? "b" : "o") + '">证据 ' + e.lv + "</span>";
    return chips;
  }

  function renderDaily(e) {
    var el = document.getElementById("dailyCard");
    if (!el) return;
    el.style.animation = "none";
    void el.offsetWidth;
    el.style.animation = "mileIn .4s ease";
    el.innerHTML =
      '<div class="dt"><span>每日一条 · 碰到对味的就打勾</span><button class="rr" onclick="reroll()">换一条</button></div>' +
      '<div class="t"><a href="/e/' + e.id + '.html">' + e.t + "</a></div>" +
      '<div class="human">' + e.h + "…</div>" +
      '<div class="chips">' + chipHtml(e) + "</div>" +
      '<span class="chk" style="position:absolute;top:20px;right:22px"><button data-ck="' + e.id + '" onclick="toggleDone(\'' + e.id + '\',this)">打勾</button></span>';
    refreshUI();
  }
  window.reroll = function () {
    initData(function (DATA) {
      if (!DATA.length) return;
      renderDaily(DATA[Math.floor(Math.random() * DATA.length)]);
    });
  };

  // ---------- 预设套餐 ----------
  function bindPresets() {
    document.querySelectorAll(".preset").forEach(function (p) {
      p.addEventListener("click", function () {
        var parts = p.getAttribute("data-p").split("|");
        var map = { 0: "fQian", 1: "fYili", 2: "fShouyi", 3: "fLv" };
        for (var i = 0; i < 4; i++) {
          var el = document.getElementById(map[i]);
          if (el) el.value = parts[i];
        }
        var kw = document.getElementById("fKw");
        if (kw) kw.value = "";
        window.applyFilters(true);
        var box = document.getElementById("filterList");
        if (box) box.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ["fQian", "fYili", "fShouyi", "fLv"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("change", function () { window.applyFilters(true); });
    });
    var kw = document.getElementById("fKw");
    if (kw) kw.addEventListener("input", function () { window.applyFilters(true); });
    bindPresets();
    refreshUI();
    setupReveal();
    setupCountUp();
  });
})();

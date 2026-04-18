(function () {
  const root = window.MealsOnWheels || (window.MealsOnWheels = {});
  const data = root.data;
  const utils = root.utils;

  const state = {
    activeCategory: "all",
    activePitStop: data.pitStops[0],
    currentOrigin: Object.assign({}, data.defaultOrigin),
    cart: {},
    lastFocusedElement: null,
    toastTimer: null,
    map: null
  };

  const dom = {};

  function cacheDom() {
    dom.menuButton = document.getElementById("menuButton");
    dom.siteNav = document.getElementById("siteNav");
    dom.cartButton = document.getElementById("cartButton");
    dom.cartCount = document.getElementById("cartCount");
    dom.heroStats = document.getElementById("heroStats");
    dom.locationForm = document.getElementById("locationForm");
    dom.locationInput = document.getElementById("locationInput");
    dom.gpsButton = document.getElementById("gpsButton");
    dom.quickPicks = document.getElementById("quickPicks");
    dom.originLabel = document.getElementById("originLabel");
    dom.originSummary = document.getElementById("originSummary");
    dom.coverageBadges = document.getElementById("coverageBadges");
    dom.nearestStops = document.getElementById("nearestStops");
    dom.fitMapButton = document.getElementById("fitMapButton");
    dom.selectedStopMapLink = document.getElementById("selectedStopMapLink");
    dom.selectedStopName = document.getElementById("selectedStopName");
    dom.selectedStopSummary = document.getElementById("selectedStopSummary");
    dom.selectedStopTags = document.getElementById("selectedStopTags");
    dom.selectedStopDistance = document.getElementById("selectedStopDistance");
    dom.selectedStopType = document.getElementById("selectedStopType");
    dom.selectedStopArea = document.getElementById("selectedStopArea");
    dom.directionsButton = document.getElementById("directionsButton");
    dom.categoryTabs = document.getElementById("categoryTabs");
    dom.catalogSearch = document.getElementById("catalogSearch");
    dom.dietFilter = document.getElementById("dietFilter");
    dom.sortFilter = document.getElementById("sortFilter");
    dom.catalogGrid = document.getElementById("catalogGrid");
    dom.boxGrid = document.getElementById("boxGrid");
    dom.cartDrawer = document.getElementById("cartDrawer");
    dom.closeCartButton = document.getElementById("closeCartButton");
    dom.drawerStopName = document.getElementById("drawerStopName");
    dom.drawerStopSummary = document.getElementById("drawerStopSummary");
    dom.cartList = document.getElementById("cartList");
    dom.deliveryMode = document.getElementById("deliveryMode");
    dom.checkoutName = document.getElementById("checkoutName");
    dom.checkoutPhone = document.getElementById("checkoutPhone");
    dom.checkoutButton = document.getElementById("checkoutButton");
    dom.checkoutFeedback = document.getElementById("checkoutFeedback");
    dom.subtotalValue = document.getElementById("subtotalValue");
    dom.deliveryValue = document.getElementById("deliveryValue");
    dom.savingsValue = document.getElementById("savingsValue");
    dom.totalValue = document.getElementById("totalValue");
    dom.toast = document.getElementById("toast");
  }

  function showToast(message) {
    clearTimeout(state.toastTimer);
    dom.toast.textContent = message;
    dom.toast.classList.add("show");
    state.toastTimer = window.setTimeout(function () {
      dom.toast.classList.remove("show");
    }, 1800);
  }

  function scrollToSection(sectionId) {
    const target = document.getElementById(sectionId);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function findItem(itemId) {
    return data.allItems.find(function (item) {
      return item.id === itemId;
    });
  }

  function nearestStops(origin) {
    return data.pitStops
      .map(function (stop) {
        return Object.assign({}, stop, {
          distance: utils.haversineMiles(origin, stop)
        });
      })
      .sort(function (left, right) {
        return left.distance - right.distance;
      });
  }

  function categoryCounts() {
    return data.catalogCategories.reduce(function (counts, category) {
      counts[category.id] = 0;
      return counts;
    }, {});
  }

  function renderHeroStats() {
    const stats = [
      { value: String(data.pitStops.length), label: "pit stops" },
      { value: "1 mile", label: "coverage radius" },
      { value: "40%", label: "below retail on support boxes" }
    ];

    dom.heroStats.innerHTML = stats
      .map(function (stat) {
        return (
          '<article class="stat-card">' +
          "<strong>" +
          utils.escapeHtml(stat.value) +
          "</strong>" +
          "<span>" +
          utils.escapeHtml(stat.label) +
          "</span>" +
          "</article>"
        );
      })
      .join("");
  }

  function renderCategoryTabs() {
    const counts = categoryCounts();

    data.products.forEach(function (item) {
      if (counts[item.cat] !== undefined) {
        counts[item.cat] += 1;
      }
      counts.all += 1;
    });

    dom.categoryTabs.innerHTML = data.catalogCategories
      .map(function (category) {
        const isActive = category.id === state.activeCategory;
        return (
          '<button class="category-tab' +
          (isActive ? " active" : "") +
          '" type="button" data-category="' +
          utils.escapeHtml(category.id) +
          '" aria-pressed="' +
          String(isActive) +
          '">' +
          utils.escapeHtml(category.name) +
          " (" +
          String(counts[category.id]) +
          ")" +
          "</button>"
        );
      })
      .join("");
  }

  function filteredCatalogItems() {
    const searchValue = utils.normalizeQuery(dom.catalogSearch.value);
    const dietValue = dom.dietFilter.value;
    const sortValue = dom.sortFilter.value;

    let list = data.products.filter(function (item) {
      return state.activeCategory === "all" || item.cat === state.activeCategory;
    });

    if (dietValue === "veg") {
      list = list.filter(function (item) {
        return item.diet === "veg";
      });
    }

    if (dietValue === "nonveg") {
      list = list.filter(function (item) {
        return item.diet === "nonveg" || item.diet === "mixed";
      });
    }

    if (dietValue === "student") {
      list = list.filter(function (item) {
        return item.student;
      });
    }

    if (searchValue) {
      list = list.filter(function (item) {
        const combinedText = [
          item.name,
          item.tag,
          item.unit,
          item.portion,
          item.contents || "",
          data.categoryMeta[item.cat].name
        ].join(" ");

        return utils.normalizeQuery(combinedText).indexOf(searchValue) !== -1;
      });
    }

    if (sortValue === "priceLow") {
      list.sort(function (left, right) {
        return left.price - right.price;
      });
    }

    if (sortValue === "protein") {
      list.sort(function (left, right) {
        return right.protein - left.protein;
      });
    }

    if (sortValue === "savings") {
      list.sort(function (left, right) {
        return 1 - right.price / right.retail - (1 - left.price / left.retail);
      });
    }

    return list;
  }

  function stockStatus(stock) {
    if (stock <= 0) {
      return { className: "out", label: "Out of stock" };
    }
    if (stock <= 5) {
      return { className: "low", label: "Low stock" };
    }
    return { className: "in", label: "In stock" };
  }

  function itemCardMarkup(item) {
    const meta = data.categoryMeta[item.cat];
    const stock = utils.stockFor(item, state.activePitStop);
    const status = stockStatus(stock);
    const savings = Math.max(0, Math.round((1 - item.price / item.retail) * 100));
    const detail = item.unit + " · " + item.portion;
    const badges = ['<span class="pill-badge">' + utils.escapeHtml(item.tag) + "</span>"];

    if (item.student) {
      badges.push('<span class="pill-badge">Student pick</span>');
    }

    return (
      '<article class="product-card">' +
      '<div class="product-visual">' +
      '<img class="product-image" src="' +
      utils.escapeHtml(meta.image) +
      '" alt="' +
      utils.escapeHtml(item.name) +
      '" loading="lazy" />' +
      "</div>" +
      '<div class="product-top">' +
      '<div class="product-meta">' +
      '<span class="product-type">' +
      utils.escapeHtml(meta.short) +
      "</span>" +
      '<span class="stock-pill ' +
      status.className +
      '">' +
      utils.escapeHtml(status.label) +
      "</span>" +
      "</div>" +
      "</div>" +
      "<div>" +
      "<h3>" +
      utils.escapeHtml(item.name) +
      "</h3>" +
      '<p class="product-description">' +
      utils.escapeHtml(detail) +
      "</p>" +
      "</div>" +
      '<div class="product-badges">' +
      badges.join("") +
      '<span class="pill-badge">' + String(savings) + "% below retail</span>" +
      "</div>" +
      '<dl class="nutrition-grid">' +
      '<div class="nutrition-card"><dt>Protein</dt><dd>' +
      String(item.protein) +
      "g</dd></div>" +
      '<div class="nutrition-card"><dt>Fiber</dt><dd>' +
      String(item.fiber) +
      "g</dd></div>" +
      '<div class="nutrition-card"><dt>Energy</dt><dd>' +
      String(item.kcal) +
      "</dd></div>" +
      "</dl>" +
      '<div class="price-row">' +
      '<div class="price-block"><strong>' +
      utils.formatCurrency(item.price) +
      "</strong><span>Retail " +
      utils.formatCurrency(item.retail) +
      "</span></div>" +
      '<button class="card-button" type="button" data-add-id="' +
      utils.escapeHtml(item.id) +
      '"' +
      (stock <= 0 ? " disabled" : "") +
      ">Add</button>" +
      "</div>" +
      "</article>"
    );
  }

  function renderCatalog() {
    renderCategoryTabs();

    const list = filteredCatalogItems();
    if (!list.length) {
      dom.catalogGrid.innerHTML =
        '<div class="empty-state">No matching items for this combination of search, diet, and category filters.</div>';
      return;
    }

    dom.catalogGrid.innerHTML = list.map(itemCardMarkup).join("");
  }

  function renderBoxes() {
    dom.boxGrid.innerHTML = data.boxes.map(itemCardMarkup).join("");
  }

  function renderOriginSummary() {
    const rankedStops = nearestStops(state.currentOrigin);
    const nearest = rankedStops[0];
    const insideCoverage = nearest.distance <= data.mapRadiusMiles;

    dom.originLabel.textContent = state.currentOrigin.label;
    dom.originSummary.textContent = insideCoverage
      ? "Inside " + nearest.short + "'s 1-mile ring."
      : "Closest hub: " + nearest.short + ".";

    dom.coverageBadges.innerHTML =
      '<span class="badge">Closest hub: ' +
      utils.escapeHtml(nearest.short) +
      "</span>" +
      '<span class="badge">' +
      nearest.distance.toFixed(2) +
      " mi away</span>" +
      '<span class="badge">' +
      (insideCoverage ? "Inside a live service ring" : "Outside the nearest ring") +
      "</span>" +
      '<span class="badge">Active hub: ' +
      utils.escapeHtml(state.activePitStop.short) +
      "</span>";
  }

  function renderNearestStops() {
    dom.nearestStops.innerHTML = nearestStops(state.currentOrigin)
      .slice(0, 5)
      .map(function (stop, index) {
        return (
          '<button class="stop-card' +
          (stop.id === state.activePitStop.id ? " active" : "") +
          '" type="button" data-stop-id="' +
          utils.escapeHtml(stop.id) +
          '">' +
          "<div>" +
          "<strong>" +
          String(index + 1) +
          ". " +
          utils.escapeHtml(stop.name) +
          "</strong>" +
          "<span>" +
          utils.escapeHtml(stop.area) +
          "<br>" +
          utils.escapeHtml(stop.type) +
          "</span>" +
          "</div>" +
          '<span class="distance-pill">' +
          stop.distance.toFixed(2) +
          " mi</span>" +
          "</button>"
        );
      })
      .join("");
  }

  function renderSelectedStop() {
    const stop = state.activePitStop;
    const distance = utils.haversineMiles(state.currentOrigin, stop);

    dom.selectedStopName.textContent = stop.name;
    dom.selectedStopSummary.textContent = stop.note;
    dom.selectedStopDistance.textContent = distance.toFixed(2) + " mi";
    dom.selectedStopType.textContent = stop.type;
    dom.selectedStopArea.textContent = stop.area;
    dom.selectedStopTags.innerHTML = stop.services
      .map(function (service) {
        return '<span class="badge">' + utils.escapeHtml(service) + "</span>";
      })
      .join("");

    dom.selectedStopMapLink.href = utils.buildStopUrl(stop);
    dom.selectedStopMapLink.textContent = "Open " + stop.short + " in Google Maps";
    dom.directionsButton.href = utils.buildDirectionsUrl(state.currentOrigin, stop);
    dom.drawerStopName.textContent = stop.name;
    dom.drawerStopSummary.textContent = stop.note;
  }

  function getTotals() {
    const items = Object.keys(state.cart).map(function (itemId) {
      return state.cart[itemId];
    });
    const subtotal = items.reduce(function (total, item) {
      return total + item.price * item.qty;
    }, 0);
    const retail = items.reduce(function (total, item) {
      return total + item.retail * item.qty;
    }, 0);
    const count = items.reduce(function (total, item) {
      return total + item.qty;
    }, 0);

    let fee = 0;
    if (count > 0) {
      if (dom.deliveryMode.value === "dorm") {
        fee = 1.49;
      } else if (dom.deliveryMode.value === "priority") {
        fee = 4.99;
      }
    }

    return {
      count: count,
      subtotal: subtotal,
      retail: retail,
      savings: Math.max(0, retail - subtotal),
      fee: fee,
      total: subtotal + fee
    };
  }

  function renderCart() {
    const items = Object.keys(state.cart).map(function (itemId) {
      return state.cart[itemId];
    });

    if (!items.length) {
      dom.cartList.innerHTML =
        '<div class="empty-state">Your cart is empty. Pick a hub, add groceries, and this drawer will stay aligned with that hub&apos;s stock.</div>';
    } else {
      dom.cartList.innerHTML = items
        .map(function (item) {
          return (
            '<article class="cart-item">' +
            '<div class="cart-mark">' +
            utils.escapeHtml(item.mark || utils.abbreviateLabel(item.name, "MW")) +
            "</div>" +
            "<div>" +
            "<strong>" +
            utils.escapeHtml(item.name) +
            "</strong>" +
            "<span>" +
            utils.formatCurrency(item.price) +
            " each · " +
            utils.escapeHtml(item.portion) +
            "</span>" +
            "</div>" +
            '<div class="qty-controls">' +
            '<button type="button" aria-label="Decrease quantity" data-qty-id="' +
            utils.escapeHtml(item.id) +
            '" data-delta="-1">-</button>' +
            "<output>" +
            String(item.qty) +
            "</output>" +
            '<button type="button" aria-label="Increase quantity" data-qty-id="' +
            utils.escapeHtml(item.id) +
            '" data-delta="1">+</button>' +
            "</div>" +
            "</article>"
          );
        })
        .join("");
    }

    const totals = getTotals();
    dom.cartCount.textContent = String(totals.count);
    dom.subtotalValue.textContent = utils.formatCurrency(totals.subtotal);
    dom.deliveryValue.textContent = utils.formatCurrency(totals.fee);
    dom.savingsValue.textContent = utils.formatCurrency(totals.savings);
    dom.totalValue.textContent = utils.formatCurrency(totals.total);
  }

  function reconcileCartStock() {
    let adjustedLines = 0;

    Object.keys(state.cart).forEach(function (itemId) {
      const cartItem = state.cart[itemId];
      const maxStock = utils.stockFor(cartItem, state.activePitStop);

      if (maxStock <= 0) {
        delete state.cart[itemId];
        adjustedLines += 1;
        return;
      }

      if (cartItem.qty > maxStock) {
        state.cart[itemId].qty = maxStock;
        adjustedLines += 1;
      }
    });

    return adjustedLines;
  }

  function selectPitStop(stopId, options) {
    const stop = data.pitStops.find(function (candidate) {
      return candidate.id === stopId;
    });

    if (!stop) {
      return;
    }

    state.activePitStop = stop;
    const adjustments = reconcileCartStock();

    renderOriginSummary();
    renderNearestStops();
    renderSelectedStop();
    renderCatalog();
    renderBoxes();
    renderCart();

    if (state.map) {
      state.map.setActiveStop(stop.id, !(options && options.focusMap === false));
    }

    if (dom.checkoutFeedback.hidden === false) {
      dom.checkoutFeedback.hidden = true;
      dom.checkoutFeedback.textContent = "";
    }

    if (adjustments > 0) {
      showToast("Cart adjusted for " + stop.short + " stock.");
      return;
    }

    if (!options || options.announce !== false) {
      showToast(stop.short + " selected.");
    }
  }

  function handleLocationSearch(query, shouldScroll) {
    const origin = utils.geocodeLocal(query);

    if (!origin) {
      showToast("Try a neighborhood, ZIP, campus, or coordinates.");
      return;
    }

    state.currentOrigin = origin;
    dom.locationInput.value = query;

    if (state.map) {
      state.map.setOrigin(state.currentOrigin);
    }

    const nearest = nearestStops(state.currentOrigin)[0];
    selectPitStop(nearest.id, { announce: false, focusMap: true });

    if (shouldScroll !== false) {
      scrollToSection("coverage");
    }

    showToast("Closest hub: " + nearest.short + ".");
  }

  function addToCart(itemId) {
    const item = findItem(itemId);
    if (!item) {
      return;
    }

    const currentQty = state.cart[itemId] ? state.cart[itemId].qty : 0;
    const maxStock = utils.stockFor(item, state.activePitStop);

    if (currentQty >= maxStock) {
      showToast("No more stock at this hub.");
      return;
    }

    if (!state.cart[itemId]) {
      state.cart[itemId] = Object.assign({}, item, { qty: 0 });
    }

    state.cart[itemId].qty += 1;
    renderCart();
    dom.checkoutFeedback.hidden = true;
    dom.checkoutFeedback.textContent = "";
    showToast(item.name + " added.");
  }

  function changeQuantity(itemId, delta) {
    if (!state.cart[itemId]) {
      return;
    }

    const item = findItem(itemId);
    const nextQty = state.cart[itemId].qty + delta;
    const maxStock = utils.stockFor(item, state.activePitStop);

    if (nextQty > maxStock) {
      showToast("Quantity exceeds active hub stock.");
      return;
    }

    if (nextQty <= 0) {
      delete state.cart[itemId];
    } else {
      state.cart[itemId].qty = nextQty;
    }

    renderCart();
    dom.checkoutFeedback.hidden = true;
    dom.checkoutFeedback.textContent = "";
  }

  function drawerIsOpen() {
    return !dom.cartDrawer.hidden;
  }

  function openCart() {
    state.lastFocusedElement = document.activeElement;
    dom.cartDrawer.hidden = false;
    document.body.classList.add("drawer-open");

    window.requestAnimationFrame(function () {
      dom.cartDrawer.classList.add("open");
      dom.closeCartButton.focus();
    });
  }

  function closeCart() {
    dom.cartDrawer.classList.remove("open");
    document.body.classList.remove("drawer-open");

    window.setTimeout(function () {
      dom.cartDrawer.hidden = true;
    }, 220);

    if (state.lastFocusedElement && typeof state.lastFocusedElement.focus === "function") {
      state.lastFocusedElement.focus();
    }
  }

  function focusableElementsInDrawer() {
    return Array.prototype.slice
      .call(
        dom.cartDrawer.querySelectorAll(
          'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      )
      .filter(function (element) {
        return !element.hidden;
      });
  }

  function trapDrawerFocus(event) {
    const focusable = focusableElementsInDrawer();
    if (!focusable.length) {
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
      return;
    }

    if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function handleCheckout() {
    const totals = getTotals();

    if (!totals.count) {
      showToast("Add items before placing a demo order.");
      return;
    }

    const name = dom.checkoutName.value.trim() || "Guest";
    const pickupCode = "MOW-" + String(Math.floor(1000 + Math.random() * 9000));

    dom.checkoutFeedback.hidden = false;
    dom.checkoutFeedback.textContent =
      "Demo order placed for " +
      name +
      ". Pickup code: " +
      pickupCode +
      ". Hub: " +
      state.activePitStop.name +
      ". Total: " +
      utils.formatCurrency(totals.total) +
      ".";

    state.cart = {};
    renderCart();
    showToast("Demo order created.");
  }

  function initializeMap() {
    const mapElement = document.getElementById("coverageMap");

    if (!mapElement) {
      return;
    }

    if (typeof root.createCoverageMap !== "function" || typeof window.L === "undefined") {
      mapElement.classList.add("map-fallback");
      mapElement.innerHTML =
        '<div class="map-fallback-message">' +
        "<strong>Map unavailable</strong>" +
        "<p>The catalog still works below.</p>" +
        "</div>";
      return;
    }

    try {
      state.map = root.createCoverageMap({
        elementId: "coverageMap",
        radiusMeters: data.mapRadiusMeters,
        onSelectStop: function (stopId) {
          selectPitStop(stopId, { announce: true, focusMap: true });
        }
      });

      state.map.setStops(data.pitStops, state.activePitStop.id);
      state.map.setOrigin(state.currentOrigin);
    } catch (error) {
      console.error("Coverage map initialization failed.", error);
      state.map = null;
      mapElement.classList.add("map-fallback");
      mapElement.innerHTML =
        '<div class="map-fallback-message">' +
        "<strong>Map unavailable</strong>" +
        "<p>The catalog still works below.</p>" +
        "</div>";
    }
  }

  function bindEvents() {
    document.querySelectorAll("[data-scroll-target]").forEach(function (button) {
      button.addEventListener("click", function () {
        scrollToSection(button.getAttribute("data-scroll-target"));
      });
    });

    dom.menuButton.addEventListener("click", function () {
      const nextState = !dom.siteNav.classList.contains("is-open");
      dom.siteNav.classList.toggle("is-open", nextState);
      dom.menuButton.setAttribute("aria-expanded", String(nextState));
    });

    dom.siteNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        dom.siteNav.classList.remove("is-open");
        dom.menuButton.setAttribute("aria-expanded", "false");
      });
    });

    dom.locationForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLocationSearch(dom.locationInput.value, false);
    });

    dom.quickPicks.addEventListener("click", function (event) {
      const button = event.target.closest("[data-query]");
      if (!button) {
        return;
      }

      handleLocationSearch(button.getAttribute("data-query"), false);
    });

    dom.gpsButton.addEventListener("click", function () {
      if (!navigator.geolocation) {
        showToast("GPS is not available in this browser.");
        return;
      }

      navigator.geolocation.getCurrentPosition(
        function (position) {
          state.currentOrigin = {
            label: "Your current location",
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            query: position.coords.latitude + "," + position.coords.longitude
          };

          dom.locationInput.value = "Current location";

          if (state.map) {
            state.map.setOrigin(state.currentOrigin);
          }

          const nearest = nearestStops(state.currentOrigin)[0];
          selectPitStop(nearest.id, { announce: false, focusMap: true });
          showToast("Closest hub: " + nearest.short + ".");
        },
        function () {
          showToast("Location access was denied.");
        }
      );
    });

    dom.fitMapButton.addEventListener("click", function () {
      if (state.map) {
        state.map.fitToNetwork();
      }
    });

    dom.categoryTabs.addEventListener("click", function (event) {
      const button = event.target.closest("[data-category]");
      if (!button) {
        return;
      }

      state.activeCategory = button.getAttribute("data-category");
      renderCatalog();
    });

    dom.catalogSearch.addEventListener("input", renderCatalog);
    dom.dietFilter.addEventListener("change", renderCatalog);
    dom.sortFilter.addEventListener("change", renderCatalog);

    dom.catalogGrid.addEventListener("click", function (event) {
      const button = event.target.closest("[data-add-id]");
      if (!button) {
        return;
      }
      addToCart(button.getAttribute("data-add-id"));
    });

    dom.boxGrid.addEventListener("click", function (event) {
      const button = event.target.closest("[data-add-id]");
      if (!button) {
        return;
      }
      addToCart(button.getAttribute("data-add-id"));
    });

    dom.nearestStops.addEventListener("click", function (event) {
      const button = event.target.closest("[data-stop-id]");
      if (!button) {
        return;
      }
      selectPitStop(button.getAttribute("data-stop-id"), { announce: true, focusMap: true });
    });

    dom.cartButton.addEventListener("click", openCart);
    dom.closeCartButton.addEventListener("click", closeCart);

    dom.cartDrawer.addEventListener("click", function (event) {
      if (event.target.hasAttribute("data-close-cart")) {
        closeCart();
      }
    });

    dom.cartList.addEventListener("click", function (event) {
      const button = event.target.closest("[data-qty-id]");
      if (!button) {
        return;
      }

      changeQuantity(button.getAttribute("data-qty-id"), Number(button.getAttribute("data-delta")));
    });

    dom.deliveryMode.addEventListener("change", renderCart);
    dom.checkoutButton.addEventListener("click", handleCheckout);

    document.addEventListener("keydown", function (event) {
      if (!drawerIsOpen()) {
        return;
      }

      if (event.key === "Escape") {
        closeCart();
        return;
      }

      if (event.key === "Tab") {
        trapDrawerFocus(event);
      }
    });
  }

  function initialize() {
    cacheDom();
    renderHeroStats();
    initializeMap();
    selectPitStop(nearestStops(state.currentOrigin)[0].id, { announce: false, focusMap: false });
    renderCart();
    bindEvents();
  }

  document.addEventListener("DOMContentLoaded", initialize);
})();

(function () {
  "use strict";

  var PAGE_SIZE = 60;

  var CATEGORY_DEFINITIONS = [
    { key: "characters-fashion", label: "Characters & Fashion" },
    { key: "scenes-architecture", label: "Scenes & Architecture" },
    { key: "product-commercial", label: "Product & Commercial" },
    { key: "food-lifestyle", label: "Food & Lifestyle" },
    { key: "infographics-text", label: "Infographics & Text" },
    { key: "photo-editing-effects", label: "Photo Editing & Effects" },
    { key: "craft-3d-styles", label: "Craft & 3D Styles" },
    { key: "other-concepts", label: "Other Concepts" }
  ];

  var CATEGORY_BY_KEY = CATEGORY_DEFINITIONS.reduce(function (acc, category) {
    acc[category.key] = category;
    return acc;
  }, {});

  var state = {
    query: "",
    category: "all",
    tag: "all",
    randomSort: true,
    randomSeed: Math.random(),
    page: 1,
    lastFocusedElement: null,
    activePrompt: "main",
    activeModalItem: null
  };

  var nodes = {
    totalCount: document.getElementById("total-count"),
    searchInput: document.getElementById("search-input"),
    randomSortToggle: document.getElementById("random-sort-toggle"),
    categoryFilters: document.getElementById("category-filters"),
    tagFilters: document.getElementById("tag-filters"),
    gallerySummary: document.getElementById("gallery-summary"),
    pageStatus: document.getElementById("page-status"),
    galleryGrid: document.getElementById("gallery-grid"),
    emptyState: document.getElementById("empty-state"),
    prevPage: document.getElementById("prev-page"),
    nextPage: document.getElementById("next-page"),
    pageButtons: document.getElementById("page-buttons"),
    modal: document.getElementById("detail-modal"),
    modalImage: document.getElementById("modal-image"),
    modalTitle: document.getElementById("modal-title"),
    modalCategory: document.getElementById("modal-category"),
    modalModel: document.getElementById("modal-model"),
    modalRuntime: document.getElementById("modal-runtime"),
    modalTags: document.getElementById("modal-tags"),
    modalCopyPrompt: document.getElementById("modal-copy-prompt"),
    modalPromptTabs: document.getElementById("modal-prompt-tabs"),
    modalPromptPanel: document.getElementById("modal-prompt-panel"),
    modalPrompt: document.getElementById("modal-prompt")
  };

  var rawData = Array.isArray(window.__GALLERY_DATA__) ? window.__GALLERY_DATA__ : [];
  var classificationData = window.__PROMPT_CLASSIFICATION__ || {};
  var classifiedItems = rawData.map(normalizeItem);
  var tagDefinitions = buildTagDefinitions(classifiedItems);

  initialize();

  function initialize() {
    nodes.totalCount.textContent = classifiedItems.length.toLocaleString();
    renderFilters();
    renderGallery();
    bindEvents();
  }

  function bindEvents() {
    nodes.searchInput.addEventListener("input", function (event) {
      state.query = event.target.value.trim().toLowerCase();
      state.page = 1;
      renderGallery();
    });

    nodes.randomSortToggle.addEventListener("change", function (event) {
      state.randomSort = event.target.checked;
      if (state.randomSort) {
        state.randomSeed = Math.random();
      }
      state.page = 1;
      renderGallery();
      scrollToGalleryTop();
    });

    nodes.prevPage.addEventListener("click", function () {
      if (state.page > 1) {
        state.page -= 1;
        renderGallery();
        scrollToGalleryTop();
      }
    });

    nodes.nextPage.addEventListener("click", function () {
      var totalPages = getTotalPages(getFilteredItems().length);
      if (state.page < totalPages) {
        state.page += 1;
        renderGallery();
        scrollToGalleryTop();
      }
    });

    nodes.modal.addEventListener("click", function (event) {
      if (event.target.hasAttribute("data-close-modal")) {
        closeModal();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !nodes.modal.hidden) {
        closeModal();
      }
    });

    nodes.modalCopyPrompt.addEventListener("click", function () {
      if (state.activeModalItem) {
        copyPrompt(getActivePromptText(state.activeModalItem), nodes.modalCopyPrompt);
      }
    });
  }

  function normalizeItem(item, index) {
    var image = item.image || "";
    var indexFromImage = getImageIndex(image);
    var prompt = item.prompt || "";
    var title = item.title || "Image " + (indexFromImage || index + 1);
    var stored = getStoredClassification(item, image, indexFromImage);
    var categoryKey = stored.categoryKey || slugifyCategory(stored.category || item.category || "");
    var category = CATEGORY_BY_KEY[categoryKey] || CATEGORY_BY_KEY["other-concepts"];
    var tags = normalizeTags(stored.tags || item.tags || [category.label]);
    var tagKeys = tags.map(slugify);

    return {
      id: image || String(index),
      sortOrder: index,
      image: image,
      fallbackImage: item.fallbackImage || "",
      index: indexFromImage || index + 1,
      title: title,
      prompt: prompt,
      model: item.model || "Unknown",
      elapsedSeconds: item.elapsed_seconds,
      categoryKey: category.key,
      categoryLabel: category.label,
      tags: tags,
      tagKeys: tagKeys,
      searchText: [
        title,
        image,
        item.fallbackImage || "",
        prompt,
        item.model || "",
        category.label,
        tags.join(" ")
      ]
        .join(" ")
        .toLowerCase()
    };
  }

  function getStoredClassification(item, image, imageIndex) {
    var items = classificationData.items || {};
    var candidates = [
      item.id,
      item.image,
      image,
      imageIndex !== null && imageIndex !== undefined ? String(imageIndex) : ""
    ].filter(Boolean);

    for (var i = 0; i < candidates.length; i += 1) {
      if (items[candidates[i]]) {
        return items[candidates[i]];
      }
    }

    return {};
  }

  function getImageIndex(image) {
    var match = String(image).match(/(\d+)(?=\.[a-z0-9]+$)/i);
    return match ? Number(match[1]) : null;
  }

  function normalizeTags(tags) {
    var seen = {};
    return tags
      .filter(Boolean)
      .map(function (tag) {
        return String(tag).trim();
      })
      .filter(function (tag) {
        var key = slugify(tag);
        if (!key || seen[key]) {
          return false;
        }
        seen[key] = true;
        return true;
      })
      .slice(0, 6);
  }

  function slugifyCategory(value) {
    var normalized = slugify(value);
    var directMatch = CATEGORY_DEFINITIONS.find(function (category) {
      return category.key === normalized || slugify(category.label) === normalized;
    });
    return directMatch ? directMatch.key : "other-concepts";
  }

  function slugify(value) {
    return String(value)
      .toLowerCase()
      .replace(/&/g, "and")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function buildTagDefinitions(items) {
    var counts = {};
    items.forEach(function (item) {
      item.tags.forEach(function (tag, index) {
        var key = item.tagKeys[index];
        if (!counts[key]) {
          counts[key] = { key: key, label: tag, count: 0 };
        }
        counts[key].count += 1;
      });
    });

    return Object.keys(counts)
      .map(function (key) {
        return counts[key];
      })
      .sort(function (a, b) {
        return b.count - a.count || a.label.localeCompare(b.label);
      });
  }

  function renderFilters() {
    renderCategoryFilters();
    renderTagFilters();
  }

  function renderCategoryFilters() {
    var counts = classifiedItems.reduce(function (acc, item) {
      acc[item.categoryKey] = (acc[item.categoryKey] || 0) + 1;
      return acc;
    }, {});

    nodes.categoryFilters.replaceChildren();
    nodes.categoryFilters.appendChild(
      createFilterButton("category", "all", "All", classifiedItems.length)
    );

    CATEGORY_DEFINITIONS.forEach(function (category) {
      nodes.categoryFilters.appendChild(
        createFilterButton("category", category.key, category.label, counts[category.key] || 0)
      );
    });
  }

  function renderTagFilters() {
    nodes.tagFilters.replaceChildren();
    nodes.tagFilters.appendChild(createFilterButton("tag", "all", "All tags", classifiedItems.length));

    tagDefinitions.forEach(function (tag) {
      nodes.tagFilters.appendChild(createFilterButton("tag", tag.key, tag.label, tag.count));
    });
  }

  function createFilterButton(type, key, label, count) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.setAttribute("role", "listitem");
    button.setAttribute("aria-pressed", String(state[type] === key));
    button.dataset[type] = key;

    if (state[type] === key) {
      button.classList.add("is-active");
    }

    button.append(document.createTextNode(label + " "));

    var countNode = document.createElement("span");
    countNode.textContent = count;
    button.appendChild(countNode);

    button.addEventListener("click", function () {
      state[type] = key;
      state.page = 1;
      renderFilters();
      renderGallery();
    });

    return button;
  }

  function renderGallery() {
    var filteredItems = getFilteredItems();
    var totalPages = getTotalPages(filteredItems.length);
    state.page = Math.min(state.page, totalPages);

    var startIndex = (state.page - 1) * PAGE_SIZE;
    var pageItems = filteredItems.slice(startIndex, startIndex + PAGE_SIZE);
    var endIndex = startIndex + pageItems.length;

    nodes.galleryGrid.replaceChildren();
    pageItems.forEach(function (item) {
      nodes.galleryGrid.appendChild(createImageCard(item));
    });

    nodes.emptyState.hidden = filteredItems.length !== 0;
    nodes.gallerySummary.textContent = getGallerySummary(filteredItems.length, startIndex, endIndex);
    nodes.pageStatus.textContent = "Page " + state.page + " of " + totalPages;

    renderPagination(totalPages);
  }

  function getFilteredItems() {
    return classifiedItems.filter(function (item) {
      var matchesCategory = state.category === "all" || item.categoryKey === state.category;
      var matchesTag = state.tag === "all" || item.tagKeys.indexOf(state.tag) !== -1;
      var matchesSearch = !state.query || item.searchText.indexOf(state.query) !== -1;
      return matchesCategory && matchesTag && matchesSearch;
    }).sort(compareItems);
  }

  function compareItems(a, b) {
    if (!state.randomSort) {
      return a.sortOrder - b.sortOrder;
    }

    return seededSortValue(a.id) - seededSortValue(b.id);
  }

  function seededSortValue(value) {
    var text = String(value) + ":" + state.randomSeed;
    var hash = 2166136261;
    for (var index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function getTotalPages(totalItems) {
    return Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  }

  function getGallerySummary(total, startIndex, endIndex) {
    if (!total) {
      return "No prompts to show.";
    }

    return (
      "Showing " +
      (startIndex + 1).toLocaleString() +
      "-" +
      endIndex.toLocaleString() +
      " of " +
      total.toLocaleString() +
      " matching prompts, " +
      PAGE_SIZE +
      " max per page."
    );
  }

  function createImageCard(item) {
    var article = document.createElement("article");
    article.className = "image-card";

    var copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "copy-prompt-button";
    copyButton.textContent = "⧉";
    copyButton.title = "Copy prompt";
    copyButton.setAttribute("aria-label", "Copy prompt for " + item.title);
    copyButton.addEventListener("click", function () {
      copyPrompt(getCopyPrompt(item), copyButton);
    });

    var button = document.createElement("button");
    button.type = "button";
    button.className = "card-button";
    button.setAttribute("aria-label", "Open details for " + item.title);
    button.addEventListener("click", function () {
      openModal(item, button);
    });

    var thumbWrap = document.createElement("div");
    thumbWrap.className = "thumb-wrap";

    var image = document.createElement("img");
    image.alt = item.title;
    image.loading = "lazy";
    setImageSource(image, item.image, item.fallbackImage, function () {
      thumbWrap.classList.add("is-broken");
    });

    var overlay = document.createElement("div");
    overlay.className = "prompt-overlay";

    var overlayTitle = document.createElement("strong");
    overlayTitle.textContent = "Prompt";
    var overlayPrompt = document.createElement("p");
    overlayPrompt.textContent = item.prompt || "No prompt available.";
    overlay.append(overlayTitle, overlayPrompt);

    thumbWrap.append(image, overlay);

    var cardBody = document.createElement("div");
    cardBody.className = "card-body";

    var title = document.createElement("h3");
    title.textContent = item.title;

    var meta = document.createElement("div");
    meta.className = "card-meta";

    var category = document.createElement("span");
    category.className = "category-badge";
    category.textContent = item.categoryLabel;

    var index = document.createElement("span");
    index.textContent = "#" + item.index;

    var tags = document.createElement("div");
    tags.className = "card-tags";
    item.tags.slice(0, 3).forEach(function (tag) {
      tags.appendChild(createTagBadge(tag));
    });

    meta.append(category, index);
    cardBody.append(title, meta, tags);
    button.append(thumbWrap, cardBody);
    article.append(copyButton, button);

    return article;
  }

  function createTagBadge(label) {
    var tag = document.createElement("span");
    tag.className = "tag-badge";
    tag.textContent = label;
    return tag;
  }

  function renderPagination(totalPages) {
    nodes.prevPage.disabled = state.page <= 1;
    nodes.nextPage.disabled = state.page >= totalPages;
    nodes.pageButtons.replaceChildren();

    getVisiblePages(totalPages, state.page).forEach(function (page) {
      if (page === "...") {
        var spacer = document.createElement("span");
        spacer.className = "page-ellipsis";
        spacer.textContent = "...";
        nodes.pageButtons.appendChild(spacer);
        return;
      }

      var button = document.createElement("button");
      button.type = "button";
      button.className = "page-button";
      button.textContent = page;
      button.setAttribute("aria-label", "Go to page " + page);

      if (page === state.page) {
        button.classList.add("is-active");
        button.setAttribute("aria-current", "page");
      }

      button.addEventListener("click", function () {
        state.page = page;
        renderGallery();
        scrollToGalleryTop();
      });

      nodes.pageButtons.appendChild(button);
    });
  }

  function getVisiblePages(totalPages, currentPage) {
    if (totalPages <= 7) {
      return range(1, totalPages);
    }

    var pages = [1];
    var start = Math.max(2, currentPage - 1);
    var end = Math.min(totalPages - 1, currentPage + 1);

    if (start > 2) {
      pages.push("...");
    }

    range(start, end).forEach(function (page) {
      pages.push(page);
    });

    if (end < totalPages - 1) {
      pages.push("...");
    }

    pages.push(totalPages);
    return pages;
  }

  function range(start, end) {
    var values = [];
    for (var page = start; page <= end; page += 1) {
      values.push(page);
    }
    return values;
  }

  function openModal(item, trigger) {
    state.lastFocusedElement = trigger;
    state.activeModalItem = item;
    state.activePrompt = "main";

    nodes.modalImage.alt = item.title;
    setImageSource(nodes.modalImage, item.image, item.fallbackImage);
    nodes.modalTitle.textContent = item.title;
    nodes.modalCategory.textContent = item.categoryLabel;
    nodes.modalModel.textContent = item.model;
    nodes.modalRuntime.textContent =
      item.elapsedSeconds === undefined ? "Not recorded" : Number(item.elapsedSeconds).toFixed(3) + "s";
    nodes.modalTags.replaceChildren();
    item.tags.forEach(function (tag) {
      nodes.modalTags.appendChild(createTagBadge(tag));
    });
    renderPromptTabs(item);

    nodes.modal.hidden = false;
    document.body.style.overflow = "hidden";
    var closeButton = nodes.modal.querySelector(".modal-close");
    if (closeButton) {
      closeButton.focus();
    }
  }

  function closeModal() {
    nodes.modal.hidden = true;
    nodes.modalImage.onerror = null;
    nodes.modalImage.removeAttribute("src");
    state.activeModalItem = null;
    document.body.style.overflow = "";

    if (state.lastFocusedElement) {
      state.lastFocusedElement.focus();
      state.lastFocusedElement = null;
    }
  }

  function scrollToGalleryTop() {
    document.getElementById("gallery-heading").scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  }

  function setImageSource(image, primaryUrl, fallbackUrl, onBroken) {
    image.dataset.fallbackAttempted = "false";
    image.onerror = function () {
      var canFallback =
        image.dataset.fallbackAttempted !== "true" &&
        fallbackUrl &&
        fallbackUrl !== image.currentSrc &&
        fallbackUrl !== image.src;

      if (canFallback) {
        image.dataset.fallbackAttempted = "true";
        image.src = fallbackUrl;
        return;
      }

      if (onBroken) {
        onBroken();
      }
    };
    image.src = primaryUrl || fallbackUrl || "";
  }

  function getPromptVersions(item) {
    return [
      {
        key: "main",
        label: "Prompt",
        text: item.prompt || ""
      }
    ].filter(function (version) {
      return version.text;
    });
  }

  function renderPromptTabs(item) {
    var versions = getPromptVersions(item);
    nodes.modalPromptTabs.replaceChildren();

    versions.forEach(function (version) {
      var tab = document.createElement("button");
      tab.type = "button";
      tab.className = "prompt-tab";
      tab.textContent = version.label;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-selected", String(version.key === state.activePrompt));
      if (version.key === state.activePrompt) {
        tab.classList.add("is-active");
      }
      tab.addEventListener("click", function () {
        state.activePrompt = version.key;
        renderPromptTabs(item);
      });
      nodes.modalPromptTabs.appendChild(tab);
    });

    setActivePrompt(item);
  }

  function setActivePrompt(item) {
    var versions = getPromptVersions(item);
    var activeVersion =
      versions.find(function (version) {
        return version.key === state.activePrompt;
      }) || versions[0];

    nodes.modalPrompt.textContent = activeVersion
      ? activeVersion.text
      : "No prompt available.";
    nodes.modalPromptPanel.scrollTop = 0;
    nodes.modalCopyPrompt.textContent = "Copy";
  }

  function getCopyPrompt(item) {
    return item.prompt || "";
  }

  function getActivePromptText(item) {
    var versions = getPromptVersions(item);
    var activeVersion = versions.find(function (version) {
      return version.key === state.activePrompt;
    });
    return (activeVersion && activeVersion.text) || getCopyPrompt(item);
  }

  function copyPrompt(text, button) {
    if (!text) {
      return;
    }

    copyText(text).then(function () {
      var originalText = button.textContent;
      button.textContent = "✓";
      window.setTimeout(function () {
        button.textContent = originalText;
      }, 1200);
    });
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () {
        return fallbackCopyText(text);
      });
    }

    return fallbackCopyText(text);
  }

  function fallbackCopyText(text) {
    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    return Promise.resolve();
  }
})();

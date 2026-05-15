(function () {
  "use strict";

  var PAGE_SIZE = 60;

  var CATEGORY_DEFINITIONS = [
    {
      key: "characters-fashion",
      label: "Characters & Fashion",
      keywords: [
        "character",
        "portrait",
        "person",
        "people",
        "face",
        "girl",
        "boy",
        "woman",
        "man",
        "fashion",
        "outfit",
        "ootd",
        "wearing",
        "clothing",
        "makeup",
        "chibi",
        "profession"
      ]
    },
    {
      key: "scenes-architecture",
      label: "Scenes & Architecture",
      keywords: [
        "street",
        "city",
        "urban",
        "landscape",
        "building",
        "architecture",
        "interior",
        "room",
        "garden",
        "forest",
        "beach",
        "mountain",
        "isometric",
        "diorama",
        "scene"
      ]
    },
    {
      key: "product-commercial",
      label: "Product & Commercial",
      keywords: [
        "product",
        "packaging",
        "brand",
        "advertisement",
        "ad ",
        "mockup",
        "logo",
        "label",
        "bottle",
        "cosmetic",
        "shoe",
        "bag",
        "jewelry",
        "watch",
        "commercial"
      ]
    },
    {
      key: "food-lifestyle",
      label: "Food & Lifestyle",
      keywords: [
        "food",
        "recipe",
        "ingredient",
        "pasta",
        "cake",
        "dessert",
        "drink",
        "coffee",
        "restaurant",
        "kitchen",
        "meal",
        "breakfast",
        "cream"
      ]
    },
    {
      key: "infographics-text",
      label: "Infographics & Text",
      keywords: [
        "infographic",
        "diagram",
        "chart",
        "steps",
        "step-by-step",
        "labeled",
        "text",
        "typography",
        "poster",
        "layout",
        "menu",
        "brochure",
        "instruction",
        "icon"
      ]
    },
    {
      key: "photo-editing-effects",
      label: "Photo Editing & Effects",
      keywords: [
        "photo",
        "photograph",
        "camera",
        "overlay",
        "effect",
        "glass",
        "rain",
        "remove",
        "replace",
        "composited",
        "cinematic",
        "lighting",
        "bokeh",
        "retouch"
      ]
    },
    {
      key: "craft-3d-styles",
      label: "Craft & 3D Styles",
      keywords: [
        "3d",
        "c4d",
        "render",
        "felt",
        "wool",
        "clay",
        "miniature",
        "handcrafted",
        "toy",
        "paper",
        "origami",
        "crochet",
        "stop-motion",
        "plush"
      ]
    },
    {
      key: "other-concepts",
      label: "Other Concepts",
      keywords: []
    }
  ];

  var CATEGORY_BY_KEY = CATEGORY_DEFINITIONS.reduce(function (acc, category) {
    acc[category.key] = category;
    return acc;
  }, {});

  var state = {
    query: "",
    category: "all",
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
    modalAuthor: document.getElementById("modal-author"),
    modalSource: document.getElementById("modal-source"),
    modalCopyPrompt: document.getElementById("modal-copy-prompt"),
    modalPromptTabs: document.getElementById("modal-prompt-tabs"),
    modalPromptPanel: document.getElementById("modal-prompt-panel"),
    modalPrompt: document.getElementById("modal-prompt")
  };

  var rawData = Array.isArray(window.__GALLERY_DATA__) ? window.__GALLERY_DATA__ : [];
  var classificationData = window.__PROMPT_CLASSIFICATION__ || {};
  var classifiedItems = rawData.map(normalizeItem);

  initialize();

  function initialize() {
    nodes.totalCount.textContent = classifiedItems.length.toLocaleString();
    renderCategoryFilters();
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
    var prompt = item.prompt_en || item.prompt || "";
    var revisedPrompt = item.revised_prompt_en || item.revised_prompt || "";
    var title = item.title_en || item.title || item.filename || "Untitled image";
    var categoryKey = resolveCategoryKey(item, prompt, revisedPrompt, title);
    var category = CATEGORY_BY_KEY[categoryKey] || CATEGORY_BY_KEY["other-concepts"];

    return {
      id: item.filename || String(item.index || index),
      sortOrder: index,
      filename: item.filename || "",
      index: item.index,
      title: title,
      author: item.author || "Unknown",
      source: item.source || item.author_link || "",
      image: item.image,
      prompt: prompt,
      revisedPrompt: revisedPrompt,
      promptZh: item.prompt_zh || "",
      revisedPromptZh: item.revised_prompt || "",
      categoryKey: category.key,
      categoryLabel: category.label,
      searchText: [
        title,
        item.title || "",
        prompt,
        revisedPrompt,
        item.author || "",
        category.label
      ]
        .join(" ")
        .toLowerCase()
    };
  }

  function resolveCategoryKey(item, prompt, revisedPrompt, title) {
    var storedCategory = getStoredCategory(item);
    if (storedCategory) {
      return slugifyCategory(storedCategory);
    }

    return classifyWithKeywords([prompt, revisedPrompt, title].join(" "));
  }

  function getStoredCategory(item) {
    var items = classificationData.items || {};
    var byFilename = item.filename && items[item.filename];
    var byIndex = item.index !== undefined && items[String(item.index)];
    var match = byFilename || byIndex;
    return match && (match.category || match.label || match);
  }

  function slugifyCategory(value) {
    var normalized = String(value)
      .toLowerCase()
      .replace(/&/g, "and")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

    var directMatch = CATEGORY_DEFINITIONS.find(function (category) {
      return category.key === normalized || slugifyCategoryLabel(category.label) === normalized;
    });

    return directMatch ? directMatch.key : "other-concepts";
  }

  function slugifyCategoryLabel(label) {
    return String(label)
      .toLowerCase()
      .replace(/&/g, "and")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function classifyWithKeywords(text) {
    var normalizedText = " " + text.toLowerCase() + " ";
    var best = {
      key: "other-concepts",
      score: 0
    };

    CATEGORY_DEFINITIONS.forEach(function (category) {
      if (!category.key || category.key === "other-concepts") {
        return;
      }

      var score = category.keywords.reduce(function (sum, keyword) {
        return normalizedText.indexOf(keyword) === -1 ? sum : sum + keywordWeight(keyword);
      }, 0);

      if (score > best.score) {
        best = {
          key: category.key,
          score: score
        };
      }
    });

    return best.key;
  }

  function keywordWeight(keyword) {
    return keyword.length > 8 ? 3 : 2;
  }

  function renderCategoryFilters() {
    var counts = classifiedItems.reduce(function (acc, item) {
      acc[item.categoryKey] = (acc[item.categoryKey] || 0) + 1;
      return acc;
    }, {});

    nodes.categoryFilters.replaceChildren();
    nodes.categoryFilters.appendChild(createCategoryButton("all", "All", classifiedItems.length));

    CATEGORY_DEFINITIONS.forEach(function (category) {
      nodes.categoryFilters.appendChild(
        createCategoryButton(category.key, category.label, counts[category.key] || 0)
      );
    });
  }

  function createCategoryButton(key, label, count) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.setAttribute("role", "listitem");
    button.setAttribute("aria-pressed", String(state.category === key));
    button.dataset.category = key;

    if (state.category === key) {
      button.classList.add("is-active");
    }

    button.append(document.createTextNode(label + " "));

    var countNode = document.createElement("span");
    countNode.textContent = count;
    button.appendChild(countNode);

    button.addEventListener("click", function () {
      state.category = key;
      state.page = 1;
      renderCategoryFilters();
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
      var matchesSearch = !state.query || item.searchText.indexOf(state.query) !== -1;
      return matchesCategory && matchesSearch;
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
      return "No images to show.";
    }

    return (
      "Showing " +
      (startIndex + 1).toLocaleString() +
      "-" +
      endIndex.toLocaleString() +
      " of " +
      total.toLocaleString() +
      " matching images, " +
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
    image.src = item.image;
    image.alt = item.title;
    image.loading = "lazy";
    image.addEventListener("error", function () {
      thumbWrap.classList.add("is-broken");
    });

    var overlay = document.createElement("div");
    overlay.className = "prompt-overlay";

    var overlayTitle = document.createElement("strong");
    overlayTitle.textContent = "Prompt";
    var overlayPrompt = document.createElement("p");
    overlayPrompt.textContent = getCopyPrompt(item) || "No prompt available.";
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
    index.textContent = item.index ? "#" + item.index : item.filename;

    meta.append(category, index);
    cardBody.append(title, meta);
    button.append(thumbWrap, cardBody);
    article.append(copyButton, button);

    return article;
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

    nodes.modalImage.src = item.image;
    nodes.modalImage.alt = item.title;
    nodes.modalTitle.textContent = item.title;
    nodes.modalCategory.textContent = item.categoryLabel;
    nodes.modalAuthor.textContent = item.author;
    renderPromptTabs(item);

    nodes.modalSource.replaceChildren();
    if (item.source) {
      var link = document.createElement("a");
      link.href = item.source;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = "Open source";
      nodes.modalSource.appendChild(link);
    } else {
      nodes.modalSource.textContent = "Not provided";
    }

    nodes.modal.hidden = false;
    document.body.style.overflow = "hidden";
    var closeButton = nodes.modal.querySelector(".modal-close");
    if (closeButton) {
      closeButton.focus();
    }
  }

  function closeModal() {
    nodes.modal.hidden = true;
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

  function getPromptVersions(item) {
    return [
      {
        key: "main",
        label: "Main prompt",
        text: item.revisedPrompt || item.prompt || "",
        copy: true
      },
      {
        key: "original",
        label: "Original",
        text: item.prompt || ""
      },
      {
        key: "revised-zh",
        label: "Revised Chinese",
        text: item.revisedPromptZh || ""
      },
      {
        key: "original-zh",
        label: "Original Chinese",
        text: item.promptZh || ""
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
    return item.revisedPrompt || item.prompt || "";
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

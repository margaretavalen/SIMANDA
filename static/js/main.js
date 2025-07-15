(function () {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector("body");
    const selectHeader = document.querySelector("#header");
    if (
      !selectHeader.classList.contains("scroll-up-sticky") &&
      !selectHeader.classList.contains("sticky-top") &&
      !selectHeader.classList.contains("fixed-top")
    )
      return;
    window.scrollY > 100
      ? selectBody.classList.add("scrolled")
      : selectBody.classList.remove("scrolled");
  }

  document.addEventListener("scroll", toggleScrolled);
  window.addEventListener("load", toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector(".mobile-nav-toggle");

  function mobileNavToogle() {
    document.querySelector("body").classList.toggle("mobile-nav-active");
    mobileNavToggleBtn.classList.toggle("bi-list");
    mobileNavToggleBtn.classList.toggle("bi-x");
  }
  mobileNavToggleBtn.addEventListener("click", mobileNavToogle);

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll("#navmenu a").forEach((navmenu) => {
    navmenu.addEventListener("click", () => {
      if (document.querySelector(".mobile-nav-active")) {
        mobileNavToogle();
      }
    });
  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll(".navmenu .toggle-dropdown").forEach((navmenu) => {
    navmenu.addEventListener("click", function (e) {
      e.preventDefault();
      this.parentNode.classList.toggle("active");
      this.parentNode.nextElementSibling.classList.toggle("dropdown-active");
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector("#preloader");
  if (preloader) {
    window.addEventListener("load", () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector(".scroll-top");

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100
        ? scrollTop.classList.add("active")
        : scrollTop.classList.remove("active");
    }
  }
  scrollTop.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  window.addEventListener("load", toggleScrollTop);
  document.addEventListener("scroll", toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: "ease-in-out",
      once: true,
      mirror: false,
    });
  }
  window.addEventListener("load", aosInit);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: ".glightbox",
  });

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function (swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Frequently Asked Questions Toggle
   */
  document
    .querySelectorAll(".faq-item h3, .faq-item .faq-toggle")
    .forEach((faqItem) => {
      faqItem.addEventListener("click", () => {
        faqItem.parentNode.classList.toggle("faq-active");
      });
    });

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener("load", function (e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: "smooth",
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll(".navmenu a");

  function navmenuScrollspy() {
    navmenulinks.forEach((navmenulink) => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        document
          .querySelectorAll(".navmenu a.active")
          .forEach((link) => link.classList.remove("active"));
        navmenulink.classList.add("active");
      } else {
        navmenulink.classList.remove("active");
      }
    });
  }
  window.addEventListener("load", navmenuScrollspy);
  document.addEventListener("scroll", navmenuScrollspy);
})();

// Pagination
function paginateTable(tbodyId, paginationId, selectorId, initialRows = 10) {
  const tbody = document.getElementById(tbodyId);
  const pagination = document.getElementById(paginationId);
  const rowsPerPageSelector = document.getElementById(selectorId);

  let rowsPerPage = initialRows;
  let currentPage = 1;

  // Ambil semua baris asli (disimpan di memori)
  const allRows = Array.from(tbody.querySelectorAll("tr"));
  let filteredRows = allRows;

  function renderPage(page) {
    const totalPages = Math.ceil(filteredRows.length / rowsPerPage) || 1;
    currentPage = Math.min(Math.max(page, 1), totalPages);

    tbody.innerHTML = ""; // Kosongkan tbody dulu

    const start = (currentPage - 1) * rowsPerPage;
    const pageRows = filteredRows.slice(start, start + rowsPerPage);

    // Render baris untuk halaman sekarang
    pageRows.forEach((row, idx) => {
      const clone = row.cloneNode(true);
      // Update nomor urut
      const numCell = clone.querySelector(".row-number");
      if (numCell) numCell.textContent = start + idx + 1;
      tbody.appendChild(clone);
    });

    renderPagination(totalPages);
  }

  function renderPagination(totalPages) {
    pagination.innerHTML = "";
    if (totalPages <= 1) return;

    // Tombol Prev
    if (currentPage > 1) {
      const prev = document.createElement("button");
      prev.textContent = "Prev";
      prev.onclick = () => renderPage(currentPage - 1);
      pagination.appendChild(prev);
    }

    // Tombol halaman
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= currentPage - 1 && i <= currentPage + 1)
      ) {
        const btn = document.createElement("button");
        btn.textContent = i;
        if (i === currentPage) btn.classList.add("active");
        btn.onclick = () => renderPage(i);
        pagination.appendChild(btn);
      } else if (
        (i === currentPage - 2 && currentPage - 3 > 1) ||
        (i === currentPage + 2 && currentPage + 3 < totalPages)
      ) {
        const ellipsis = document.createElement("span");
        ellipsis.textContent = "...";
        pagination.appendChild(ellipsis);
      }
    }

    // Tombol Next
    if (currentPage < totalPages) {
      const next = document.createElement("button");
      next.textContent = "Next";
      next.onclick = () => renderPage(currentPage + 1);
      pagination.appendChild(next);
    }
  }

  // Event handler dropdown rows per page
  if (rowsPerPageSelector) {
    rowsPerPageSelector.onchange = () => {
      rowsPerPage = parseInt(rowsPerPageSelector.value);
      renderPage(1);
    };
  }

  // Fungsi debounce untuk search input
  function debounce(fn, delay) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }

  // Fungsi tambah filter search
  function addSearchFilter(inputId, searchableCols = [2, 3, 6]) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const doFilter = () => {
      const filter = input.value.toLowerCase();
      filteredRows = allRows.filter((row) =>
        searchableCols.some((i) => {
          const cell = row.cells[i];
          return cell && cell.textContent.toLowerCase().includes(filter);
        })
      );
      renderPage(1);
    };

    input.oninput = debounce(doFilter, 300);
  }

  // Render awal
  renderPage(1);

  return addSearchFilter;
}

// Contoh inisialisasi (sesuaikan ID)
document.addEventListener("DOMContentLoaded", () => {
  const addSearchAkan = paginateTable(
    "akanTableBody",
    "akanPagination",
    "akanRowsPerPage",
    10
  );
  addSearchAkan("searchAkanMagang");
  const addSearchSedang = paginateTable(
    "sedangTableBody",
    "sedangPagination",
    "sedangRowsPerPage",
    10
  );
  addSearchSedang("searchSedangMagang");
  const addSearchSelesai = paginateTable(
    "selesaiTableBody",
    "selesaiPagination",
    "selesaiRowsPerPage",
    10
  );
  addSearchSelesai("searchSelesaiMagang");
  const addSearchBatal = paginateTable(
    "batalTableBody",
    "batalPagination",
    "batalRowsPerPage",
    10
  );
  addSearchBatal("searchBatalMagang");
});

// calendar
document.addEventListener("DOMContentLoaded", function () {
  fetch("/get_tanggal_user")
    .then((response) => response.json())
    .then((tanggalList) => {
      const dates = tanggalList.map((item) => item.start);
      flatpickr("#calendar-container", {
        inline: true,
        dateFormat: "Y-m-d",
        onChange: function (selectedDates, dateStr) {
          document.getElementById("tanggal").value = dateStr;
        },
        onDayCreate: function (_, __, ___, dayElem) {
          const d = dayElem.dateObj;
          const year = d.getFullYear();
          const month = String(d.getMonth() + 1).padStart(2, "0");
          const day = String(d.getDate()).padStart(2, "0");
          const date = `${year}-${month}-${day}`;

          if (dates.includes(date)) {
            dayElem.classList.add("filled");
          }
        },
      });
    })

    .catch((error) => {
      console.error("Gagal mengambil data tanggal:", error);
    });
});

//chart
document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("magangChart").getContext("2d");

  const filteredLabels = chartLabels.filter((label) => parseInt(label) > 2020);
  const filteredData = chartLabels
    .map((label, index) => ({ year: parseInt(label), value: chartData[index] }))
    .filter((item) => item.year > 2020)
    .map((item) => item.value);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: filteredLabels,
      datasets: [
        {
          label: "Jumlah Peserta",
          data: filteredData,
          backgroundColor: "#F9A825",
          borderColor: "#F9A825",
          borderWidth: 1,
          borderRadius: 5,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            font: {
              family: "Poppins",
              size: 12,
              weight: "500",
            },
            color: "#333",
          },
          title: {
            display: true,
            text: "Jumlah Peserta",
            font: {
              family: "Poppins",
              size: 14,
              weight: "bold",
            },
            color: "#444",
          },
        },
        x: {
          ticks: {
            font: {
              family: "Poppins",
              size: 12,
              weight: "500",
            },
            color: "#333",
          },
          title: {
            display: true,
            text: "Tahun",
            font: {
              family: "Poppins",
              size: 14,
              weight: "bold",
            },
            color: "#444",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: {
            font: {
              family: "Poppins",
              size: 13,
              weight: "600",
            },
            color: "#333",
          },
        },
        tooltip: {
          enabled: true,
          titleFont: {
            family: "Poppins",
            size: 13,
            weight: "bold",
          },
          bodyFont: {
            family: "Poppins",
            size: 12,
          },
        },
      },
    },
  });
});

// audio
window.addEventListener('click', () => {
    const audio = document.getElementById('bgmusic');
    audio.muted = false;
    audio.play();
}, { once: true });

//upload foto
document
  .getElementById("gallery-photo-add")
  .addEventListener("change", function (event) {
    const previewContainer = document.getElementById("image-preview");
    previewContainer.innerHTML = ""; // bersihkan preview sebelumnya

    const files = event.target.files;

    if (files.length > 0) {
      Array.from(files).forEach((file) => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = function (e) {
            const img = document.createElement("img");
            img.src = e.target.result;
            previewContainer.appendChild(img);
          };
          reader.readAsDataURL(file);
        }
      });
    }
  });

const fileTempl = document.getElementById("file-template"),
  imageTempl = document.getElementById("image-template"),
  empty = document.getElementById("empty");

// use to store pre selected files
let FILES = {};

// check if file is of type image and prepend the initialied
// template to the target element
function addFile(target, file) {
  const isImage = file.type.match("image.*"),
    objectURL = URL.createObjectURL(file);

  const clone = isImage
    ? imageTempl.content.cloneNode(true)
    : fileTempl.content.cloneNode(true);

  clone.querySelector("h1").textContent = file.name;
  clone.querySelector("li").id = objectURL;
  clone.querySelector(".delete").dataset.target = objectURL;
  clone.querySelector(".size").textContent =
    file.size > 1024
      ? file.size > 1048576
        ? Math.round(file.size / 1048576) + "mb"
        : Math.round(file.size / 1024) + "kb"
      : file.size + "b";

  isImage &&
    Object.assign(clone.querySelector("img"), {
      src: objectURL,
      alt: file.name,
    });

  empty.classList.add("hidden");
  target.prepend(clone);

  FILES[objectURL] = file;
}

//gallery
const gallery = document.getElementById("gallery"),
  overlay = document.getElementById("overlay");

// click the hidden input of type file if the visible button is clicked
// and capture the selected files
const hidden = document.getElementById("hidden-input");
document.getElementById("button").onclick = () => hidden.click();
hidden.onchange = (e) => {
  for (const file of e.target.files) {
    addFile(gallery, file);
  }
};

// use to check if a file is being dragged
const hasFiles = ({ dataTransfer: { types = [] } }) =>
  types.indexOf("Files") > -1;

// use to drag dragenter and dragleave events.
// this is to know if the outermost parent is dragged over
// without issues due to drag events on its children
let counter = 0;

// reset counter and append file to gallery when file is dropped
function dropHandler(ev) {
  ev.preventDefault();
  for (const file of ev.dataTransfer.files) {
    addFile(gallery, file);
    overlay.classList.remove("draggedover");
    counter = 0;
  }
}

// only react to actual files being dragged
function dragEnterHandler(e) {
  e.preventDefault();
  if (!hasFiles(e)) {
    return;
  }
  ++counter && overlay.classList.add("draggedover");
}

function dragLeaveHandler(e) {
  1 > --counter && overlay.classList.remove("draggedover");
}

function dragOverHandler(e) {
  if (hasFiles(e)) {
    e.preventDefault();
  }
}

// event delegation to caputre delete events
// fron the waste buckets in the file preview cards
gallery.onclick = ({ target }) => {
  if (target.classList.contains("delete")) {
    const ou = target.dataset.target;
    document.getElementById(ou).remove(ou);
    gallery.children.length === 1 && empty.classList.remove("hidden");
    delete FILES[ou];
  }
};

// print all selected files
document.getElementById("submit").onclick = () => {
  alert(`Submitted Files:\n${JSON.stringify(FILES)}`);
  console.log(FILES);
};

// clear entire selection
document.getElementById("cancel").onclick = () => {
  while (gallery.children.length > 0) {
    gallery.lastChild.remove();
  }
  FILES = {};
  empty.classList.remove("hidden");
  gallery.append(empty);
};

(() => {
  const toggle = document.getElementById("facsimiles-pane-select");
  const panel = document.getElementById("bellum-facsimiles");
  const reference = document.getElementById("bellum-facsimiles-reference");
  const status = document.getElementById("bellum-facsimiles-status");
  const witnesses = document.getElementById("bellum-facsimiles-witnesses");
  const option = "facsimiles";

  let passage;
  let catalogue;
  let renderVersion = 0;
  const lineMaps = new Map();
  const catalogueURL = new URL(panel.dataset.catalogueUrl, window.location.href);

  const compare = (a, b) => a[0] - b[0] || a[1] - b[1];

  function loadCatalogue() {
    if (!catalogue) {
      catalogue = fetch(catalogueURL)
        .then(response => {
          if (!response.ok) throw new Error("Facsimile catalogue request failed");
          return response.json();
        })
        .then(data => {
          if (data.schemaVersion !== 2 || !Array.isArray(data.witnesses)) {
            throw new Error("Unsupported facsimile catalogue");
          }
          return data.witnesses;
        })
        .catch(error => {
          catalogue = null;
          throw error;
        });
    }
    return catalogue;
  }

  function setStatus(message = "") {
    status.textContent = message;
    status.hidden = !message;
  }

  async function loadPassage(witness, position) {
    if (!witness.lineMap) return null;
    const url = new URL(witness.lineMap, catalogueURL).href;
    if (!lineMaps.has(url)) {
      lineMaps.set(url, fetch(url).then(async response => {
        if (!response.ok) throw new Error("Passage map request failed");
        const map = await response.json();
        if (map.schemaVersion !== 1 || !map.sections || !map.imageDirectory || !map.width || !map.height) {
          throw new Error("Unsupported passage map");
        }
        return {...map, images: new URL(map.imageDirectory, url)};
      }).catch(() => {
        lineMaps.delete(url);
        return null;
      }));
    }
    const map = await lineMaps.get(url);
    const parts = map?.sections[position.join(".")];
    return parts?.length ? {map, parts} : null;
  }

  function openPassage(witness, position, excerpt, folios) {
    const dialog = document.createElement("dialog");
    dialog.className = "facsimile-passage";
    dialog.setAttribute("aria-labelledby", "facsimile-passage-heading");
    const heading = document.createElement("h2");
    heading.id = "facsimile-passage-heading";
    heading.textContent = witness.label + " · BJ " + position.join(".");
    const header = document.createElement("header");
    const close = document.createElement("button");
    close.type = "button";
    close.textContent = "Close";
    close.addEventListener("click", () => dialog.close());
    header.append(heading, close);
    dialog.append(header);

    const controller = new AbortController();
    const imageURLs = [];
    const {map, parts} = excerpt;
    const regions = parts.flatMap(part => [
      part,
      ...(part.otherRegions || []).map(region => ({...part, lines: undefined, highlight: undefined, image: undefined, ...region})),
    ]);
    for (const part of regions) {
      const folio = folios.find(record => record.label === part.folio);
      if (!folio) continue;
      const section = document.createElement("section");
      const locator = document.createElement("h3");
      locator.textContent = "f. " + part.folio + part.column;
      if (part.lines) {
        const [start, end] = part.lines;
        locator.textContent += start === end ? ", line " + start : ", lines " + start + "–" + end;
      }
      section.append(locator);

      if (part.note) {
        const note = document.createElement("p");
        note.textContent = part.note;
        section.append(note);
      }
      if (part.box) {
        const [x, y, width, height] = part.box;
        const frame = document.createElement("div");
        frame.className = "facsimile-crop";
        const scanSize = map.scanSizes?.[part.scan];
        const cropWidth = scanSize ? width * scanSize[0] / map.width : width;
        const cropHeight = scanSize ? height * scanSize[1] / map.height : height;
        frame.style.aspectRatio = cropWidth + "/" + cropHeight;
        const image = document.createElement("img");
        image.alt = "Passage on " + locator.textContent;
        const status = document.createElement("p");
        status.textContent = "Loading image…";
        const details = document.createElement("details");
        const contextLabel = document.createElement("summary");
        contextLabel.textContent = "Show the passage on the folio";
        const context = document.createElement("div");
        context.className = "facsimile-folio-context";
        const fullImage = document.createElement("img");
        fullImage.alt = "Scan of f. " + part.folio + " with the passage marked";
        const marked = document.createElement("span");
        marked.className = "facsimile-crop-outline";
        marked.setAttribute("aria-hidden", "true");
        marked.style.left = 100 * x / map.width + "%";
        marked.style.top = 100 * y / map.height + "%";
        marked.style.width = 100 * width / map.width + "%";
        marked.style.height = 100 * height / map.height + "%";
        context.append(fullImage, marked);
        details.append(contextLabel, context);
        details.hidden = true;
        const unavailable = () => {
          frame.hidden = true;
          details.hidden = true;
          status.hidden = false;
          status.textContent = "Passage image unavailable.";
        };
        image.addEventListener("load", () => {
          status.hidden = true;
          frame.hidden = false;
          details.hidden = false;
        }, {once: true});
        frame.hidden = true;
        frame.append(image);
        for (const [left, top, w, h] of part.highlight || []) {
          const outline = document.createElement("span");
          outline.className = "facsimile-crop-outline";
          outline.setAttribute("aria-hidden", "true");
          outline.style.left = 100 * (left - x) / width + "%";
          outline.style.top = 100 * (top - y) / height + "%";
          outline.style.width = 100 * w / width + "%";
          outline.style.height = 100 * h / height + "%";
          frame.append(outline);
        }
        section.append(status, frame, details);
        const extension = map.scanExtension === "jpg" ? ".jpg" : ".webp";
        const scanURL = new URL(String(part.scan).padStart(4, "0") + extension, map.images);
        const showScanCrop = () => {
          frame.style.aspectRatio = cropWidth + "/" + cropHeight;
          image.style.width = 100 * map.width / width + "%";
          image.style.left = -100 * x / width + "%";
          image.style.top = -100 * y / height + "%";
          fetch(scanURL, {signal: controller.signal}).then(response => {
            if (!response.ok) throw new Error("Scan request failed");
            return response.blob();
          }).then(blob => {
            if (controller.signal.aborted) return;
            const objectURL = URL.createObjectURL(blob);
            imageURLs.push(objectURL);
            image.src = objectURL;
            fullImage.src = objectURL;
          }).catch(() => {
            if (!controller.signal.aborted) unavailable();
          });
        };
        let usingPassageImage = Boolean(part.image);
        image.addEventListener("error", () => {
          if (usingPassageImage) {
            usingPassageImage = false;
            showScanCrop();
          } else {
            unavailable();
          }
        });
        if (usingPassageImage) {
          image.style.width = "100%";
          if (part.imageSize) frame.style.aspectRatio = part.imageSize.join("/");
          image.style.left = "0";
          image.style.top = "0";
          image.src = new URL(part.image, map.images).href;
          details.addEventListener("toggle", () => {
            if (details.open && !fullImage.getAttribute("src")) fullImage.src = scanURL.href;
          });
          fullImage.addEventListener("error", () => {
            fullImage.removeAttribute("src");
            fullImage.alt = "Folio image unavailable.";
          });
        } else {
          showScanCrop();
        }
      } else {
        const status = document.createElement("p");
        status.textContent = "Column location";
        section.append(status);
      }
      const fullFolio = document.createElement("a");
      fullFolio.href = folio.url;
      fullFolio.target = "_blank";
      fullFolio.rel = "noopener";
      fullFolio.textContent = "Open full folio";
      section.append(fullFolio);
      dialog.append(section);
    }

    if (witness.digitisation) {
      const source = document.createElement("p");
      source.className = "facsimile-image-credit";
      const record = document.createElement("a");
      record.href = witness.digitisation.url;
      record.textContent = witness.digitisation.credit || witness.shelfmark;
      record.title = witness.digitisation.urn;
      const rights = document.createElement("a");
      rights.href = witness.digitisation.rightsUrl;
      rights.textContent = witness.digitisation.rightsLabel;
      source.append("Images from ", record, " · ", rights);
      dialog.append(source);
    }

    dialog.addEventListener("close", () => {
      controller.abort();
      imageURLs.forEach(url => URL.revokeObjectURL(url));
      dialog.remove();
    }, {once: true});
    document.body.append(dialog);
    dialog.showModal();
  }

  function renderWitness(witness, folios, position, excerpt) {
    const entry = document.createElement("li");
    const label = document.createElement("h3");
    label.className = "facsimile-witness-name";
    label.textContent = witness.label;

    const shelfmark = document.createElement("p");
    shelfmark.className = "facsimile-shelfmark";
    shelfmark.textContent = witness.shelfmark;

    const links = document.createElement("ul");
    links.className = "facsimile-folios";
    for (const folio of folios) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = folio.url;
      link.target = "_blank";
      link.rel = "noopener";
      const columns = folio.columnLabels;
      link.textContent = "f. " + folio.label + columns.join("–");
      const columnLabel = columns.length === 1 ? "column " : "columns ";
      link.setAttribute("aria-label",
        witness.label + ", folio " + folio.label + ", " + columnLabel + columns.join(" and ") + " (opens in a new tab)"
      );
      item.append(link);
      links.append(item);
    }
    entry.append(label, shelfmark);
    if (excerpt?.parts.some(part => part.box)) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "facsimile-show-passage";
      button.setAttribute("aria-haspopup", "dialog");
      button.setAttribute("aria-label", witness.label + ", show passage");
      button.textContent = "Show passage";
      button.addEventListener("click", () => openPassage(witness, position, excerpt, folios));
      entry.append(button);
    }
    entry.append(links);
    return entry;
  }

  async function render() {
    const version = ++renderVersion;
    const enabled = new URLSearchParams(window.location.search).get(option) === "1";
    toggle.checked = enabled;
    panel.hidden = !enabled;
    panel.parentElement.classList.toggle("has-facsimiles", enabled);
    if (!enabled) return;

    const section = passage?.section;
    const hasSection = Number.isInteger(section) && section > 0;
    reference.hidden = !hasSection;
    reference.textContent = hasSection ? "BJ " + passage.book + "." + section : "";
    witnesses.replaceChildren();
    if (!hasSection) {
      setStatus(passage ? "Select Niese section under the viewing levels." : "Loading passage…");
      return;
    }

    setStatus("Loading facsimile links…");
    const position = [passage.book, section];
    try {
      const records = await loadCatalogue();
      const rendered = await Promise.all(records.map(async witness => {
        const excerpt = await loadPassage(witness, position);
        const folios = witness.folios.flatMap(folio => {
          const columnLabels = folio.columns
            .filter(column => compare(column.start, position) <= 0 && compare(position, column.end) <= 0)
            .filter(column => !excerpt || excerpt.parts.some(part => part.folio === folio.label && part.column === column.label))
            .map(column => column.label);
          return columnLabels.length ? [{...folio, columnLabels}] : [];
        });
        if (!folios.length) return null;
        return renderWitness(witness, folios, position, excerpt);
      }));
      if (version !== renderVersion) return;
      witnesses.append(...rendered.filter(Boolean));
      setStatus(witnesses.childElementCount ? "" : "No folios are mapped for this section.");
    } catch {
      if (version === renderVersion) setStatus("Facsimile links could not be loaded.");
    }
  }

  toggle.addEventListener("change", () => {
    const url = new URL(window.location.href);
    if (toggle.checked) url.searchParams.set(option, "1");
    else url.searchParams.delete(option);
    window.history.replaceState(window.history.state, "", url);
    render();
  });
  document.addEventListener("bellum-view-rendered", event => {
    passage = event.detail;
    render();
  });
  window.addEventListener("popstate", () => {
    passage = null;
    render();
  });
  render();
})();

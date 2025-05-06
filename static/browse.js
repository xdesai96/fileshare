let selectedFiles = [];

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return console.warn(`Modal "${modalId}" not found`);
  const content = modal.querySelector(".modal-content");

  modal.style.display = "flex";
  modal.style.animation = "fadeIn 0.3s ease-out forwards";
  if (content) content.style.animation = "slideIn 0.3s ease-out forwards";
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  const content = modal.querySelector(".modal-content");

  modal.style.animation = "fadeOut 0.3s ease-in forwards";
  if (content) content.style.animation = "slideOut 0.3s ease-in forwards";

  setTimeout(() => {
    modal.style.display = "none";
    modal.style.animation = "";
    if (content) content.style.animation = "";
  }, 300);
}

function bindModalButton(buttonId, modalId) {
  const button = document.getElementById(buttonId);
  if (button) {
    button.addEventListener("click", () => openModal(modalId));
  }
}

function setupCloseButtons() {
  document.querySelectorAll(".close-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const modal = button.closest(".modal");
      if (modal) closeModal(modal.id);
    });
  });
}

function setupOutsideClickClose() {
  window.addEventListener("click", function (event) {
    document.querySelectorAll(".modal").forEach((modal) => {
      if (event.target === modal) closeModal(modal.id);
    });
  });
}

function setupDropZone(dropZoneId, fileInputId, previewListId) {
  const dropZone = document.getElementById(dropZoneId);
  const fileInput = document.getElementById(fileInputId);
  const previewList = document.getElementById(previewListId);

  if (!dropZone || !fileInput || !previewList) return;

  let selectedFiles = [];

  function updateFileInput() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach((file) => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
  }

  function renderPreview() {
    previewList.innerHTML = "";

    const addedFolders = new Set();

    selectedFiles.forEach((file, index) => {
      const li = document.createElement("li");
      let label = "";

      if (file.webkitRelativePath) {
        const folderName = file.webkitRelativePath.split("/")[0];
        if (addedFolders.has(folderName)) return;
        addedFolders.add(folderName);
        label = `📁 ${folderName}`;
      } else {
        label = file.name;
      }

      li.textContent = label;

      const removeBtn = document.createElement("button");
      removeBtn.textContent = "✕";
      removeBtn.className = "remove-file-btn";
      removeBtn.addEventListener("click", () => {
        if (file.webkitRelativePath) {
          // Удаляем ВСЕ файлы из этой папки
          const folderPrefix = file.webkitRelativePath.split("/")[0] + "/";
          selectedFiles = selectedFiles.filter(
            (f) =>
              !(
                f.webkitRelativePath &&
                f.webkitRelativePath.startsWith(folderPrefix)
              ),
          );
        } else {
          selectedFiles.splice(index, 1);
        }
        renderPreview();
        updateFileInput();
      });

      li.appendChild(removeBtn);
      previewList.appendChild(li);
    });
  }

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");

    const items = Array.from(e.dataTransfer.items);
    const newFiles = [];

    async function traverseFileTree(item, path = "") {
      return new Promise((resolve) => {
        if (item.kind === "file") {
          const entry = item.webkitGetAsEntry();
          if (!entry) return resolve();

          if (entry.isFile) {
            entry.file((file) => {
              file.webkitRelativePath = path + file.name;
              newFiles.push(file);
              resolve();
            });
          } else if (entry.isDirectory) {
            const dirReader = entry.createReader();
            const entries = [];

            const readEntries = () => {
              dirReader.readEntries(async (results) => {
                if (!results.length) {
                  for (const entry of entries) {
                    await traverseFileTree(
                      { kind: "file", webkitGetAsEntry: () => entry },
                      path + entry.name + "/",
                    );
                  }
                  resolve();
                } else {
                  entries.push(...results);
                  readEntries();
                }
              });
            };

            readEntries();
          }
        } else {
          resolve();
        }
      });
    }

    await Promise.all(items.map((item) => traverseFileTree(item)));

    selectedFiles = [...selectedFiles, ...newFiles];
    renderPreview();
    updateFileInput();
  });

  fileInput.addEventListener("change", () => {
    const newFiles = Array.from(fileInput.files);
    selectedFiles = [...selectedFiles, ...newFiles];
    renderPreview();
    updateFileInput();
  });
}

function changeRole(username, newRole) {
  fetch(`/change_role/${username}/${newRole}`, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload();
      } else {
        alert(data.message || "Failed to update role");
      }
    })
    .catch((error) => {
      console.error("Error changing role:", error);
    });
}

document
  .getElementById("updateFileShareBtn")
  .addEventListener("click", function () {
    fetch("/update_fileshare", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("FileShare updated successfully!");
          console.log(data.output); // Можно логировать вывод команды
        } else {
          alert("Failed to update FileShare: " + data.error);
          console.error(data.error); // Логируем ошибку
        }
      })
      .catch((error) => {
        alert("Error occurred while updating FileShare!");
        console.error(error);
      });
  });

document.addEventListener("DOMContentLoaded", () => {
  bindModalButton("adminPanelBtn", "adminModal");
  bindModalButton("openAddUserModal", "addUserModal");
  bindModalButton("settingsBtn", "settingsModal");
  bindModalButton("uploadFileBtn", "uploadModal");

  setupCloseButtons();
  setupOutsideClickClose();

  setupDropZone("dropZone", "fileInput", "filePreviewList");
});

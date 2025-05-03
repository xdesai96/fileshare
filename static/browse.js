let selectedFiles = [];

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return console.warn(`Modal "${modalId}" not found`);
  const content = modal.querySelector('.modal-content');

  modal.style.display = 'flex';
  modal.style.animation = "fadeIn 0.3s ease-out forwards";
  if (content) content.style.animation = "slideIn 0.3s ease-out forwards";
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  const content = modal.querySelector('.modal-content');

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
  document.querySelectorAll(".close-btn").forEach(button => {
    button.addEventListener("click", () => {
      const modal = button.closest(".modal");
      if (modal) closeModal(modal.id);
    });
  });
}

function setupOutsideClickClose() {
  window.addEventListener("click", function (event) {
    document.querySelectorAll(".modal").forEach(modal => {
      if (event.target === modal) closeModal(modal.id);
    });
  });
}

function setupDropZone(dropZoneId, fileInputId, previewListId) {
  const dropZone = document.getElementById(dropZoneId);
  const fileInput = document.getElementById(fileInputId);
  const previewList = document.getElementById(previewListId);

  if (!dropZone || !fileInput || !previewList) return;


  function updateFileInput() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
  }

  function renderPreview() { 
    previewList.innerHTML = '';
    selectedFiles.forEach((file, index) => {
      const li = document.createElement('li');
      li.textContent = file.name;

      const removeBtn = document.createElement('button');
      removeBtn.textContent = '✕';
      removeBtn.className = 'remove-file-btn';
      removeBtn.addEventListener('click', () => {
        selectedFiles.splice(index, 1);
        renderPreview();
        updateFileInput();
      });

      li.appendChild(removeBtn);
      previewList.appendChild(li);
    });
  }

  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    selectedFiles = [...selectedFiles, ...Array.from(e.dataTransfer.files)];
    renderPreview();
    updateFileInput();
  });

  fileInput.addEventListener('change', () => {
    selectedFiles = [...selectedFiles, ...Array.from(fileInput.files)];
    renderPreview();
    updateFileInput();
  });
}

function changeRole(username, newRole) {
  fetch(`/change_role/${username}/${newRole}`, {
    method: 'POST'
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else {
        alert(data.message || 'Failed to update role');
      }
    })
    .catch(error => {
      console.error('Error changing role:', error);
    });
}


document.addEventListener("DOMContentLoaded", () => {
  bindModalButton("adminPanelBtn", "adminModal");
  bindModalButton("openAddUserModal", "addUserModal");
  bindModalButton("settingsBtn", "settingsModal");
  bindModalButton("uploadFileBtn", "uploadModal");

  setupCloseButtons();
  setupOutsideClickClose();

  setupDropZone('dropZone', 'fileInput', 'filePreviewList');
});


const uploadArea = document.getElementById("uploadArea");
const fileTime = document.getElementById("fileInput");
const fileListDiv = document.getElementById("fileList");
const uploadButton = document.getElementById("uploadBtn");
const deleteButton = document.getElementById("deleteBtn");
const uploadMessage = document.getElementById("uploadMessage");
const uploadsNav = document.getElementById("uploadsNav");
const previewNav = document.getElementById("previewNav");
const uploadFilesPanel = document.getElementById("uploadFilesPanel");
const uploadedFilesList = document.getElementById("uploadedFilesList");
const totalFiles = document.getElementById("totalFiles");
const navLinks = document.querySelectorAll(".nav-links li a");
const loginPopup = document.getElementById("loginPopup")
const profilePopup = document.getElementById("profilePopup");
const loginBtn = document.getElementById("loginBtn");
const usernameInput = document.getElementById("username");
const profileName = document.getElementById("profileName");
const navProfile = navLinks[1]; 
const navLogout = navLinks[3];  

let selectedFiles = [];
let uploadedFiles = [];
let previewVisible = true;
let uploadsVisible = false;
let loggedIn = false;
let username = "";

fileInput.onchange = () => handleFiles(fileInput.files);

uploadArea.onclick = () => {
    fileInput.value = "";
    fileInput.click();
};

["dragenter", "dragover", "dragleave", "drop"].forEach(event => {
    uploadArea.addEventListener(event, e => e.preventDefault());
});

uploadArea.addEventListener("dragover", () => uploadArea.classList.add("active"));
uploadArea.addEventListener("dragleave", () => uploadArea.classList.remove("active"));
uploadArea.addEventListener("drop", e => {
    uploadArea.classList.remove("active");
    handleFiles(e.dataTransfer.files);
});

function createCSVPreview(file) {
    return new Promise(resolve => {
        const reader = new FileReader();
        reader.onload = () => {
            const lines = reader.result.split("\n").slice(0, 3); 
            resolve(lines.join("<br>"));
        };
        reader.readAsText(file);
    });
}

async function handleFiles(files) {
    for (let file of files) {
        if (!file.name.endsWith(".csv")) {
            alert(`${file.name} is not a CSV file`);
            continue;
        }

        if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            alert(`${file.name} is already selected`);
            continue;
        }

        if (uploadedFiles.some(f => f.name === file.name && f.size === file.size)) {
            alert(`${file.name} is already uploaded`);
            continue;
        }

        selectedFiles.push(file);

        const preview = await createCSVPreview(file);
        const item = document.createElement("div");
        item.classList.add("file-item");
        item.innerHTML = `
            <div class="thumb">📄</div>
            <div>
                <strong>${file.name}</strong><br>
                <small>${Math.round(file.size / 1024)} KB</small>
                <div class="csv-preview">${preview}</div>
            </div>
        `;
        
        item.addEventListener("click", () => {
            item.classList.toggle("selected");

        })

        fileListDiv.appendChild(item);
    }
}

function renderFiles() {
    uploadedFilesList.innerHTML = "";

    uploadedFiles.forEach(file => {
        const item = document.createElement("div");
        item.classList.add("uploaded-item");
        item.innerHTML = `
            <strong>${file.name}</strong>
            <small>${(file.size / 1024).toFixed(1)} KB</small>
            <small class="timestamp" data-time="${file.timestamp}">${file.timestamp}</small>
        `;

        item.addEventListener("click", (e) => {
            if (!e.target.classList.contains("timestamp")) {
                item.classList.toggle("selected");
            }
        });

        const ts = item.querySelector(".timestamp");
        ts.addEventListener("click", (e) => {
            const time = e.target.dataset.time;
            alert(`You clicked on timestamp: ${time}`);
            e.stopPropagation(); 
        });

        uploadedFilesList.appendChild(item);
    });

    totalFiles.textContent = uploadedFiles.length;
}

uploadButton.onclick = async () => {
  if (selectedFiles.length === 0) {
    alert("No file has been selected");
    return;
  }

  try {
    for (const file of selectedFiles) {
      await uploadFile(file); 
      uploadedFiles.push({
        name: file.name,
        size: file.size,
        timestamp: new Date().toLocaleString()
      });
    }

    renderFiles();
    selectedFiles = [];
    fileListDiv.innerHTML = "";

    uploadMessage.textContent = "Files uploaded successfully!";
    uploadMessage.style.display = "block";
    setTimeout(() => uploadMessage.style.display = "none", 3000);

  } catch (err) {
    console.error(err);
    alert("Upload failed — check console");
  }
};

deleteButton.onclick = () => {
    const selectedPending = fileListDiv.querySelectorAll(".file-item.selected")
    const selectedUploaded = uploadedFilesList.querySelectorAll(".uploaded-item.selected");

    if (selectedPending.length === 0 & selectedUploaded.length === 0){
        alert("no file selected");
        return;
    }

    let filenames = [];

    selectedPending.forEach(div => {
        filenames.push(div.querySelector("strong").textContent);
    });

    selectedUploaded.forEach(div => {
        filenames.push(div.querySelector("strong").textContent);
    });

    const ok = confirm(`Are you sure you want to delete:\n\n${filenames.join("\n")}`);
    if (!ok) return

    selectedPending.forEach(div => {
        const fileName = div.querySelector("strong").textContent;
        selectedFiles = selectedFiles.filter(f => f.name !== fileName);
        div.remove();
    });

    selectedUploaded.forEach(div => {
        const fileName = div.querySelector("strong").textContent;
        uploadedFiles = uploadedFiles.filter(f => f.name !== fileName);
        div.remove();
    });

    totalFiles.textContent = uploadedFiles.length;
};


uploadFilesPanel.style.display = "none";
uploadsNav.addEventListener("click", e => {
    e.preventDefault();
    uploadsVisible = !uploadsVisible;
    uploadFilesPanel.style.display = uploadsVisible ? "block" : "none";
    if (uploadsVisible) uploadFilesPanel.scrollIntoView({ behavior: "smooth" });
});

previewNav.addEventListener("click", e => {
    e.preventDefault();
    previewVisible = !previewVisible;

    if (previewVisible) {
        fileListDiv.innerHTML = "";
        selectedFiles.forEach(async file => {
            const preview = await createCSVPreview(file);
            const item = document.createElement("div");
            item.classList.add("file-item");
            item.innerHTML = `
                <div class="thumb">📄</div>
                <div>
                    <strong>${file.name}</strong><br>
                    <small>${Math.round(file.size / 1024)} KB</small>
                    <div class="csv-preview">${preview}</div>
                </div>
            `;
            fileListDiv.appendChild(item);
        });
    } else {
        fileListDiv.innerHTML = "";
    }
});

navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault()

        if (link.classList.contains("active")) {
            link.classList.remove("active");
            return;
        }

        navLinks.forEach(l => l.classList.remove("active"));

        link.classList.add("active");

    });
});

navLinks[1].addEventListener("click", (e) => {
    e.preventDefault();

    if (!loggedIn) {
        loginPopup.classList.toggle("hidden");
    } else {
        profilePopup.classList.toggle("hidden");
    }
});

loginBtn.addEventListener("click", () => {
    username = usernameInput.value.trim();
    if (!username) return alert("Enter a name!");
    loggedIn = true;
    profileName.textContent = username;

    loginPopup.classList.add("hidden");
    profilePopup.classList.remove("hidden");
});

navLogout.addEventListener("click", (e) => {
    e.preventDefault();
    loggedIn = false;
    username = "";
    profilePopup.classList.add("hidden");
    alert("You are logged out!");
});
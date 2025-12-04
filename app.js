let uploadArea = document.getElementById("uploadArea");
let fileInput = document.getElementById("fileInput");
let fileList = document.getElementById("fileList");

uploadArea.onclick = () => fileInput.click();

fileInput.onchange = () => {
    handleFiles(fileInput.files);
};

["dragenter", "dragover", "dragleave", "drop"].forEach(event => {
    uploadArea.addEventListener(event, e => e.preventDefault());
});

uploadArea.addEventListener("dragover", () => {
    uploadArea.classList.add("active");
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("active");
});

uploadArea.addEventListener("drop", e => {
    uploadArea.classList.remove("active");
    handleFiles(e.dataTransfer.files);
});

async function handleFiles(files) {
    for (let file of files) {
        await uploadToS3(file);
    }
}

async function uploadToS3(file){
    const res = await fetch("/presign?filename=" + file.name);
    const data = await res.json();

    const uploadUrl = data.uploadUrl;
    const fileUrl = data.fileUrl;

    const upload = await fetch(uploadUrl, {
        method: "PUT",
        body: file,
        headers: {
            "Content-Type": file.type
        }
    });
    if (upload.ok) {
        console.log("Uploaded:", fileUrl);
        addFileToList(file, fileUrl);
    } else {
        console.error("S3 Upload failed");
    }
}

function addFileToList(file, url) {
    let item = document.createElement("div");
    item.classList.add("file-item");
    item.innerHTML = `
        <strong>${file.name}</strong> uploaded → 
        <a href="${url}" target="_blank">view</a>
    `;
    fileList.appendChild(item);
}
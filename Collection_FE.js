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

function handleFiles(files) {
    for (let file of files) {
        let item = document.createElement("div");
        item.classList.add("file-item");
        item.textContent = file.name + " (" + Math.round(file.size / 1024) + " KB)";
        fileList.appendChild(item);
    }
}

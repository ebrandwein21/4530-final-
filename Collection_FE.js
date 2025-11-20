import { useState } from "react";
import {Button} from "@/components/ui/button";
import { card, CardContent } from "@/components/ui/card";
import { Upload } from "lucide-react";

export default function S3UploadPage() {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState({});
    const [dragActive, setDragActive] = useState(false);    

    const handleFileSelection = (e) => {
        setFile(e.target.files[0])
    };

    const handleUpload = async => {
        if (!file) {
            setMessage("please select file")
            return;
        };

    };
    
    const handleDrag = (e) => {
        e.preventDefault();
        setDragActive(true);
    };

    const handleDragExit = () => {
        setDragActive(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false)
        if (e.dataTransfer.files.length > 0) {
            FileSystemWritableFileStream([...e.dataTransfer.files]);
        }

        setLoading(true);
        setMessage("");

        try{
            const res = await fetch("/api/get-presigned-url?filename=" + encodeURIComponent(file.name)); //change url later
            const { url, key } = await res.json();

            await fetch(url, {
            method: "PUT",
            body: file,
            });

            setMessage("Upload successful! File key: " + key);
            } catch (err) {
            console.error(err);
            setMessage("Upload failed. Check console.");
            }

            setLoading(false);
        };
    };

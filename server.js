import express from "express";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const app = express();
const PORT = 3000;

const s3 = new S3Client({
    region: "us-east-1",
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY,
        secretAccessKey: process.env.AWS_SECRET_KEY
    }
});

app.get("/presign", async (req, res) => {
    const fileName = req.query.filename;

    const command = new PutObjectCommand({
        Bucket: "your-bucket-name",
        Key: fileName,
        ContentType: "application/octet-stream"
    });

    const uploadUrl = await getSignedUrl(s3, command, { expiresIn: 60 });

    res.json({
        uploadUrl,
        fileUrl: `https://${"your-bucket-name"}.s3.amazonaws.com/${fileName}`
    });
});

app.listen(PORT, () => console.log("Server running on port", PORT));

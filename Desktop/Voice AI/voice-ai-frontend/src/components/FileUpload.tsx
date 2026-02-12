import { useState } from "react";

export default function FileUpload() {
  const [error, setError] = useState("");

  const handleFileChange = (e: any) => {
    const file = e.target.files[0];

    if (!file) return;

    const allowedTypes = ["application/pdf", "image/jpeg", "image/png"];
    const maxSize = 2 * 1024 * 1024; // 2MB

    if (!allowedTypes.includes(file.type)) {
      setError("Only PDF, JPG, PNG allowed");
      return;
    }

    if (file.size > maxSize) {
      setError("File must be under 2MB");
      return;
    }

    setError("");
    alert("File uploaded successfully");
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <p style={{ color: "red" }}>{error}</p>
      <small>Supported: PDF, JPG, PNG | Max: 2MB</small>
    </div>
  );
}

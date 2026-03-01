import { useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { api } from "../../lib/api";

interface Props {
  brandId?: string;
  onUploadComplete?: (filename: string) => void;
  onError?: (error: string) => void;
}

export default function CSVUploader({ brandId = "default", onUploadComplete, onError }: Props) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      onError?.('Please upload a CSV file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      onError?.('File size must be less than 10MB');
      return;
    }

    setUploading(true);
    setProgress(10);

    try {
      // Step 1: Get pre-signed URL from API Gateway
      setProgress(20);
      const presignedData = await api.getPresignedUrl(brandId);

      // Step 2: Upload directly to S3 (bypasses API Gateway)
      setProgress(40);
      const filename = await api.uploadToS3(presignedData, file);

      // Step 3: Trigger ESG ingestion
      setProgress(70);
      const result = await api.ingestESG(filename, brandId);

      setProgress(100);
      
      if (result.status === 'processing') {
        // Large CSV - async processing via Step Functions
        onUploadComplete?.(filename);
      } else {
        // Small CSV - synchronous processing complete
        onUploadComplete?.(filename);
      }
    } catch (error) {
      onError?.((error as Error).message);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleChange}
        style={{ display: 'none' }}
      />

      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{
          cursor: uploading ? 'not-allowed' : 'pointer',
          opacity: uploading ? 0.6 : 1,
        }}
      >
        {uploading ? (
          <>
            <div className="spinner" style={{ width: 28, height: 28, marginBottom: 12 }} />
            <div className="mono-label">Uploading... {progress}%</div>
            <div className="sub-text" style={{ marginTop: 4 }}>
              {progress < 40 ? 'Getting upload URL...' :
               progress < 70 ? 'Uploading to S3...' :
               'Processing ESG data...'}
            </div>
          </>
        ) : (
          <>
            <div style={{ fontSize: 32, opacity: 0.4, marginBottom: 8 }}>📊</div>
            <div className="mono-label">Upload Historical Posts CSV</div>
            <div className="sub-text">
              Drag & drop or click to browse
            </div>
            <div style={{ 
              fontFamily: "var(--font-mono)", 
              fontSize: 9, 
              color: "var(--text-muted)", 
              marginTop: 8 
            }}>
              Required columns: post_text, likes, comments, shares, platform
              <br />
              Max 10MB · Direct S3 upload (bypasses API Gateway)
            </div>
          </>
        )}
      </div>

      {uploading && (
        <div style={{ 
          marginTop: 12, 
          height: 4, 
          background: 'var(--border)', 
          borderRadius: 2,
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${progress}%`,
            background: 'var(--teal)',
            transition: 'width 0.3s ease'
          }} />
        </div>
      )}
    </div>
  );
}
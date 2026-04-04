"use client";

import { useCallback, useRef, useState } from "react";

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  disabled?: boolean;
}

export default function ImageUpload({ onImageSelect, disabled }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const ALLOWED = ["image/jpeg", "image/png", "image/webp"];
  const MAX_MB = 10;

  const handleFile = useCallback(
    (file: File) => {
      setError(null);
      if (!ALLOWED.includes(file.type)) {
        setError("Only JPG, PNG, or WebP images are allowed.");
        return;
      }
      if (file.size > MAX_MB * 1024 * 1024) {
        setError(`File size must be under ${MAX_MB} MB.`);
        return;
      }
      const url = URL.createObjectURL(file);
      setPreview(url);
      onImageSelect(file);
    },
    [onImageSelect]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="flex flex-col gap-3">
      <label className="text-sm font-semibold text-violet-300 uppercase tracking-wider">
        Character Image
      </label>

      <div
        role="button"
        aria-label="Upload character image"
        tabIndex={disabled ? -1 : 0}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && !disabled && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={[
          "relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-6 transition-all cursor-pointer select-none min-h-[220px]",
          isDragging
            ? "drop-active"
            : "border-violet-700/50 bg-white/5 hover:bg-violet-950/20 hover:border-violet-500",
          disabled ? "opacity-50 pointer-events-none" : "",
        ].join(" ")}
      >
        {preview ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={preview}
            alt="Character preview"
            className="max-h-48 max-w-full rounded-xl object-contain shadow-lg"
          />
        ) : (
          <>
            <svg
              className="h-12 w-12 text-violet-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm text-gray-400 text-center">
              <span className="text-violet-400 font-medium">Click to upload</span> or drag &amp; drop
            </p>
            <p className="text-xs text-gray-600">JPG, PNG, WebP — max {MAX_MB} MB</p>
          </>
        )}
      </div>

      {preview && (
        <button
          type="button"
          onClick={() => { setPreview(null); if (inputRef.current) inputRef.current.value = ""; }}
          className="text-xs text-gray-500 hover:text-red-400 transition-colors self-end"
        >
          Remove image
        </button>
      )}

      {error && (
        <p role="alert" className="text-xs text-red-400">
          {error}
        </p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={onInputChange}
        disabled={disabled}
      />
    </div>
  );
}

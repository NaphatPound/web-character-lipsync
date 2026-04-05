"use client";

import { useState } from "react";

const MAX_CHARS = 500;

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  onGenerate?: (topic: string) => Promise<void>;
  isGenerating?: boolean;
}

export default function TextInput({
  value,
  onChange,
  disabled,
  onGenerate,
  isGenerating,
}: TextInputProps) {
  const [showTopic, setShowTopic] = useState(false);
  const [topic, setTopic] = useState("");
  const remaining = MAX_CHARS - value.length;
  const isNearLimit = remaining <= 50;

  const handleGenerate = async () => {
    if (!onGenerate) return;
    await onGenerate(topic);
    setShowTopic(false);
    setTopic("");
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <label
          htmlFor="dialogue-input"
          className="text-sm font-semibold text-violet-300 uppercase tracking-wider"
        >
          Dialogue Text
        </label>

        {onGenerate && (
          <button
            type="button"
            onClick={() => setShowTopic((v) => !v)}
            disabled={disabled || isGenerating}
            className={[
              "flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-medium transition-all",
              disabled || isGenerating
                ? "opacity-40 cursor-not-allowed bg-violet-700/30 text-violet-400"
                : "bg-violet-600/30 hover:bg-violet-600/50 text-violet-300 hover:text-white border border-violet-600/40 hover:border-violet-500",
            ].join(" ")}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 21 12 17.77 5.82 21 7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            Auto Generate
          </button>
        )}
      </div>

      {/* Inline topic input */}
      {showTopic && onGenerate && (
        <div className="flex gap-2">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
            placeholder="Topic (optional) — e.g. greet the player, explain the quest…"
            className="flex-1 rounded-xl border border-violet-700/50 bg-white/5 px-3 py-2 text-sm text-white placeholder-gray-600 outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
          />
          <button
            type="button"
            onClick={handleGenerate}
            disabled={isGenerating}
            className={[
              "px-4 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap",
              isGenerating
                ? "bg-violet-700/40 text-violet-400 cursor-not-allowed"
                : "bg-violet-600 hover:bg-violet-500 text-white",
            ].join(" ")}
          >
            {isGenerating ? (
              <span className="flex items-center gap-1.5">
                <svg className="animate-spin" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
                Generating…
              </span>
            ) : (
              "Generate"
            )}
          </button>
        </div>
      )}

      <textarea
        id="dialogue-input"
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_CHARS))}
        placeholder="Type what your character will say…  or click Auto Generate ↑"
        disabled={disabled || isGenerating}
        rows={6}
        className={[
          "w-full rounded-2xl border bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-600",
          "resize-none transition-all outline-none",
          "focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20",
          disabled || isGenerating
            ? "opacity-50 cursor-not-allowed border-white/10"
            : "border-violet-700/50 hover:border-violet-600",
        ].join(" ")}
      />

      <div className="flex justify-end">
        <span
          className={[
            "text-xs tabular-nums",
            isNearLimit ? "text-orange-400" : "text-gray-600",
          ].join(" ")}
        >
          {remaining} / {MAX_CHARS}
        </span>
      </div>
    </div>
  );
}

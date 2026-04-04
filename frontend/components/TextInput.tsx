"use client";

const MAX_CHARS = 500;

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function TextInput({ value, onChange, disabled }: TextInputProps) {
  const remaining = MAX_CHARS - value.length;
  const isNearLimit = remaining <= 50;

  return (
    <div className="flex flex-col gap-3">
      <label
        htmlFor="dialogue-input"
        className="text-sm font-semibold text-violet-300 uppercase tracking-wider"
      >
        Dialogue Text
      </label>

      <textarea
        id="dialogue-input"
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_CHARS))}
        placeholder="Type what your character will say..."
        disabled={disabled}
        rows={6}
        className={[
          "w-full rounded-2xl border bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-600",
          "resize-none transition-all outline-none",
          "focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20",
          disabled
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

"use client";

export const VOICES = [
  { value: "th-TH-PremwadeeNeural", label: "Premwadee — หญิง (ไทย)" },
  { value: "th-TH-NiwatNeural",     label: "Niwat — ชาย (ไทย)" },
  { value: "en-US-JennyNeural",     label: "Jenny — Female (EN-US)" },
  { value: "en-US-GuyNeural",       label: "Guy — Male (EN-US)" },
  { value: "en-GB-SoniaNeural",     label: "Sonia — Female (EN-GB)" },
];

interface VoiceSettingsProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function VoiceSettings({ value, onChange, disabled }: VoiceSettingsProps) {
  return (
    <div className="flex flex-col gap-3">
      <label
        htmlFor="voice-select"
        className="text-sm font-semibold text-violet-300 uppercase tracking-wider"
      >
        Voice
      </label>

      <select
        id="voice-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={[
          "w-full rounded-2xl border bg-white/5 px-4 py-3 text-sm text-white",
          "transition-all outline-none appearance-none cursor-pointer",
          "focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20",
          disabled
            ? "opacity-50 cursor-not-allowed border-white/10"
            : "border-violet-700/50 hover:border-violet-600",
        ].join(" ")}
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%238b5cf6'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 1rem center", backgroundSize: "1rem" }}
      >
        {VOICES.map((v) => (
          <option key={v.value} value={v.value} className="bg-gray-900 text-white">
            {v.label}
          </option>
        ))}
      </select>
    </div>
  );
}

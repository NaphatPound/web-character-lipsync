"use client";

export type GenerateStatus =
  | "idle"
  | "uploading"
  | "tts"
  | "lipsync"
  | "done"
  | "error";

const STATUS_LABELS: Record<GenerateStatus, string> = {
  idle: "Generate Avatar Video",
  uploading: "Uploading image...",
  tts: "Generating speech...",
  lipsync: "Lip-syncing character...",
  done: "Done!",
  error: "Try Again",
};

const STATUS_PROGRESS: Record<GenerateStatus, number> = {
  idle: 0,
  uploading: 15,
  tts: 40,
  lipsync: 75,
  done: 100,
  error: 0,
};

interface GenerateButtonProps {
  status: GenerateStatus;
  onClick: () => void;
  disabled?: boolean;
}

export default function GenerateButton({ status, onClick, disabled }: GenerateButtonProps) {
  const isLoading = ["uploading", "tts", "lipsync"].includes(status);
  const progress = STATUS_PROGRESS[status];

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        className={[
          "relative w-full max-w-sm rounded-2xl px-8 py-4 text-base font-bold transition-all duration-200 overflow-hidden",
          "shadow-[0_0_30px_rgba(124,58,237,0.3)]",
          isLoading || disabled
            ? "opacity-60 cursor-not-allowed bg-violet-800"
            : "bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 hover:shadow-[0_0_40px_rgba(124,58,237,0.5)] active:scale-95",
        ].join(" ")}
      >
        <span className="relative z-10 flex items-center justify-center gap-2">
          {isLoading && (
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          )}
          {!isLoading && status === "idle" && (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
          {STATUS_LABELS[status]}
        </span>
      </button>

      {isLoading && (
        <div className="w-full max-w-sm">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>{STATUS_LABELS[status]}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-400 transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

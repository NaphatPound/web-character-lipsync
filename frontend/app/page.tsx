"use client";

import { useState } from "react";
import GenerateButton, { GenerateStatus } from "@/components/GenerateButton";
import ImageUpload from "@/components/ImageUpload";
import TextInput from "@/components/TextInput";
import VideoPlayer from "@/components/VideoPlayer";
import VoiceSettings from "@/components/VoiceSettings";
import { generateVideo, getVideoUrl } from "@/lib/api";

export default function Home() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [textPrompt, setTextPrompt] = useState("");
  const [voice, setVoice] = useState("th-TH-PremwadeeNeural");
  const [status, setStatus] = useState<GenerateStatus>("idle");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const isProcessing = ["uploading", "tts", "lipsync"].includes(status);

  const handleGenerate = async () => {
    setErrorMessage(null);
    setVideoUrl(null);

    if (!imageFile) {
      setErrorMessage("Please upload a character image first.");
      return;
    }
    if (!textPrompt.trim()) {
      setErrorMessage("Please type some dialogue text.");
      return;
    }

    try {
      setStatus("uploading");
      await new Promise((r) => setTimeout(r, 400)); // brief visual pause

      setStatus("tts");
      // The actual API call starts here — backend runs TTS then lip-sync
      const result = await generateVideo(imageFile, textPrompt, voice);

      setStatus("lipsync");
      await new Promise((r) => setTimeout(r, 500)); // let progress bar show

      setVideoUrl(getVideoUrl(result.video_url));
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "An unexpected error occurred.");
    }
  };

  return (
    <main className="min-h-screen px-4 py-10 md:py-16">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-violet-400 to-purple-300 bg-clip-text text-transparent mb-3">
            AI Talking Avatar
          </h1>
          <p className="text-gray-400 text-base md:text-lg">
            Upload a character image, type your dialogue, and generate a lip-synced video.
          </p>
        </div>

        {/* Input Card */}
        <div className="rounded-3xl border border-violet-800/30 bg-white/[0.03] backdrop-blur-sm p-6 md:p-8 shadow-2xl mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left: Image Upload */}
            <ImageUpload onImageSelect={setImageFile} disabled={isProcessing} />

            {/* Right: Text + Voice */}
            <div className="flex flex-col gap-6">
              <TextInput
                value={textPrompt}
                onChange={setTextPrompt}
                disabled={isProcessing}
              />
              <VoiceSettings
                value={voice}
                onChange={setVoice}
                disabled={isProcessing}
              />
            </div>
          </div>
        </div>

        {/* Error message */}
        {errorMessage && (
          <div
            role="alert"
            className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-300"
          >
            {errorMessage}
          </div>
        )}

        {/* Generate Button */}
        <div className="flex justify-center mb-10">
          <GenerateButton
            status={status}
            onClick={handleGenerate}
            disabled={isProcessing}
          />
        </div>

        {/* Video Output */}
        {videoUrl && (
          <div className="rounded-3xl border border-violet-800/30 bg-white/[0.03] backdrop-blur-sm p-6 md:p-8 shadow-2xl">
            <VideoPlayer src={videoUrl} />
          </div>
        )}
      </div>
    </main>
  );
}

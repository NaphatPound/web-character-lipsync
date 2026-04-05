const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export interface GenerateVideoResult {
  status: string;
  video_url: string;
  job_id: string;
}

export async function generateVideo(
  image: File,
  textPrompt: string,
  voice: string
): Promise<GenerateVideoResult> {
  const formData = new FormData();
  formData.append("image_file", image);
  formData.append("text_prompt", textPrompt);
  formData.append("voice", voice);

  const response = await fetch(`${BACKEND_URL}/generate-video`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail ?? `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export function getVideoUrl(videoPath: string): string {
  if (videoPath.startsWith("http")) return videoPath;
  return `${BACKEND_URL}${videoPath}`;
}

export async function generateDialog(
  topic: string,
  voice: string
): Promise<string> {
  const formData = new FormData();
  formData.append("topic", topic);
  formData.append("voice", voice);

  const response = await fetch(`${BACKEND_URL}/generate-dialog`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.dialog as string;
}

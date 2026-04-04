/**
 * Frontend API helper tests
 * Run: npm test
 */
import { generateVideo, getVideoUrl } from "@/lib/api";

const BACKEND = "http://localhost:8000";

describe("getVideoUrl", () => {
  it("prefixes relative paths with backend URL", () => {
    const result = getVideoUrl("/outputs/abc.mp4");
    expect(result).toBe(`${BACKEND}/outputs/abc.mp4`);
  });

  it("returns absolute URLs unchanged", () => {
    const url = "http://example.com/video.mp4";
    expect(getVideoUrl(url)).toBe(url);
  });
});

describe("generateVideo", () => {
  const mockFile = new File(["data"], "char.jpg", { type: "image/jpeg" });

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("sends FormData to /generate-video and returns result", async () => {
    const mockResult = {
      status: "success",
      video_url: "/outputs/test.mp4",
      job_id: "123",
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResult,
    });

    const result = await generateVideo(mockFile, "Hello world", "en-US-JennyNeural");

    expect(global.fetch).toHaveBeenCalledWith(
      `${BACKEND}/generate-video`,
      expect.objectContaining({ method: "POST" })
    );
    expect(result.status).toBe("success");
    expect(result.video_url).toBe("/outputs/test.mp4");
  });

  it("throws an Error with backend detail on non-ok response", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "File too large. Max 10 MB." }),
    });

    await expect(
      generateVideo(mockFile, "Hello", "th-TH-PremwadeeNeural")
    ).rejects.toThrow("File too large. Max 10 MB.");
  });

  it("throws fallback error message when backend returns no detail", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({}),
    });

    await expect(
      generateVideo(mockFile, "Hello", "th-TH-PremwadeeNeural")
    ).rejects.toThrow("Request failed with status 500");
  });

  it("throws when network fails", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

    await expect(
      generateVideo(mockFile, "Hello", "en-US-GuyNeural")
    ).rejects.toThrow("Network error");
  });
});

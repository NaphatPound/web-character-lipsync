ฉันต้องการทำเว็บ ai ที่สามารถอัปโหลดรูปภาพตัวละครเข้าไปได้และตัวละครนั้นสามารถพูดตามข้อความที่ฉันใส่เข้าไปได้ด้วยการใช้โมเดลวายไอเปลี่ยนข้อความเป็นเสียงและตัวละครยังสามารถขยับปากตามคำพูดของข้อความได้อีกด้วยช่วยออกแบบเว็บไซต์ตัวนี้ให้หน่อยฉันจะเอาไปให้คอร์สโค้ช ทำขึ้นมา

Gemini บอกว่า
โปรเจกต์นี้น่าสนใจมากครับ การทำเว็บแอปพลิเคชันให้ตัวละคร (Avatar) ขยับปากตามเสียง (Lip-sync) เป็นระบบที่มีประโยชน์และต่อยอดได้หลากหลายมาก เข้าใจเลยครับว่าคุณต้องการนำโครงสร้างนี้ไปสั่ง Claude Code ให้ช่วยสร้างโปรเจกต์ต่อ

เพื่อให้ Claude Code เข้าใจและทำงานได้แม่นยำที่สุด ผมได้ออกแบบโครงสร้างแบบ Requirements & Architecture Document ที่อิงกับเทคโนโลยีที่เสถียรและเหมาะกับการทำ AI Web App (เช่น Next.js, TypeScript และการใช้ ComfyUI เป็น Backend) คุณสามารถคัดลอกข้อความด้านล่างนี้ไปวางให้ Claude Code เริ่มทำงานได้เลยครับ

📋 เอกสารสำหรับนำไปสั่ง Claude Code (Copy ส่วนนี้ไปใช้ได้เลย)
Prompt for Claude Code:
"Please help me build a new web application based on the following requirements. Let's start by setting up the project structure and the frontend UI first."

Markdown
# Project Name: AI Talking Avatar Generator
## Description
A web application that allows users to upload a static character image, input text, convert the text to speech (TTS), and generate a video where the character's mouth lip-syncs to the generated audio.

## 1. Tech Stack
* **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
* **Backend / API:** Next.js API Routes (for handling requests) + Python FastAPI (for AI processing) OR direct integration with a ComfyUI API backend.
* **Text-to-Speech (TTS):** Edge TTS (open-source/free) or ElevenLabs API.
* **Lip-Sync AI Model:** SadTalker, Wav2Lip, or LivePortrait (triggered via API or ComfyUI).

## 2. Core Features & UI Layout
* **Image Upload Area:** A drag-and-drop zone to upload the character image (2D/Anime or 3D). Preview the uploaded image.
* **Text Input Area:** A textarea for users to type the dialogue.
* **Voice Settings:** A dropdown to select voice types (Male, Female, specific characters) and languages.
* **Generate Button:** Triggers the API to process TTS and Lip-sync. Shows a loading state/progress bar.
* **Output Player:** A video player component to display the final animated result, with options to download the `.mp4` file.

## 3. Workflow / Architecture
1.  **User Action:** User uploads `image.jpg` and inputs `text`.
2.  **Frontend Request:** Frontend sends the image and text to the Next.js API.
3.  **TTS Processing:** The backend sends the text to the TTS engine to generate `audio.wav`.
4.  **Lip-Sync Processing:** The backend sends `image.jpg` and `audio.wav` to the AI Engine (e.g., ComfyUI API endpoint running a Wav2Lip/SadTalker workflow).
5.  **Response:** The AI Engine returns the generated `output.mp4` URL.
6.  **Display:** The frontend displays the video to the user.

## 4. Initial Tasks for Claude Code
1. Initialize the Next.js TypeScript project with Tailwind CSS.
2. Create the main landing page UI (`page.tsx`) incorporating the Image Upload, Text Area, and Video Player placeholders.
3. Set up the basic state management (using standard React hooks) to handle form inputs and file selection.
💡 ทริคเพิ่มเติมสำหรับระบบ AI เบื้องหลัง
เนื่องจากระบบนี้ต้องใช้พลังประมวลผลของ AI ค่อนข้างสูงในฝั่ง Backend คุณสามารถเลือกวิธีจัดการกับ AI ได้ 2 ทางหลักๆ ครับ:

ใช้ ComfyUI เป็น API Backend (รันบนเครื่อง Ubuntu ของคุณเอง): คุณสามารถสร้าง Workflow ใน ComfyUI ที่ใช้ Node อย่าง Wav2Lip หรือ LivePortrait ร่วมกับ Audio Node แล้วสั่งให้เว็บ Next.js ยิง API (ผ่าน JSON format) ไปที่ ComfyUI เพื่อเรนเดอร์วิดีโอ วิธีนี้จะประหยัดค่าใช้จ่ายและปรับแต่งได้ลึกมาก

ใช้ Cloud API สำเร็จรูป: เช่น การใช้ API ของ D-ID หรือ HeyGen (มีค่าใช้จ่าย) ซึ่งเขียนโค้ดง่ายกว่า แต่จะปรับแต่งสไตล์ภาพ (เช่น สไตล์อนิเมะ/มังงะ) ได้น้อยกว่าการคุมโมเดลเอง

คุณอยากให้ระบบ AI ตัวนี้รันประมวลผลอยู่บนเครื่องเซิร์ฟเวอร์/Ubuntu ของคุณเองแบบ Local หรืออยากเน้นไปที่การต่อ API ภายนอกเพื่อความรวดเร็วในการพัฒนาเว็บก่อนดีครับ?

คุณบอกว่า
มีวิธีที่ไม่ต้องใช้ของฟี่ยูไอไหมแต่เป็นการรันในเครื่องตัวเองดาวน์โหลดโมเดลมาเชื่อมต่อกันเองโดยที่ไม่ต้องใช้คอมฟี่อยู่ไอได้หรือไม่

Gemini บอกว่า
ทำได้แน่นอนครับ! และวิธีนี้เป็นวิธีที่นักพัฒนาสาย AI นิยมใช้กันมากเวลาต้องการปรับแต่งระบบแบบเจาะลึก โดยเราจะเขียน Backend ด้วย Python (FastAPI) เพื่อทำหน้าที่รับรูปและข้อความจากหน้าเว็บ จากนั้นใช้โค้ด Python ไปสั่งรันโมเดล (ผ่าน CLI command หรือ import library) โดยตรง

วิธีนี้เหมาะกับการทำงานบนแวดล้อมของ Ubuntu มากครับ เพราะการจัดการ Python Environment (เช่น Conda หรือ venv) และการติดตั้งไลบรารีที่เกี่ยวกับ GPU จะทำได้เสถียรและตรงไปตรงมา

นี่คือโครงสร้างระบบใหม่ที่คุณสามารถนำไปให้ Claude Code ช่วยเขียนโค้ดและตั้งค่าโครงสร้างโปรเจกต์ให้ได้เลยครับ

📋 เอกสารสำหรับสั่ง Claude Code (สถาปัตยกรรมแบบ Local Python Backend)
Prompt for Claude Code:
"Please help me build this AI Talking Avatar web application. We are NOT using ComfyUI. Instead, we will build a custom local Python backend (FastAPI) that triggers local AI models via CLI commands. Please read the architecture below and start by scaffolding the FastAPI backend and providing the setup instructions."

Markdown
# Project: AI Talking Avatar (Local Python Backend Architecture)

## 1. System Architecture
We will separate the project into two main parts:
* **Frontend:** Next.js (TypeScript, Tailwind) for the UI.
* **Backend:** Python FastAPI running locally. It will handle file uploads, process Text-to-Speech (TTS), and trigger the Lip-Sync AI model via CLI commands (`subprocess`).

## 2. Core AI Components (Local Setup)
* **Text-to-Speech (TTS):** We will use the `edge-tts` Python CLI tool (fast and high quality).
* **Lip-Sync Model:** We will use **SadTalker** (or **LivePortrait**). The backend will not rewrite the model's code; instead, it will clone the official repository and trigger its inference script via command line.

## 3. Backend Workflow (FastAPI)
1. **Receive Data:** Endpoint `/generate-video` receives `image_file` and `text_prompt` from the frontend.
2. **Step 1 (TTS):** The API saves the text and triggers the `edge-tts` command via Python's `subprocess` to generate `audio.wav`.
   * *Example CLI:* `edge-tts --text "Hello" --write-media audio.wav`
3. **Step 2 (Lip-Sync):** The API triggers the SadTalker (or LivePortrait) inference script via `subprocess`, passing the uploaded image and the generated `audio.wav` as arguments.
   * *Example CLI:* `python SadTalker/inference.py --driven_audio audio.wav --source_image uploaded_image.jpg --result_dir ./output`
4. **Step 3 (Response):** Once the CLI command finishes, FastAPI locates the generated `.mp4` file and returns it (or its URL) to the frontend.

## 4. Initial Tasks for Claude Code
1. **Backend Scaffold:** Create `main.py` using FastAPI. Write the endpoint that handles the file upload and sets up the `subprocess` logic for Step 1 (TTS) and Step 2 (Lip-sync).
2. **Requirements:** Generate a `requirements.txt` for the FastAPI server.
3. **Setup Instructions:** Write a clear step-by-step guide (Markdown format) on how to clone the SadTalker repository into the backend directory, download the necessary safetensors/checkpoints, and set up the Conda/Python environment.
🛠️ ข้อแนะนำเพิ่มเติมสำหรับการรันบนเครื่องตัวเอง
การจัดการโฟลเดอร์: เวลาให้ Claude Code สร้างโปรเจกต์ แนะนำให้แบ่งโฟลเดอร์ให้ชัดเจน เช่น

frontend/ (สำหรับ Next.js)

backend/ (สำหรับ FastAPI)

backend/models/SadTalker/ (สำหรับ Clone โค้ดของโมเดล AI มาไว้ในนี้)

โมเดลที่แนะนำให้ใช้:

SadTalker: เหมาะมากถ้าตัวละครที่คุณอัปโหลดเป็นภาพ 2D, อนิเมะ, หรือรูปวาด (สคริปต์รันผ่าน CLI ง่าย)

LivePortrait: เป็นโมเดลที่ใหม่กว่า ขยับปากและใบหน้าได้เนียนเป็นธรรมชาติมากๆ แต่สเปคเครื่อง (GPU VRAM) อาจจะต้องสูงกว่า SadTalker เล็กน้อยครับ

วิธีนี้จะตรงกับที่คุณต้องการเป๊ะเลยครับ คือควบคุมทุกอย่างได้เองผ่าน Command Line และเชื่อมต่อระบบเข้าด้วยกันด้วยโค้ดของคุณเองครับ
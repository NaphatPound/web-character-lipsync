/**
 * VoiceSettings component tests
 */
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import VoiceSettings, { VOICES } from "@/components/VoiceSettings";

describe("VoiceSettings", () => {
  it("renders a select with all voice options", () => {
    render(<VoiceSettings value={VOICES[0].value} onChange={() => {}} />);
    const select = screen.getByRole("combobox");
    expect(select).toBeInTheDocument();
    expect(screen.getAllByRole("option")).toHaveLength(VOICES.length);
  });

  it("shows the correct selected voice", () => {
    render(<VoiceSettings value="en-US-JennyNeural" onChange={() => {}} />);
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select.value).toBe("en-US-JennyNeural");
  });

  it("calls onChange when a new voice is selected", () => {
    const onChange = jest.fn();
    render(<VoiceSettings value={VOICES[0].value} onChange={onChange} />);
    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "th-TH-NiwatNeural" },
    });
    expect(onChange).toHaveBeenCalledWith("th-TH-NiwatNeural");
  });

  it("disables the select when disabled prop is true", () => {
    render(<VoiceSettings value={VOICES[0].value} onChange={() => {}} disabled />);
    expect(screen.getByRole("combobox")).toBeDisabled();
  });
});

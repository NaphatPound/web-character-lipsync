/**
 * TextInput component tests
 */
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import TextInput from "@/components/TextInput";

describe("TextInput", () => {
  it("renders the textarea", () => {
    render(<TextInput value="" onChange={() => {}} />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("shows remaining character count", () => {
    render(<TextInput value="Hello" onChange={() => {}} />);
    expect(screen.getByText("495 / 500")).toBeInTheDocument();
  });

  it("calls onChange with new value", () => {
    const onChange = jest.fn();
    render(<TextInput value="" onChange={onChange} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Hi" } });
    expect(onChange).toHaveBeenCalledWith("Hi");
  });

  it("truncates input to 500 characters", () => {
    const onChange = jest.fn();
    render(<TextInput value="" onChange={onChange} />);
    const longText = "a".repeat(510);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: longText } });
    expect(onChange).toHaveBeenCalledWith("a".repeat(500));
  });

  it("disables textarea when disabled prop is true", () => {
    render(<TextInput value="" onChange={() => {}} disabled />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });
});

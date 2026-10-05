import { render, screen } from "@testing-library/react";

import { Button } from "./button";

describe("Button", () => {
  it("renders an accessible button and forwards disabled state", () => {
    render(<Button disabled>Simülasyonu başlat</Button>);
    expect(screen.getByRole("button", { name: "Simülasyonu başlat" })).toBeDisabled();
  });
});

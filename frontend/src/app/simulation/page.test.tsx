import { render, screen } from "@testing-library/react";

import SimulationPage from "./page";

describe("SimulationPage", () => {
  it("renders the simulation workspace", () => {
    render(<SimulationPage />);

    expect(screen.getByRole("heading", { name: /Sürü ağını gözlemle/i })).toBeInTheDocument();
  });
});

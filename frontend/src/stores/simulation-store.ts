import { create } from "zustand";

import type {
  SessionStatus,
  SimulationCreateResponse,
  SimulationFrame,
  StreamMessage,
} from "@/lib/api/schemas";
import type { ConnectionState } from "@/lib/api/stream";

type SimulationState = {
  session: SimulationCreateResponse | null;
  status: SessionStatus | "idle";
  connection: ConnectionState;
  frames: SimulationFrame[];
  latestFrame: SimulationFrame | null;
  error: string | null;
  setSession: (session: SimulationCreateResponse) => void;
  setStatus: (status: SessionStatus) => void;
  setConnection: (connection: ConnectionState) => void;
  receiveMessage: (message: StreamMessage) => void;
  setError: (error: string) => void;
  reset: () => void;
};

const initialState = {
  session: null,
  status: "idle" as const,
  connection: "disconnected" as const,
  frames: [] as SimulationFrame[],
  latestFrame: null,
  error: null,
};

export const useSimulationStore = create<SimulationState>((set) => ({
  ...initialState,
  setSession: (session) => set({ session, status: session.status, frames: [], latestFrame: null, error: null }),
  setStatus: (status) => set({ status }),
  setConnection: (connection) => set({ connection }),
  receiveMessage: (message) => {
    if (message.type === "frame") {
      set((state) => ({
        frames: [...state.frames.filter((frame) => frame.step !== message.frame.step), message.frame].sort(
          (left, right) => left.step - right.step,
        ),
        latestFrame: message.frame,
        status: state.status === "created" ? "running" : state.status,
      }));
      return;
    }
    set({ status: message.status, error: message.error });
  },
  setError: (error) => set({ error, connection: "failed" }),
  reset: () => set(initialState),
}));

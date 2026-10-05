"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { apiClient } from "@/lib/api/client";
import type { SimulationCreateRequest } from "@/lib/api/schemas";
import { SimulationStreamClient } from "@/lib/api/stream";
import { useSimulationStore } from "@/stores/simulation-store";

export function useSimulationController() {
  const streamRef = useRef<SimulationStreamClient | null>(null);
  const [busy, setBusy] = useState(false);
  const session = useSimulationStore((state) => state.session);
  const status = useSimulationStore((state) => state.status);
  const connection = useSimulationStore((state) => state.connection);
  const setSession = useSimulationStore((state) => state.setSession);
  const setStatus = useSimulationStore((state) => state.setStatus);
  const setConnection = useSimulationStore((state) => state.setConnection);
  const receiveMessage = useSimulationStore((state) => state.receiveMessage);
  const setError = useSimulationStore((state) => state.setError);
  const resetStore = useSimulationStore((state) => state.reset);

  const disconnect = useCallback(() => {
    streamRef.current?.disconnect();
    streamRef.current = null;
  }, []);

  useEffect(() => disconnect, [disconnect]);

  const start = useCallback(
    async (config: SimulationCreateRequest) => {
      setBusy(true);
      disconnect();
      resetStore();
      try {
        const created = await apiClient.createSimulation(config);
        setSession(created);
        const stream = new SimulationStreamClient(created.id);
        stream.onMessage(receiveMessage);
        stream.onStateChange(setConnection);
        streamRef.current = stream;
        stream.connect();
      } catch (error) {
        setError(error instanceof Error ? error.message : "Simülasyon başlatılamadı");
      } finally {
        setBusy(false);
      }
    },
    [disconnect, receiveMessage, resetStore, setConnection, setError, setSession],
  );

  const control = useCallback(
    async (action: "pause" | "resume" | "stop") => {
      if (!session) return;
      setBusy(true);
      try {
        const response =
          action === "pause"
            ? await apiClient.pauseSimulation(session.id)
            : action === "resume"
              ? await apiClient.resumeSimulation(session.id)
              : await apiClient.stopSimulation(session.id);
        setStatus(response.status);
      } catch (error) {
        setError(error instanceof Error ? error.message : "Simülasyon kontrol edilemedi");
      } finally {
        setBusy(false);
      }
    },
    [session, setError, setStatus],
  );

  const reset = useCallback(() => {
    disconnect();
    resetStore();
  }, [disconnect, resetStore]);

  return {
    busy,
    connection,
    session,
    status,
    start,
    pause: () => control("pause"),
    resume: () => control("resume"),
    stop: () => control("stop"),
    reset,
  };
}

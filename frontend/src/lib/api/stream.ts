import { WS_BASE_URL } from "./config";
import { streamMessageSchema, type StreamMessage } from "./schemas";

export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "completed"
  | "failed";

type StreamOptions = {
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
};

export function parseStreamMessage(raw: string): StreamMessage {
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    throw new Error("WebSocket mesajı geçerli JSON değil");
  }
  const parsed = streamMessageSchema.safeParse(value);
  if (!parsed.success) {
    throw new Error("WebSocket mesajı beklenen sözleşmeyle eşleşmiyor");
  }
  return parsed.data;
}

export class SimulationStreamClient {
  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private manuallyClosed = false;
  private terminal = false;
  private readonly messageListeners = new Set<(message: StreamMessage) => void>();
  private readonly stateListeners = new Set<(state: ConnectionState) => void>();

  constructor(
    private readonly simulationId: string,
    private readonly options: StreamOptions = {},
  ) {}

  connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN || this.socket?.readyState === WebSocket.CONNECTING) return;
    this.manuallyClosed = false;
    this.emitState(this.reconnectAttempts ? "reconnecting" : "connecting");
    this.socket = new WebSocket(`${WS_BASE_URL}/api/v1/simulations/${this.simulationId}/stream`);
    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.emitState("connected");
    };
    this.socket.onmessage = (event) => {
      try {
        const message = parseStreamMessage(String(event.data));
        this.messageListeners.forEach((listener) => listener(message));
        if (message.type === "status") {
          this.terminal = true;
          this.emitState(message.status === "failed" ? "failed" : "completed");
        }
      } catch {
        this.emitState("failed");
      }
    };
    this.socket.onerror = () => this.emitState("failed");
    this.socket.onclose = () => {
      this.socket = null;
      if (!this.manuallyClosed && !this.terminal) this.scheduleReconnect();
    };
  }

  disconnect(): void {
    this.manuallyClosed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.socket?.close(1000, "Client disconnected");
    this.socket = null;
    if (!this.terminal) this.emitState("disconnected");
  }

  onMessage(listener: (message: StreamMessage) => void): () => void {
    this.messageListeners.add(listener);
    return () => this.messageListeners.delete(listener);
  }

  onStateChange(listener: (state: ConnectionState) => void): () => void {
    this.stateListeners.add(listener);
    return () => this.stateListeners.delete(listener);
  }

  private emitState(state: ConnectionState): void {
    this.stateListeners.forEach((listener) => listener(state));
  }

  private scheduleReconnect(): void {
    const maxAttempts = this.options.maxReconnectAttempts ?? 5;
    if (this.reconnectAttempts >= maxAttempts) {
      this.emitState("failed");
      return;
    }
    this.reconnectAttempts += 1;
    this.emitState("reconnecting");
    const baseDelay = this.options.reconnectDelayMs ?? 500;
    const delay = Math.min(baseDelay * 2 ** (this.reconnectAttempts - 1), 8_000);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}

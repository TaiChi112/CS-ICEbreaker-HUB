export type EventEnvelope<TPayload = Record<string, unknown>> = {
  eventType: string;
  payload: TPayload;
  occurredAt?: string;
};

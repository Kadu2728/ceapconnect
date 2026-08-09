export interface PushPublicKey {
  public_key: string;
  configured: boolean;
}

export interface PushSubscribeInput {
  endpoint: string;
  p256dh: string;
  auth: string;
}

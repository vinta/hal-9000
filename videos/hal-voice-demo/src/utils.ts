export function typewriterText(
  fullText: string,
  frame: number,
  startFrame: number,
  charsPerFrame = 0.7,
): string {
  if (frame < startFrame) return "";
  const elapsed = frame - startFrame;
  const chars = Math.min(fullText.length, Math.floor(elapsed * charsPerFrame));
  return fullText.substring(0, chars);
}

export function isTypewriterDone(
  fullText: string,
  frame: number,
  startFrame: number,
  charsPerFrame = 0.7,
): boolean {
  if (frame < startFrame) return false;
  const elapsed = frame - startFrame;
  return Math.floor(elapsed * charsPerFrame) >= fullText.length;
}

export function cursorOpacity(frame: number): number {
  return Math.sin(frame * 0.2) > 0 ? 1 : 0;
}

import { Composition } from "remotion";
import { HAL9000Video } from "./HAL9000Video";

// Video timing (in seconds):
// Intro: 4s
// Bootstrap: 5s
// Commands: 5s
// Tech Stack: 4s
// Outro: 7s
// Transitions: 4 x 0.5s = 2s overlap
// Total: 25 - 2 = 23s

const FPS = 30;
const DURATION_SECONDS = 23;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="HAL9000Video"
      component={HAL9000Video}
      durationInFrames={DURATION_SECONDS * FPS}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};

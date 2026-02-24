import React from "react";
import { Composition } from "remotion";
import { HalVoiceVideo } from "./HalVoiceVideo";

// Scene durations (seconds):
//   SessionStart:         7.0
//   UserPromptSubmit:     4.0
//   AskUserQuestion:      5.5
//   PermissionRequest:    5.5
//   SubagentStart:        5.5
//   PostToolUseFailure:   4.0
//   PreCompact:           7.0
//   Stop:                 6.5
//   SessionEnd:           7.0
//                        -----
//   Raw total:           52.0s
//   Transitions:          8 x 10 frames = 80 frames (2.67s overlap)
//   Net duration:        ~49.3s = 1480 frames

const FPS = 30;
const DURATION_FRAMES = 1480;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="HalVoiceDemo"
      component={HalVoiceVideo}
      durationInFrames={DURATION_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};

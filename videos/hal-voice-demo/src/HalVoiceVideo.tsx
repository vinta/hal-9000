import React from "react";
import { useVideoConfig } from "remotion";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { TRANSITION_FRAMES } from "./styles";
import { SessionStartScene } from "./scenes/SessionStartScene";
import { UserPromptSubmitScene } from "./scenes/UserPromptSubmitScene";
import { AskUserQuestionScene } from "./scenes/AskUserQuestionScene";
import { PermissionRequestScene } from "./scenes/PermissionRequestScene";
import { SubagentStartScene } from "./scenes/SubagentStartScene";
import { PostToolUseFailureScene } from "./scenes/PostToolUseFailureScene";
import { PreCompactScene } from "./scenes/PreCompactScene";
import { StopScene } from "./scenes/StopScene";
import { SessionEndScene } from "./scenes/SessionEndScene";

const SCENES: { component: React.FC; durationSec: number }[] = [
  { component: SessionStartScene, durationSec: 7 },
  { component: UserPromptSubmitScene, durationSec: 4 },
  { component: AskUserQuestionScene, durationSec: 5.5 },
  { component: PermissionRequestScene, durationSec: 5.5 },
  { component: SubagentStartScene, durationSec: 5.5 },
  { component: PostToolUseFailureScene, durationSec: 4 },
  { component: PreCompactScene, durationSec: 7 },
  { component: StopScene, durationSec: 6.5 },
  { component: SessionEndScene, durationSec: 7 },
];

export const HalVoiceVideo: React.FC = () => {
  const { fps } = useVideoConfig();

  return (
    <TransitionSeries>
      {SCENES.map((scene, i) => {
        const Scene = scene.component;
        return (
          <React.Fragment key={i}>
            <TransitionSeries.Sequence
              durationInFrames={Math.round(scene.durationSec * fps)}
            >
              <Scene />
            </TransitionSeries.Sequence>
            {i < SCENES.length - 1 && (
              <TransitionSeries.Transition
                presentation={fade()}
                timing={linearTiming({
                  durationInFrames: TRANSITION_FRAMES,
                })}
              />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};

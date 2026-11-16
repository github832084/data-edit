import React from 'react';
import { Composition } from 'remotion';
import { MapVideo } from './Map';
import route from './route.json';

const FPS = 30;
export const Root: React.FC = () => (
  <>
    <Composition id="Map" component={MapVideo} durationInFrames={route.seconds * FPS} fps={FPS} width={1920} height={1080} />
    <Composition id="MapVertical" component={MapVideo} durationInFrames={route.seconds * FPS} fps={FPS} width={1080} height={1920} />
  </>
);

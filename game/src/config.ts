// Every tunable number in one place.

/** Internal resolution (9:16 portrait). The canvas is scaled to fit the screen. */
export const GAME_WIDTH = 1080;
export const GAME_HEIGHT = 1920;

/** The battle map: 4096x4096 world pixels, loaded as a grid of JPEG tiles. */
export const MAP_SIZE = 4096;
export const MAP_TILE_SIZE = 2048;
export const MAP_TILES_PER_SIDE = MAP_SIZE / MAP_TILE_SIZE;

/** Where the camera starts: the castle courtyard. */
export const START_VIEW = { x: 2090, y: 1990 };

export const ZOOM = {
  /** 1.5 shows about 720x1280 world pixels. */
  start: 1.5,
  max: 2.2,
  /** Wheel zoom multiplier per notch. */
  wheelStep: 1.12,
};

export const DRAG = {
  /** Movement (screen px) below which a press counts as a tap, not a drag. */
  tapSlop: 14,
  /** Fling: velocity kept per 16 ms frame after the finger lifts. */
  friction: 0.9,
  /** Fling stops below this speed (world px per ms). */
  minSpeed: 0.02,
};

/** One scale for every brawler sheet: their bodies are 186-223 px tall, so about 74-89 world px on the map. */
export const BRAWLER_SCALE = 0.4;

/** Attack row timing, the same as the shoot / attack GIFs (tools/build_armed.py). */
export const ANIM = {
  attackFramesMs: [220, 80, 120, 260],
};

export const IDLE_BOB = {
  /** How much the body squashes while standing (fraction of its height). */
  squash: 0.03,
  minMs: 650,
  maxMs: 900,
};

export const SHADOW = {
  color: 0x000000,
  alpha: 0.22,
  /** Shadow width relative to the feet width, and height relative to its width. */
  widthScale: 1.25,
  heightRatio: 0.28,
};

export const BACKGROUND_COLOR = '#12161f';

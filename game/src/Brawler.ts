import Phaser from 'phaser';
import { ARMED_SHEET, type BrawlerSpawn } from './brawlers';
import { ANIM, IDLE_BOB, SHADOW } from './config';

export function armedSheetKey(name: string): string {
  return `${name}_armed`;
}

/** Where the body sits inside one sheet cell, measured from the first walk frame. */
interface FrameMetrics {
  cellW: number;
  cellH: number;
  left: number;
  right: number;
  top: number;
  bottom: number;
  /** Center and width of the opaque pixels in the lowest band of the body (the feet). */
  feetX: number;
  feetWidth: number;
}

/** One armed brawler standing on the map: idle bob, shoots or swings when tapped. */
export class Brawler {
  readonly sprite: Phaser.GameObjects.Sprite;
  readonly shadow: Phaser.GameObjects.Ellipse;
  /** World-space box around the visible body, for taps. */
  readonly hitArea: Phaser.Geom.Rectangle;

  private readonly shootKey: string;

  constructor(scene: Phaser.Scene, readonly spawn: BrawlerSpawn) {
    const key = armedSheetKey(spawn.name);
    const m = sliceSheet(scene, key);
    const scale = spawn.height / (m.bottom - m.top + 1);
    const dir = spawn.faceLeft ? -1 : 1;

    // Origin on the feet, so x/y is where the brawler stands. A negative scaleX
    // mirrors around that origin, so the feet stay put when facing left.
    this.sprite = scene.add
      .sprite(spawn.x, spawn.y, key, 0)
      .setOrigin(m.feetX / m.cellW, (m.bottom + 1) / m.cellH)
      .setScale(scale * dir, scale)
      .setDepth(spawn.y);

    const shadowW = Math.max(m.feetWidth * SHADOW.widthScale, (m.right - m.left) * 0.5) * scale;
    const shadowH = shadowW * SHADOW.heightRatio;
    this.shadow = scene.add
      .ellipse(spawn.x, spawn.y - shadowH * 0.15, shadowW, shadowH, SHADOW.color, SHADOW.alpha)
      .setDepth(spawn.y - 0.5);

    const x1 = spawn.x + (m.left - m.feetX) * scale * dir;
    const x2 = spawn.x + (m.right + 1 - m.feetX) * scale * dir;
    const height = (m.bottom + 1 - m.top) * scale;
    this.hitArea = new Phaser.Geom.Rectangle(Math.min(x1, x2), spawn.y - height, Math.abs(x2 - x1), height);

    this.shootKey = `${spawn.name}_shoot`;
    if (!scene.anims.exists(this.shootKey)) {
      const first = ARMED_SHEET.cols; // row 2 starts after the 4 walk frames
      scene.anims.create({
        key: this.shootKey,
        frames: [0, 1, 2, 3].map((i) => ({
          key,
          frame: first + i,
          duration: i === 3 ? ANIM.attackLastFrameHoldMs : ANIM.attackFrameMs,
        })),
        repeat: 0,
      });
    }

    this.startIdleBob(scale * dir, scale);
  }

  /** Play the shoot (or melee swing) row once, then stand again. */
  attack(): void {
    if (this.sprite.anims.isPlaying) return;
    this.sprite.play(this.shootKey);
    this.sprite.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => this.sprite.setFrame(0));
  }

  private startIdleBob(scaleX: number, scaleY: number): void {
    this.sprite.scene.tweens.add({
      targets: this.sprite,
      scaleY: scaleY * (1 - IDLE_BOB.squash),
      scaleX: scaleX * (1 + IDLE_BOB.squash / 2),
      duration: Phaser.Math.Between(IDLE_BOB.minMs, IDLE_BOB.maxMs),
      delay: Phaser.Math.Between(0, IDLE_BOB.maxMs),
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    });
  }
}

/**
 * The armed sheets are loaded as plain images because every brawler's cell size
 * differs. Split the texture into its 4x2 frames and measure the body in frame 0.
 */
function sliceSheet(scene: Phaser.Scene, key: string): FrameMetrics {
  const texture = scene.textures.get(key);
  const source = texture.getSourceImage() as HTMLImageElement;
  const cellW = Math.floor(source.width / ARMED_SHEET.cols);
  const cellH = Math.floor(source.height / ARMED_SHEET.rows);

  if (!texture.has('0')) {
    for (let i = 0; i < ARMED_SHEET.cols * ARMED_SHEET.rows; i++) {
      const col = i % ARMED_SHEET.cols;
      const row = Math.floor(i / ARMED_SHEET.cols);
      texture.add(i, 0, col * cellW, row * cellH, cellW, cellH);
    }
  }
  return measureFrame(source, cellW, cellH);
}

function measureFrame(source: HTMLImageElement, cellW: number, cellH: number): FrameMetrics {
  const fallback: FrameMetrics = {
    cellW,
    cellH,
    left: 0,
    right: cellW - 1,
    top: 0,
    bottom: cellH - 1,
    feetX: cellW / 2,
    feetWidth: cellW / 2,
  };

  let data: Uint8ClampedArray;
  try {
    const canvas = document.createElement('canvas');
    canvas.width = cellW;
    canvas.height = cellH;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return fallback;
    ctx.drawImage(source, 0, 0, cellW, cellH, 0, 0, cellW, cellH);
    data = ctx.getImageData(0, 0, cellW, cellH).data;
  } catch {
    return fallback;
  }

  const opaque = (x: number, y: number) => data[(y * cellW + x) * 4 + 3] > 40;
  let left = cellW;
  let right = -1;
  let top = cellH;
  let bottom = -1;
  for (let y = 0; y < cellH; y++) {
    for (let x = 0; x < cellW; x++) {
      if (!opaque(x, y)) continue;
      if (x < left) left = x;
      if (x > right) right = x;
      if (y < top) top = y;
      if (y > bottom) bottom = y;
    }
  }
  if (right < 0) return fallback;

  // Feet: the opaque pixels in the bottom 10% of the body.
  const bandTop = Math.round(bottom - (bottom - top) * 0.1);
  let sumX = 0;
  let count = 0;
  let feetLeft = right;
  let feetRight = left;
  for (let y = bandTop; y <= bottom; y++) {
    for (let x = left; x <= right; x++) {
      if (!opaque(x, y)) continue;
      sumX += x;
      count++;
      if (x < feetLeft) feetLeft = x;
      if (x > feetRight) feetRight = x;
    }
  }
  const feetX = count > 0 ? sumX / count : (left + right) / 2;
  const feetWidth = count > 0 ? feetRight - feetLeft + 1 : right - left + 1;

  return { cellW, cellH, left, right, top, bottom, feetX, feetWidth };
}

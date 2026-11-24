import Phaser from 'phaser';
import { DRAG, MAP_SIZE, ZOOM } from './config';

/**
 * Drag to scroll (with a fling), pinch or mouse wheel to zoom, tap to pick.
 * The camera never shows anything outside the map.
 */
export class CameraControl {
  /** Called with world coordinates when a press ends without dragging. */
  onTap?: (worldX: number, worldY: number) => void;

  private readonly cam: Phaser.Cameras.Scene2D.Camera;

  private dragPointerId = -1;
  private downX = 0;
  private downY = 0;
  private lastX = 0;
  private lastY = 0;
  private lastTime = 0;
  private moved = false;
  private velX = 0;
  private velY = 0;

  private pinching = false;
  private pinchStartDist = 0;
  private pinchStartZoom = 1;
  private pinchLastMidX = 0;
  private pinchLastMidY = 0;

  constructor(private readonly scene: Phaser.Scene) {
    this.cam = scene.cameras.main;

    // The canvas can change size (rotation, browser bars): keep the view legal.
    scene.scale.on(Phaser.Scale.Events.RESIZE, () => {
      this.cam.setZoom(Phaser.Math.Clamp(this.cam.zoom, this.minZoom(), ZOOM.max));
      this.clampScroll();
    });

    const input = scene.input;
    input.on(Phaser.Input.Events.POINTER_DOWN, this.handleDown, this);
    input.on(Phaser.Input.Events.POINTER_MOVE, this.handleMove, this);
    input.on(Phaser.Input.Events.POINTER_UP, this.handleUp, this);
    input.on(Phaser.Input.Events.POINTER_UP_OUTSIDE, this.handleUp, this);
    input.on(
      Phaser.Input.Events.POINTER_WHEEL,
      (pointer: Phaser.Input.Pointer, _over: unknown, _dx: number, dy: number) => {
        const factor = dy > 0 ? 1 / ZOOM.wheelStep : ZOOM.wheelStep;
        this.zoomAt(pointer.x, pointer.y, this.cam.zoom * factor);
      },
    );
  }

  /** Put the given world point in the middle of the screen. */
  centerOn(worldX: number, worldY: number, zoom: number): void {
    this.cam.setZoom(Phaser.Math.Clamp(zoom, this.minZoom(), ZOOM.max));
    this.cam.centerOn(worldX, worldY);
    this.clampScroll();
  }

  update(deltaMs: number): void {
    if (this.dragPointerId !== -1 || this.pinching) return;
    if (Math.abs(this.velX) < DRAG.minSpeed && Math.abs(this.velY) < DRAG.minSpeed) return;

    const beforeX = this.cam.scrollX;
    const beforeY = this.cam.scrollY;
    this.cam.scrollX += this.velX * deltaMs;
    this.cam.scrollY += this.velY * deltaMs;
    this.clampScroll();
    // Stop the fling on the axis that hit the map edge.
    if (this.cam.scrollX === beforeX) this.velX = 0;
    if (this.cam.scrollY === beforeY) this.velY = 0;

    const keep = Math.pow(DRAG.friction, deltaMs / 16);
    this.velX *= keep;
    this.velY *= keep;
  }

  private handleDown(pointer: Phaser.Input.Pointer): void {
    this.velX = 0;
    this.velY = 0;
    const [a, b] = this.touchesDown();
    if (a && b) {
      this.startPinch(a, b);
      return;
    }
    this.dragPointerId = pointer.id;
    this.downX = this.lastX = pointer.x;
    this.downY = this.lastY = pointer.y;
    this.lastTime = pointer.time;
    this.moved = false;
  }

  private handleMove(pointer: Phaser.Input.Pointer): void {
    if (this.pinching) {
      this.updatePinch();
      return;
    }
    if (pointer.id !== this.dragPointerId || !pointer.isDown) return;

    if (!this.moved) {
      const dist = Phaser.Math.Distance.Between(this.downX, this.downY, pointer.x, pointer.y);
      if (dist < DRAG.tapSlop) return;
      this.moved = true;
    }

    const dx = pointer.x - this.lastX;
    const dy = pointer.y - this.lastY;
    const dt = Math.max(1, pointer.time - this.lastTime);
    this.cam.scrollX -= dx / this.cam.zoom;
    this.cam.scrollY -= dy / this.cam.zoom;
    this.clampScroll();

    // Smoothed velocity in world px per ms, used for the fling.
    const vx = -dx / this.cam.zoom / dt;
    const vy = -dy / this.cam.zoom / dt;
    this.velX = this.velX * 0.6 + vx * 0.4;
    this.velY = this.velY * 0.6 + vy * 0.4;

    this.lastX = pointer.x;
    this.lastY = pointer.y;
    this.lastTime = pointer.time;
  }

  private handleUp(pointer: Phaser.Input.Pointer): void {
    if (this.pinching) {
      // Lifting one finger ends the pinch; the next press starts a fresh drag.
      this.pinching = false;
      this.dragPointerId = -1;
      return;
    }
    if (pointer.id !== this.dragPointerId) return;
    this.dragPointerId = -1;

    if (!this.moved) {
      this.velX = 0;
      this.velY = 0;
      const world = this.screenToWorld(pointer.x, pointer.y);
      this.onTap?.(world.x, world.y);
      return;
    }
    // A finger resting before lift means no fling.
    if (pointer.time - this.lastTime > 80) {
      this.velX = 0;
      this.velY = 0;
    }
  }

  private touchesDown(): Phaser.Input.Pointer[] {
    return this.scene.input.manager.pointers.filter((p) => p.isDown && p.id !== 0);
  }

  private startPinch(a: Phaser.Input.Pointer, b: Phaser.Input.Pointer): void {
    this.pinching = true;
    this.dragPointerId = -1;
    this.pinchStartDist = Math.max(1, Phaser.Math.Distance.Between(a.x, a.y, b.x, b.y));
    this.pinchStartZoom = this.cam.zoom;
    this.pinchLastMidX = (a.x + b.x) / 2;
    this.pinchLastMidY = (a.y + b.y) / 2;
  }

  private updatePinch(): void {
    const [a, b] = this.touchesDown();
    if (!a || !b) return;
    const midX = (a.x + b.x) / 2;
    const midY = (a.y + b.y) / 2;
    const dist = Math.max(1, Phaser.Math.Distance.Between(a.x, a.y, b.x, b.y));

    // Pan with the midpoint, then zoom around it.
    this.cam.scrollX -= (midX - this.pinchLastMidX) / this.cam.zoom;
    this.cam.scrollY -= (midY - this.pinchLastMidY) / this.cam.zoom;
    this.zoomAt(midX, midY, (this.pinchStartZoom * dist) / this.pinchStartDist);

    this.pinchLastMidX = midX;
    this.pinchLastMidY = midY;
  }

  /** Zoom while keeping the world point under the given screen point still. */
  private zoomAt(screenX: number, screenY: number, zoom: number): void {
    const newZoom = Phaser.Math.Clamp(zoom, this.minZoom(), ZOOM.max);
    const world = this.screenToWorld(screenX, screenY);
    this.cam.setZoom(newZoom);
    const halfW = this.cam.width / 2;
    const halfH = this.cam.height / 2;
    this.cam.scrollX = world.x - halfW - (screenX - halfW) / newZoom;
    this.cam.scrollY = world.y - halfH - (screenY - halfH) / newZoom;
    this.clampScroll();
  }

  /** The furthest zoom-out that still fills the screen with map. */
  private minZoom(): number {
    return Math.max(this.cam.width / MAP_SIZE, this.cam.height / MAP_SIZE);
  }

  /** Phaser zooms around the camera's center: world = scroll + half + (screen - half) / zoom. */
  private screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    const halfW = this.cam.width / 2;
    const halfH = this.cam.height / 2;
    return {
      x: this.cam.scrollX + halfW + (screenX - halfW) / this.cam.zoom,
      y: this.cam.scrollY + halfH + (screenY - halfH) / this.cam.zoom,
    };
  }

  private clampScroll(): void {
    const halfW = this.cam.width / 2;
    const halfH = this.cam.height / 2;
    const viewHalfW = halfW / this.cam.zoom;
    const viewHalfH = halfH / this.cam.zoom;
    this.cam.scrollX = Phaser.Math.Clamp(this.cam.scrollX, viewHalfW - halfW, MAP_SIZE - halfW - viewHalfW);
    this.cam.scrollY = Phaser.Math.Clamp(this.cam.scrollY, viewHalfH - halfH, MAP_SIZE - halfH - viewHalfH);
  }
}
